from typing import List, Tuple, Optional
from .window import Window
from .conn import XConnection

class Layout:
    """Base class cho các layout algorithm"""
    
    def __init__(self, xconn: XConnection):
        self.xconn = xconn
        
    def arrange(self, windows: List[Window], screen_geometry: Tuple[int, int, int, int]):
        """Sắp xếp các cửa sổ theo layout"""
        raise NotImplementedError

class TilingLayout(Layout):
    """Layout tiling giống i3 - chia màn hình thành master và stack area"""
    
    def __init__(self, xconn: XConnection, master_ratio: float = 0.6):
        super().__init__(xconn)
        self.master_ratio = master_ratio  # Tỷ lệ master area
        
    def arrange(self, windows: List[Window], screen_geometry: Tuple[int, int, int, int]):
        """Sắp xếp cửa sổ theo tiling layout"""
        if not windows:
            return
            
        screen_x, screen_y, screen_width, screen_height = screen_geometry
        n = len(windows)
        
        if n == 1:
            # Chỉ có 1 cửa sổ, chiếm toàn bộ màn hình
            windows[0].set_geometry(screen_x, screen_y, screen_width, screen_height)
        else:
            # Có nhiều cửa sổ, chia thành master và stack
            master_width = int(screen_width * self.master_ratio)
            stack_width = screen_width - master_width
            
            # Master window (cửa sổ đầu tiên)
            master_window = windows[0]
            master_window.set_geometry(
                screen_x, screen_y, 
                master_width, screen_height
            )
            
            # Stack windows (các cửa sổ còn lại)
            if n > 1:
                stack_height = screen_height // (n - 1)
                for i, window in enumerate(windows[1:], 1):
                    y_pos = screen_y + (i - 1) * stack_height
                    height = stack_height if i < n - 1 else screen_height - y_pos
                    window.set_geometry(
                        screen_x + master_width, y_pos,
                        stack_width, height
                    )

class MonocleLayout(Layout):
    """Layout monocle - chỉ hiển thị 1 cửa sổ tại một thời điểm"""
    
    def arrange(self, windows: List[Window], screen_geometry: Tuple[int, int, int, int]):
        """Sắp xếp cửa sổ theo monocle layout"""
        if not windows:
            return
            
        screen_x, screen_y, screen_width, screen_height = screen_geometry
        
        for i, window in enumerate(windows):
            if i == 0:  # Chỉ hiển thị cửa sổ đầu tiên
                window.set_geometry(screen_x, screen_y, screen_width, screen_height)
                window.map()
            else:
                window.unmap()

class StackLayout(Layout):
    """Layout stack - tất cả cửa sổ chia đều theo chiều ngang"""
    
    def arrange(self, windows: List[Window], screen_geometry: Tuple[int, int, int, int]):
        """Sắp xếp cửa sổ theo stack layout"""
        if not windows:
            return
            
        screen_x, screen_y, screen_width, screen_height = screen_geometry
        n = len(windows)
        
        window_width = screen_width // n
        
        for i, window in enumerate(windows):
            x_pos = screen_x + i * window_width
            width = window_width if i < n - 1 else screen_width - x_pos
            window.set_geometry(x_pos, screen_y, width, screen_height)

class LayoutManager:
    """Quản lý các layout khác nhau"""
    
    def __init__(self, xconn: XConnection):
        self.xconn = xconn
        self.current_layout = TilingLayout(xconn)
        self.layouts = {
            'tiling': TilingLayout(xconn),
            'monocle': MonocleLayout(xconn),
            'stack': StackLayout(xconn)
        }
        self.current_layout_name = 'tiling'
        
    def set_layout(self, layout_name: str):
        """Chuyển đổi layout"""
        if layout_name in self.layouts:
            self.current_layout = self.layouts[layout_name]
            self.current_layout_name = layout_name
            return True
        return False
        
    def get_current_layout_name(self) -> str:
        """Lấy tên layout hiện tại"""
        return self.current_layout_name
        
    def cycle_layout(self):
        """Chuyển đổi layout theo vòng lặp"""
        layout_names = list(self.layouts.keys())
        current_index = layout_names.index(self.current_layout_name)
        next_index = (current_index + 1) % len(layout_names)
        self.set_layout(layout_names[next_index])
        
    def arrange_windows(self, windows: List[Window]):
        """Sắp xếp các cửa sổ theo layout hiện tại"""
        screen_width, screen_height = self.xconn.get_screen_geometry()
        screen_geometry = (0, 0, screen_width, screen_height)
        
        # Chỉ arrange những cửa sổ không phải floating
        tiling_windows = [w for w in windows if not w.is_floating]
        self.current_layout.arrange(tiling_windows, screen_geometry)
        
    def adjust_master_ratio(self, delta: float):
        """Điều chỉnh tỷ lệ master area (chỉ áp dụng cho tiling layout)"""
        if isinstance(self.current_layout, TilingLayout):
            self.current_layout.master_ratio = max(0.1, min(0.9, 
                self.current_layout.master_ratio + delta))
