import xcffib
import xcffib.xproto as xproto
from typing import Tuple, Optional

class XConnection:
    """Quản lý kết nối đến X server và thông tin màn hình"""
    
    def __init__(self):
        self.conn = xcffib.connect()
        self.setup = self.conn.get_setup()
        self.screen = self.setup.roots[self.conn.pref_screen]
        self.root = self.screen.root
        self.screen_width = self.screen.width_in_pixels
        self.screen_height = self.screen.height_in_pixels
        self.screen_depth = self.screen.root_depth
        
    def flush(self):
        """Gửi tất cả các request đang chờ đến X server"""
        self.conn.flush()
        
    def get_screen_geometry(self) -> Tuple[int, int]:
        """Trả về kích thước màn hình (width, height)"""
        return self.screen_width, self.screen_height
        
    def get_root_window(self):
        """Trả về root window"""
        return self.root
        
    def generate_id(self) -> int:
        """Tạo ID mới cho window/pixmap/gc"""
        return self.conn.generate_id()
        
    def wait_for_event(self):
        """Chờ sự kiện từ X server"""
        return self.conn.wait_for_event()
        
    def grab_key(self, window, mod_mask: int, keycode: int) -> bool:
        """Grab một key combination"""
        try:
            self.conn.core.GrabKey(
                True, window, mod_mask, keycode,
                xproto.GrabMode.Async, xproto.GrabMode.Async
            )
            self.flush()
            return True
        except Exception:
            return False
            
    def ungrab_key(self, window, mod_mask: int, keycode: int):
        """Ungrab một key combination"""
        self.conn.core.UngrabKey(keycode, window, mod_mask)
        self.flush()
        
    def grab_button(self, window, button: int, mod_mask: int = 0):
        """Grab mouse button"""
        self.conn.core.GrabButton(
            True, window, xproto.EventMask.ButtonPress | xproto.EventMask.ButtonRelease,
            xproto.GrabMode.Async, xproto.GrabMode.Async,
            xproto.Atom._NONE, xproto.Atom._NONE, button, mod_mask
        )
        self.flush()

