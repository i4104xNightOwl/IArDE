import subprocess
import xcffib.xproto as xproto
from typing import List, Optional
from .conn import XConnection
from .window import Window
from .layout import LayoutManager
from .keybinds import KeybindManager
from .events import EventHandler
from config import config

class WindowManager:
    """Window Manager chính - điều phối tất cả các module"""
    
    def __init__(self):
        # Khởi tạo các module chính
        self.xconn = XConnection()
        self.layout_manager = LayoutManager(self.xconn)
        self.keybind_manager = KeybindManager(self.xconn)
        self.event_handler = EventHandler(self.xconn)
        
        # Cấu hình
        self.config = config
        self.running = False
        
        # Khởi tạo WM
        self._initialize_wm()
        
    def _initialize_wm(self):
        """Khởi tạo window manager"""
        try:
            # Thiết lập root window
            self._setup_root_window()
            
            # Thiết lập keybinds
            self.keybind_manager.setup_default_keybinds(self)
            
            print("IArDE Window Manager started successfully!")
            print("Press Super+Enter to open terminal")
            print("Press Super+Shift+q to quit")
            
        except Exception as e:
            print(f"Failed to initialize window manager: {e}")
            raise
            
    def _setup_root_window(self):
        """Thiết lập root window"""
        mask = (xproto.CW.EventMask,)
        values = [
            xproto.EventMask.SubstructureRedirect |
            xproto.EventMask.SubstructureNotify |
            xproto.EventMask.KeyPress |
            xproto.EventMask.KeyRelease |
            xproto.EventMask.ButtonPress |
            xproto.EventMask.ButtonRelease |
            xproto.EventMask.PointerMotion |
            xproto.EventMask.EnterWindow |
            xproto.EventMask.LeaveWindow |
            xproto.EventMask.FocusChange |
            xproto.EventMask.PropertyChange
        ]
        
        try:
            self.xconn.conn.core.ChangeWindowAttributesChecked(
                self.xconn.root, mask, values
            ).check()
        except xcffib.xproto.BadAccess:
            print("Another window manager is already running!")
            print("Please exit the current WM first.")
            exit(1)
        
    def run(self):
        """Chạy window manager - main event loop"""
        self.running = True
        
        while self.running:
            try:
                event = self.xconn.wait_for_event()
                
                # Xử lý keypress trước
                if isinstance(event, xproto.KeyPressEvent):
                    if not self.keybind_manager.handle_keypress(event):
                        # Nếu keybind không xử lý được, chuyển cho event handler
                        self.event_handler.handle_event(event)
                else:
                    # Xử lý các event khác
                    self.event_handler.handle_event(event)
                    
                # Cập nhật layout nếu cần
                self._update_layout()
                
            except KeyboardInterrupt:
                print("\\nReceived interrupt signal, shutting down...")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                continue
                
        self.quit()
        
    def _update_layout(self):
        """Cập nhật layout của các cửa sổ"""
        tiling_windows = self.event_handler.get_tiling_windows()
        self.layout_manager.arrange_windows(tiling_windows)
        
    # Window management methods
    def spawn_terminal(self):
        """Mở terminal"""
        terminal_cmd = self.config.get_terminal_command()
        try:
            subprocess.Popen([terminal_cmd])
        except Exception as e:
            print(f"Failed to spawn terminal: {e}")
            
    def spawn_dmenu(self):
        """Mở dmenu"""
        dmenu_cmd = self.config.get("applications.dmenu", "dmenu_run")
        try:
            subprocess.Popen(dmenu_cmd.split())
        except Exception as e:
            print(f"Failed to spawn dmenu: {e}")
            
    def kill_focused_window(self):
        """Đóng cửa sổ đang focus"""
        focused = self.event_handler.get_focused_window()
        if focused:
            focused.kill()
            self.event_handler.unregister_window(focused.window_id)
            
    def toggle_fullscreen(self):
        """Chuyển đổi fullscreen"""
        focused = self.event_handler.get_focused_window()
        if focused:
            # TODO: Implement fullscreen toggle
            pass
            
    def toggle_floating(self):
        """Chuyển đổi floating/tiling"""
        focused = self.event_handler.get_focused_window()
        if focused:
            focused.toggle_floating()
            self._update_layout()
            
    # Layout methods
    def set_layout(self, layout_name: str):
        """Chuyển đổi layout"""
        if self.layout_manager.set_layout(layout_name):
            self._update_layout()
            print(f"Layout changed to: {layout_name}")
            
    def cycle_layout(self):
        """Chuyển đổi layout theo vòng lặp"""
        self.layout_manager.cycle_layout()
        self._update_layout()
        print(f"Layout changed to: {self.layout_manager.get_current_layout_name()}")
        
    def adjust_master_ratio(self, delta: float):
        """Điều chỉnh tỷ lệ master area"""
        self.layout_manager.adjust_master_ratio(delta)
        self._update_layout()
        
    # Window focus methods (vim-like navigation)
    def focus_left(self):
        """Focus cửa sổ bên trái"""
        self._focus_direction('left')
        
    def focus_right(self):
        """Focus cửa sổ bên phải"""
        self._focus_direction('right')
        
    def focus_up(self):
        """Focus cửa sổ phía trên"""
        self._focus_direction('up')
        
    def focus_down(self):
        """Focus cửa sổ phía dưới"""
        self._focus_direction('down')
        
    def _focus_direction(self, direction: str):
        """Focus theo hướng"""
        # TODO: Implement window focus direction logic
        # Cần implement logic để tìm cửa sổ gần nhất theo hướng
        pass
        
    # Window move methods
    def move_left(self):
        """Di chuyển cửa sổ sang trái"""
        self._move_direction('left')
        
    def move_right(self):
        """Di chuyển cửa sổ sang phải"""
        self._move_direction('right')
        
    def move_up(self):
        """Di chuyển cửa sổ lên trên"""
        self._move_direction('up')
        
    def move_down(self):
        """Di chuyển cửa sổ xuống dưới"""
        self._move_direction('down')
        
    def _move_direction(self, direction: str):
        """Di chuyển cửa sổ theo hướng"""
        # TODO: Implement window move direction logic
        pass
        
    # Utility methods
    def reload_config(self):
        """Reload cấu hình"""
        self.config.reload()
        print("Configuration reloaded")
        
    def restart_wm(self):
        """Restart window manager"""
        print("Restarting window manager...")
        self.quit()
        # TODO: Implement restart logic
        
    def quit(self):
        """Thoát window manager"""
        print("Shutting down window manager...")
        self.running = False
        
        # Cleanup
        for window in self.event_handler.get_all_windows():
            window.unmap()
            
        self.xconn.flush()
        print("Window manager stopped.")
        
    def get_status_info(self) -> dict:
        """Lấy thông tin trạng thái"""
        windows = self.event_handler.get_all_windows()
        focused = self.event_handler.get_focused_window()
        
        return {
            'total_windows': len(windows),
            'tiling_windows': len(self.event_handler.get_tiling_windows()),
            'floating_windows': len(self.event_handler.get_floating_windows()),
            'current_layout': self.layout_manager.get_current_layout_name(),
            'focused_window': focused.get_wm_name() if focused else None,
        }
