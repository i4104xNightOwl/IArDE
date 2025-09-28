import xcffib.xproto as xproto
from typing import Optional, List
from .conn import XConnection

class Window:
    """Đại diện cho một cửa sổ được quản lý bởi WM"""
    
    def __init__(self, xconn: XConnection, window_id: int):
        self.xconn = xconn
        self.window_id = window_id
        self.is_focused = False
        self.is_mapped = False
        self.is_floating = False
        self.border_width = 3
        self.geometry = None  # (x, y, width, height)
        self.original_geometry = None  # Trước khi maximize
        self.workspace = None
        self.parent = None
        self.children: List[int] = []
        
    def get_geometry(self) -> Optional[tuple]:
        """Lấy geometry hiện tại của cửa sổ"""
        try:
            reply = self.xconn.conn.core.GetGeometry(self.window_id).reply()
            return (reply.x, reply.y, reply.width, reply.height)
        except:
            return None
            
    def set_geometry(self, x: int, y: int, width: int, height: int):
        """Đặt vị trí và kích thước cửa sổ"""
        self.geometry = (x, y, width, height)
        self.xconn.conn.core.ConfigureWindow(
            self.window_id,
            xproto.ConfigWindow.X | xproto.ConfigWindow.Y | 
            xproto.ConfigWindow.Width | xproto.ConfigWindow.Height,
            [x, y, width, height]
        )
        self.xconn.flush()
        
    def map(self):
        """Hiển thị cửa sổ"""
        self.xconn.conn.core.MapWindow(self.window_id)
        self.is_mapped = True
        self.xconn.flush()
        
    def unmap(self):
        """Ẩn cửa sổ"""
        self.xconn.conn.core.UnmapWindow(self.window_id)
        self.is_mapped = False
        self.xconn.flush()
        
    def focus(self):
        """Focus cửa sổ"""
        self.xconn.conn.core.SetInputFocus(
            xproto.InputFocus.PointerRoot,
            self.window_id,
            xproto.Time.CurrentTime
        )
        self.xconn.flush()
        
    def set_border_color(self, color: int):
        """Đặt màu border"""
        self.xconn.conn.core.ChangeWindowAttributes(
            self.window_id,
            xproto.CW.BorderPixel,
            [color]
        )
        self.xconn.flush()
        
    def set_border_width(self, width: int):
        """Đặt độ dày border"""
        self.border_width = width
        self.xconn.conn.core.ConfigureWindow(
            self.window_id,
            xproto.ConfigWindow.BorderWidth,
            [width]
        )
        self.xconn.flush()
        
    def kill(self):
        """Đóng cửa sổ"""
        try:
            # Thử đóng một cách lịch sự trước
            self.xconn.conn.core.SendEvent(
                True, self.window_id, xproto.EventMask.NoEvent,
                b'WM_DELETE_WINDOW'
            )
            # Nếu không được, force kill
            self.xconn.conn.core.KillClient(self.window_id)
        except:
            pass
        self.xconn.flush()
        
    def get_wm_name(self) -> str:
        """Lấy tên của cửa sổ"""
        try:
            # Thử lấy _NET_WM_NAME trước
            reply = self.xconn.conn.core.GetProperty(
                False, self.window_id,
                xproto.Atom._NET_WM_NAME,
                xproto.Atom._UTF8_STRING,
                0, 1024
            ).reply()
            if reply.value:
                return reply.value.decode('utf-8')
        except:
            pass
            
        try:
            # Fallback về WM_NAME
            reply = self.xconn.conn.core.GetProperty(
                False, self.window_id,
                xproto.Atom.WM_NAME,
                xproto.Atom.STRING,
                0, 1024
            ).reply()
            if reply.value:
                return reply.value.decode('utf-8')
        except:
            pass
            
        return f"Window {self.window_id}"
        
    def is_maximized(self) -> bool:
        """Kiểm tra xem cửa sổ có đang maximized không"""
        try:
            reply = self.xconn.conn.core.GetProperty(
                False, self.window_id,
                xproto.Atom._NET_WM_STATE,
                xproto.Atom.ATOM,
                0, 1024
            ).reply()
            if reply.value:
                states = list(reply.value)
                # Kiểm tra _NET_WM_STATE_MAXIMIZED_HORZ và _NET_WM_STATE_MAXIMIZED_VERT
                return (xproto.Atom._NET_WM_STATE_MAXIMIZED_HORZ in states or
                        xproto.Atom._NET_WM_STATE_MAXIMIZED_VERT in states)
        except:
            pass
        return False
        
    def toggle_floating(self):
        """Chuyển đổi giữa floating và tiling"""
        self.is_floating = not self.is_floating
        if self.is_floating:
            # Center cửa sổ khi chuyển sang floating
            screen_width, screen_height = self.xconn.get_screen_geometry()
            if self.geometry:
                width, height = self.geometry[2], self.geometry[3]
                x = (screen_width - width) // 2
                y = (screen_height - height) // 2
                self.set_geometry(x, y, width, height)
