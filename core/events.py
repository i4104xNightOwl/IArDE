import xcffib.xproto as xproto
from typing import Dict, Callable, List, Optional
from .window import Window
from .conn import XConnection

class EventHandler:
    """Xử lý các sự kiện từ X server"""
    
    def __init__(self, xconn: XConnection):
        self.xconn = xconn
        self.event_handlers: Dict[int, Callable] = {}
        self.windows: Dict[int, Window] = {}
        self.focused_window: Optional[Window] = None
        
        # Đăng ký các event handler mặc định
        self._register_default_handlers()
        
    def _register_default_handlers(self):
        """Đăng ký các event handler mặc định"""
        self.event_handlers.update({
            xproto.KeyPressEvent: self._handle_keypress,
            xproto.ButtonPressEvent: self._handle_buttonpress,
            xproto.ButtonReleaseEvent: self._handle_buttonrelease,
            xproto.MotionNotifyEvent: self._handle_motionnotify,
            xproto.EnterNotifyEvent: self._handle_enternotify,
            xproto.LeaveNotifyEvent: self._handle_leavenotify,
            xproto.CreateNotifyEvent: self._handle_createnotify,
            xproto.DestroyNotifyEvent: self._handle_destroynotify,
            xproto.MapRequestEvent: self._handle_maprequest,
            xproto.UnmapNotifyEvent: self._handle_unmapnotify,
            xproto.ConfigureRequestEvent: self._handle_configurerequest,
            xproto.ConfigureNotifyEvent: self._handle_configurenotify,
            xproto.FocusInEvent: self._handle_focusin,
            xproto.FocusOutEvent: self._handle_focusout,
            xproto.PropertyNotifyEvent: self._handle_propertynotify,
            xproto.ClientMessageEvent: self._handle_clientmessage,
        })
        
    def handle_event(self, event) -> bool:
        """Xử lý một event"""
        event_type = type(event)
        
        if event_type in self.event_handlers:
            try:
                return self.event_handlers[event_type](event)
            except Exception as e:
                print(f"Error handling event {event_type.__name__}: {e}")
                
        return False
        
    def register_window(self, window: Window):
        """Đăng ký một cửa sổ để theo dõi"""
        self.windows[window.window_id] = window
        
    def unregister_window(self, window_id: int):
        """Hủy đăng ký một cửa sổ"""
        if window_id in self.windows:
            del self.windows[window_id]
            if self.focused_window and self.focused_window.window_id == window_id:
                self.focused_window = None
                
    def get_window(self, window_id: int) -> Optional[Window]:
        """Lấy window theo ID"""
        return self.windows.get(window_id)
        
    def set_focused_window(self, window: Optional[Window]):
        """Đặt cửa sổ được focus"""
        if self.focused_window:
            self.focused_window.is_focused = False
            # Cập nhật border color
            self.focused_window.set_border_color(0xff333333)
            
        self.focused_window = window
        if window:
            window.is_focused = True
            window.focus()
            # Cập nhật border color
            window.set_border_color(0xff005577)
            
    def get_focused_window(self) -> Optional[Window]:
        """Lấy cửa sổ đang được focus"""
        return self.focused_window
        
    # Event handlers
    def _handle_keypress(self, event: xproto.KeyPressEvent) -> bool:
        """Xử lý keypress event"""
        # Keypress được xử lý bởi KeybindManager
        return False
        
    def _handle_buttonpress(self, event: xproto.ButtonPressEvent) -> bool:
        """Xử lý mouse button press"""
        window = self.get_window(event.child)
        if window:
            self.set_focused_window(window)
        return True
        
    def _handle_buttonrelease(self, event: xproto.ButtonReleaseEvent) -> bool:
        """Xử lý mouse button release"""
        return True
        
    def _handle_motionnotify(self, event: xproto.MotionNotifyEvent) -> bool:
        """Xử lý mouse motion"""
        # TODO: Implement window dragging
        return True
        
    def _handle_enternotify(self, event: xproto.EnterNotifyEvent) -> bool:
        """Xử lý mouse enter window"""
        window = self.get_window(event.window)
        from config import config
        if window and config.is_auto_focus_enabled():
            self.set_focused_window(window)
        return True
        
    def _handle_leavenotify(self, event: xproto.LeaveNotifyEvent) -> bool:
        """Xử lý mouse leave window"""
        return True
        
    def _handle_createnotify(self, event: xproto.CreateNotifyEvent) -> bool:
        """Xử lý window create"""
        # Window mới được tạo, sẽ được quản lý khi có MapRequest
        return True
        
    def _handle_destroynotify(self, event: xproto.DestroyNotifyEvent) -> bool:
        """Xử lý window destroy"""
        self.unregister_window(event.window)
        return True
        
    def _handle_maprequest(self, event: xproto.MapRequestEvent) -> bool:
        """Xử lý window map request"""
        # Tạo Window object mới và đăng ký
        window = Window(self.xconn, event.window)
        self.register_window(window)
        
        # Set border
        from config import config
        window.set_border_width(config.get_border_width())
        window.set_border_color(0xff333333)
        
        # Map window
        window.map()
        
        # Focus window nếu là window đầu tiên
        if not self.focused_window:
            self.set_focused_window(window)
            
        return True
        
    def _handle_unmapnotify(self, event: xproto.UnmapNotifyEvent) -> bool:
        """Xử lý window unmap"""
        window = self.get_window(event.window)
        if window:
            window.unmap()
        return True
        
    def _handle_configurerequest(self, event: xproto.ConfigureRequestEvent) -> bool:
        """Xử lý window configure request"""
        window = self.get_window(event.window)
        if window and not window.is_floating:
            # Từ chối configure request cho tiling windows
            # WM sẽ quản lý geometry
            return True
        else:
            # Cho phép configure cho floating windows
            return False
            
    def _handle_configurenotify(self, event: xproto.ConfigureNotifyEvent) -> bool:
        """Xử lý window configure notify"""
        window = self.get_window(event.window)
        if window:
            # Cập nhật geometry
            window.geometry = (event.x, event.y, event.width, event.height)
        return True
        
    def _handle_focusin(self, event: xproto.FocusInEvent) -> bool:
        """Xử lý window focus in"""
        window = self.get_window(event.window)
        if window:
            self.set_focused_window(window)
        return True
        
    def _handle_focusout(self, event: xproto.FocusOutEvent) -> bool:
        """Xử lý window focus out"""
        return True
        
    def _handle_propertynotify(self, event: xproto.PropertyNotifyEvent) -> bool:
        """Xử lý property change"""
        window = self.get_window(event.window)
        if window:
            # Xử lý các property thay đổi như WM_NAME, _NET_WM_NAME, etc.
            if event.atom == xproto.Atom.WM_NAME or event.atom == xproto.Atom._NET_WM_NAME:
                # Window title thay đổi, có thể cập nhật status bar
                pass
        return True
        
    def _handle_clientmessage(self, event: xproto.ClientMessageEvent) -> bool:
        """Xử lý client message"""
        # Xử lý các message như _NET_WM_STATE, _NET_CURRENT_DESKTOP, etc.
        return True
        
    def get_all_windows(self) -> List[Window]:
        """Lấy tất cả windows đang được quản lý"""
        return list(self.windows.values())
        
    def get_visible_windows(self) -> List[Window]:
        """Lấy tất cả windows đang hiển thị"""
        return [w for w in self.windows.values() if w.is_mapped]
        
    def get_tiling_windows(self) -> List[Window]:
        """Lấy tất cả tiling windows"""
        return [w for w in self.windows.values() if w.is_mapped and not w.is_floating]
        
    def get_floating_windows(self) -> List[Window]:
        """Lấy tất cả floating windows"""
        return [w for w in self.windows.values() if w.is_mapped and w.is_floating]
