# IArDE Development Guide

## Hướng dẫn phát triển và mở rộng IArDE

### 1. Thêm Layout mới

#### Tạo Custom Layout

```python
# Trong core/layout.py

class MyCustomLayout(Layout):
    """Layout tùy chỉnh của bạn"""
    
    def __init__(self, xconn: XConnection):
        super().__init__(xconn)
        self.custom_parameter = 0.5  # Tham số tùy chỉnh
        
    def arrange(self, windows: List[Window], screen_geometry: Tuple[int, int, int, int]):
        """Implement logic layout của bạn"""
        if not windows:
            return
            
        screen_x, screen_y, screen_width, screen_height = screen_geometry
        n = len(windows)
        
        # Ví dụ: Chia cửa sổ theo grid 2x2
        if n <= 4:
            cols = 2
            rows = (n + 1) // 2
            
            cell_width = screen_width // cols
            cell_height = screen_height // rows
            
            for i, window in enumerate(windows):
                row = i // cols
                col = i % cols
                
                x = screen_x + col * cell_width
                y = screen_y + row * cell_height
                
                window.set_geometry(x, y, cell_width, cell_height)
```

#### Đăng ký Layout

```python
# Trong LayoutManager.__init__()

self.layouts = {
    'tiling': TilingLayout(xconn),
    'monocle': MonocleLayout(xconn),
    'stack': StackLayout(xconn),
    'grid': MyCustomLayout(xconn),  # Thêm layout mới
}
```

#### Thêm Keybind cho Layout

```python
# Trong KeybindManager.setup_default_keybinds()

"Mod4+g": lambda: wm.set_layout('grid'),  # Thêm keybind mới
```

### 2. Thêm Keybind mới

#### Thêm Action Method

```python
# Trong core/wm.py

def my_custom_action(self):
    """Action tùy chỉnh của bạn"""
    focused = self.event_handler.get_focused_window()
    if focused:
        # Thực hiện action
        print(f"Custom action on window: {focused.get_wm_name()}")
        
def toggle_window_opacity(self):
    """Ví dụ: Toggle window opacity"""
    focused = self.event_handler.get_focused_window()
    if focused:
        # Implementation sẽ cần thêm vào Window class
        focused.toggle_opacity()
```

#### Đăng ký Keybind

```python
# Trong KeybindManager.setup_default_keybinds()

"Mod4+o": lambda: wm.toggle_window_opacity(),
"Mod4+Shift+o": lambda: wm.my_custom_action(),
```

#### Thêm Keybind động

```python
# Trong WindowManager

def add_custom_keybind(self, keybind_str: str, action: callable):
    """Thêm keybind mới trong runtime"""
    return self.keybind_manager.add_keybind(keybind_str, action)

def remove_custom_keybind(self, keybind_str: str):
    """Xóa keybind trong runtime"""
    return self.keybind_manager.remove_keybind(keybind_str)
```

### 3. Thêm Event Handler mới

#### Tạo Custom Event Handler

```python
# Trong core/events.py

def _handle_propertynotify(self, event: xproto.PropertyNotifyEvent) -> bool:
    """Xử lý property change event"""
    window = self.get_window(event.window)
    if window:
        # Xử lý các property thay đổi
        if event.atom == xproto.Atom._NET_WM_STATE:
            # Window state thay đổi
            self._handle_window_state_change(window)
        elif event.atom == xproto.Atom._NET_WM_DESKTOP:
            # Window workspace thay đổi
            self._handle_workspace_change(window)
    
    return True

def _handle_window_state_change(self, window: Window):
    """Xử lý khi window state thay đổi"""
    # Kiểm tra fullscreen state
    if window.is_fullscreen():
        # Xử lý fullscreen
        pass

def _handle_workspace_change(self, window: Window):
    """Xử lý khi window chuyển workspace"""
    # Update workspace tracking
    pass
```

#### Thêm Window State

```python
# Trong core/window.py

def is_fullscreen(self) -> bool:
    """Kiểm tra fullscreen state"""
    try:
        reply = self.xconn.conn.core.GetProperty(
            False, self.window_id,
            xproto.Atom._NET_WM_STATE,
            xproto.Atom.ATOM,
            0, 1024
        ).reply()
        if reply.value:
            states = list(reply.value)
            return xproto.Atom._NET_WM_STATE_FULLSCREEN in states
    except:
        pass
    return False

def toggle_fullscreen(self):
    """Toggle fullscreen mode"""
    if self.is_fullscreen():
        self._unset_fullscreen()
    else:
        self._set_fullscreen()

def _set_fullscreen(self):
    """Set window to fullscreen"""
    # Implementation fullscreen
    pass

def _unset_fullscreen(self):
    """Unset fullscreen mode"""
    # Implementation unset fullscreen
    pass
```

### 4. Thêm Config Option mới

#### Thêm vào Default Config

```python
# Trong config.py

def _get_default_config(self) -> Dict[str, Any]:
    return {
        # ... existing config ...
        
        # Thêm section mới
        "advanced_features": {
            "window_opacity": 1.0,
            "animation_duration": 200,
            "enable_transparency": False,
            "custom_borders": {
                "enabled": False,
                "thickness": 5,
                "color": 0xff00ff00
            }
        },
        
        # Thêm vào existing section
        "window": {
            "auto_focus": True,
            "focus_follows_mouse": False,
            "mouse_warping": True,
            "floating_modifier": "Mod4",
            "default_floating_size": [400, 300],
            "default_floating_border": "normal",
            "new_feature": True  # Thêm option mới
        }
    }
```

#### Thêm Getter Methods

```python
# Trong config.py

def get_window_opacity(self) -> float:
    """Lấy window opacity"""
    return self.get("advanced_features.window_opacity", 1.0)

def get_animation_duration(self) -> int:
    """Lấy animation duration"""
    return self.get("advanced_features.animation_duration", 200)

def is_custom_borders_enabled(self) -> bool:
    """Kiểm tra custom borders"""
    return self.get("advanced_features.custom_borders.enabled", False)
```

### 5. Thêm Workspace Support

#### Tạo Workspace Class

```python
# Tạo file mới: core/workspace.py

from typing import List, Optional
from .window import Window

class Workspace:
    """Đại diện cho một workspace"""
    
    def __init__(self, name: str, xconn):
        self.name = name
        self.xconn = xconn
        self.windows: List[Window] = []
        self.focused_window: Optional[Window] = None
        self.layout_manager = None
        
    def add_window(self, window: Window):
        """Thêm window vào workspace"""
        self.windows.append(window)
        window.workspace = self
        
    def remove_window(self, window: Window):
        """Xóa window khỏi workspace"""
        if window in self.windows:
            self.windows.remove(window)
            window.workspace = None
            
    def focus_window(self, window: Window):
        """Focus window trong workspace"""
        self.focused_window = window
        window.focus()
        
    def get_visible_windows(self) -> List[Window]:
        """Lấy windows hiển thị"""
        return [w for w in self.windows if w.is_mapped]
```

#### Tích hợp vào WindowManager

```python
# Trong core/wm.py

class WindowManager:
    def __init__(self):
        # ... existing code ...
        
        # Workspace management
        self.workspaces = {}
        self.current_workspace = None
        self._initialize_workspaces()
        
    def _initialize_workspaces(self):
        """Khởi tạo workspaces"""
        workspace_names = self.config.get_workspace_names()
        
        for name in workspace_names:
            workspace = Workspace(name, self.xconn)
            self.workspaces[name] = workspace
            
        # Set workspace đầu tiên làm current
        if workspace_names:
            self.current_workspace = self.workspaces[workspace_names[0]]
            
    def switch_workspace(self, workspace_name: str):
        """Chuyển workspace"""
        if workspace_name in self.workspaces:
            # Hide windows trong workspace hiện tại
            if self.current_workspace:
                for window in self.current_workspace.get_visible_windows():
                    window.unmap()
                    
            # Switch to new workspace
            self.current_workspace = self.workspaces[workspace_name]
            
            # Show windows trong workspace mới
            for window in self.current_workspace.get_visible_windows():
                window.map()
                
            self._update_layout()
```

### 6. Thêm Status Bar

#### Tạo Status Bar Class

```python
# Tạo file mới: core/statusbar.py

import xcffib.xproto as xproto
from .conn import XConnection

class StatusBar:
    """Status bar hiển thị thông tin WM"""
    
    def __init__(self, xconn: XConnection):
        self.xconn = xconn
        self.window_id = None
        self.height = 24
        self._create_status_bar()
        
    def _create_status_bar(self):
        """Tạo status bar window"""
        self.window_id = self.xconn.generate_id()
        
        # Tạo window
        self.xconn.conn.core.CreateWindow(
            self.xconn.screen_depth,
            self.window_id,
            self.xconn.root,
            0, 0,  # Position
            self.xconn.screen_width, self.height,  # Size
            0,  # Border width
            xproto.WindowClass.InputOutput,
            self.xconn.screen.root_visual,
            xproto.CW.BackPixel | xproto.CW.EventMask,
            [0xff333333, xproto.EventMask.Exposure]
        )
        
        # Map window
        self.xconn.conn.core.MapWindow(self.window_id)
        
    def update_content(self, content: str):
        """Cập nhật nội dung status bar"""
        # Implementation text rendering
        pass
        
    def set_position(self, position: str):
        """Đặt vị trí status bar (top/bottom)"""
        if position == "bottom":
            y = self.xconn.screen_height - self.height
        else:  # top
            y = 0
            
        self.xconn.conn.core.ConfigureWindow(
            self.window_id,
            xproto.ConfigWindow.Y,
            [y]
        )
```

### 7. Debug và Testing

#### Thêm Logging

```python
# Tạo file mới: core/logger.py

import logging
import os
from datetime import datetime

class WMLogger:
    """Logger cho IArDE"""
    
    def __init__(self):
        self.logger = logging.getLogger('IArDE')
        self.logger.setLevel(logging.DEBUG)
        
        # Tạo log directory
        log_dir = os.path.expanduser('~/.config/iarde/logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # File handler
        log_file = os.path.join(log_dir, f'iarde_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def debug(self, message: str):
        self.logger.debug(message)
        
    def info(self, message: str):
        self.logger.info(message)
        
    def warning(self, message: str):
        self.logger.warning(message)
        
    def error(self, message: str):
        self.logger.error(message)

# Global logger instance
logger = WMLogger()
```

#### Sử dụng Logger

```python
# Trong các file khác

from core.logger import logger

class WindowManager:
    def __init__(self):
        logger.info("Initializing IArDE Window Manager")
        # ... existing code ...
        
    def spawn_terminal(self):
        logger.debug("Spawning terminal")
        # ... existing code ...
```

### 8. Performance Optimization

#### Lazy Layout Calculation

```python
# Trong LayoutManager

class LayoutManager:
    def __init__(self, xconn: XConnection):
        # ... existing code ...
        self.layout_dirty = False
        self.last_window_count = 0
        
    def mark_dirty(self):
        """Đánh dấu layout cần tính lại"""
        self.layout_dirty = True
        
    def arrange_windows(self, windows: List[Window]):
        """Chỉ arrange khi cần thiết"""
        if not self.layout_dirty and len(windows) == self.last_window_count:
            return
            
        # Tính layout
        screen_width, screen_height = self.xconn.get_screen_geometry()
        screen_geometry = (0, 0, screen_width, screen_height)
        
        tiling_windows = [w for w in windows if not w.is_floating]
        self.current_layout.arrange(tiling_windows, screen_geometry)
        
        # Update state
        self.layout_dirty = False
        self.last_window_count = len(windows)
```

#### Event Batching

```python
# Trong EventHandler

class EventHandler:
    def __init__(self, xconn: XConnection):
        # ... existing code ...
        self.pending_layout_update = False
        
    def handle_event(self, event) -> bool:
        """Xử lý event với batching"""
        result = self._handle_event_immediate(event)
        
        # Mark layout update nếu cần
        if self._should_update_layout(event):
            self.pending_layout_update = True
            
        return result
        
    def flush_layout_updates(self):
        """Flush tất cả layout updates"""
        if self.pending_layout_update:
            # Trigger layout update
            self.pending_layout_update = False
```

### 9. Build và Distribution

#### Setup.py

```python
# Tạo file setup.py

from setuptools import setup, find_packages

setup(
    name="iarde",
    version="1.0.0",
    description="A simple tiling window manager for X11",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "xcffib>=1.4.0",
    ],
    entry_points={
        "console_scripts": [
            "iarde=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
```

#### Build Script

```bash
#!/bin/bash
# build.sh

echo "Building IArDE..."

# Install dependencies
pip install -r requirements.txt

# Run tests (nếu có)
python -m pytest tests/

# Build package
python setup.py sdist bdist_wheel

echo "Build complete!"
```

### 10. Best Practices

#### Code Organization
- Mỗi module có một responsibility rõ ràng
- Sử dụng type hints để code dễ hiểu
- Document tất cả public methods

#### Error Handling
- Luôn bắt exception trong event handlers
- Log errors để debug
- Graceful degradation khi có lỗi

#### Performance
- Cache kết quả tính toán đắt
- Lazy evaluation khi có thể
- Batch updates để giảm X11 calls

#### Testing
- Unit tests cho mỗi module
- Integration tests cho workflow chính
- Mock X11 để test offline

#### Security
- Validate tất cả input từ config
- Sanitize window titles và properties
- Không execute arbitrary code từ config
