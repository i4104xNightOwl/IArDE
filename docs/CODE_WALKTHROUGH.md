# IArDE Code Walkthrough

## Giải thích chi tiết từng file code

### 1. main.py - Entry Point

```python
#!/usr/bin/env python3
"""
IArDE - A simple tiling window manager for X11
Inspired by i3wm but written in Python using xcffib
"""

import sys
import os
import signal
from core.wm import WindowManager

def signal_handler(signum, frame):
    """Xử lý signal để shutdown graceful"""
    print(f"\\nReceived signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """Main entry point"""
    # Đăng ký signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Tạo và chạy window manager
        wm = WindowManager()
        wm.run()
        
    except KeyboardInterrupt:
        print("\\nReceived keyboard interrupt")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        print("IArDE window manager stopped.")
```

**Giải thích**:
- **Signal handling**: Đăng ký handler cho SIGINT (Ctrl+C) và SIGTERM để shutdown graceful
- **Exception handling**: Bắt KeyboardInterrupt và các exception khác
- **Entry point**: Tạo WindowManager instance và chạy main loop

---

### 2. core/wm.py - Window Manager Chính

#### Khởi tạo WindowManager

```python
class WindowManager:
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
```

**Giải thích**:
- **Module initialization**: Tạo các module con với dependency injection
- **Config**: Sử dụng global config instance
- **Running flag**: Để control main loop

#### Thiết lập Root Window

```python
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
        exit(1)
```

**Giải thích**:
- **Event masks**: Đăng ký các loại sự kiện muốn nhận từ root window
- **SubstructureRedirect**: Cho phép WM intercept các request từ client windows
- **BadAccess exception**: Xảy ra khi đã có WM khác đang chạy

#### Main Event Loop

```python
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
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            continue
            
    self.quit()
```

**Giải thích**:
- **Blocking wait**: `wait_for_event()` sẽ block cho đến khi có event
- **Event prioritization**: KeyPressEvent được xử lý bởi KeybindManager trước
- **Error handling**: Bắt exception để WM không crash
- **Layout update**: Cập nhật layout sau mỗi event

---

### 3. core/conn.py - X11 Connection

#### Khởi tạo Connection

```python
class XConnection:
    def __init__(self):
        self.conn = xcffib.connect()
        self.setup = self.conn.get_setup()
        self.screen = self.setup.roots[self.conn.pref_screen]
        self.root = self.screen.root
        self.screen_width = self.screen.width_in_pixels
        self.screen_height = self.screen.height_in_pixels
        self.screen_depth = self.screen.root_depth
```

**Giải thích**:
- **xcffib.connect()**: Kết nối đến X11 server
- **get_setup()**: Lấy thông tin về X11 server
- **pref_screen**: Screen mặc định (thường là 0)
- **Cache geometry**: Lưu kích thước màn hình để tránh query nhiều lần

#### Grab Key

```python
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
```

**Giải thích**:
- **GrabKey**: Đăng ký key combination với X11 server
- **Async mode**: Cho phép key được xử lý bất đồng bộ
- **Error handling**: Trả về False nếu grab thất bại (key đã được grab)

---

### 4. core/window.py - Window Management

#### Khởi tạo Window

```python
class Window:
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
```

**Giải thích**:
- **State tracking**: Theo dõi trạng thái focus, mapped, floating
- **Geometry**: Lưu vị trí và kích thước cửa sổ
- **Hierarchy**: Hỗ trợ parent-child relationship (cho tương lai)

#### Set Geometry

```python
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
```

**Giải thích**:
- **ConfigureWindow**: Gửi request thay đổi geometry đến X11
- **Value mask**: Chỉ định những thuộc tính nào cần thay đổi
- **Flush**: Đảm bảo request được gửi ngay lập tức

#### Toggle Floating

```python
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
```

**Giải thích**:
- **State toggle**: Chuyển đổi trạng thái floating
- **Auto-center**: Khi chuyển sang floating, center cửa sổ trên màn hình
- **Geometry preservation**: Giữ nguyên kích thước cửa sổ

---

### 5. core/layout.py - Layout System

#### TilingLayout

```python
class TilingLayout(Layout):
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
```

**Giải thích**:
- **Master-Stack pattern**: Chia màn hình thành 2 vùng
- **Master ratio**: Tỷ lệ master area (mặc định 60%)
- **Stack distribution**: Các cửa sổ stack chia đều theo chiều dọc
- **Edge case**: Cửa sổ cuối cùng nhận phần còn lại

#### LayoutManager

```python
class LayoutManager:
    def __init__(self, xconn: XConnection):
        self.xconn = xconn
        self.current_layout = TilingLayout(xconn)
        self.layouts = {
            'tiling': TilingLayout(xconn),
            'monocle': MonocleLayout(xconn),
            'stack': StackLayout(xconn)
        }
        self.current_layout_name = 'tiling'
        
    def cycle_layout(self):
        """Chuyển đổi layout theo vòng lặp"""
        layout_names = list(self.layouts.keys())
        current_index = layout_names.index(self.current_layout_name)
        next_index = (current_index + 1) % len(layout_names)
        self.set_layout(layout_names[next_index])
```

**Giải thích**:
- **Layout registry**: Dictionary chứa tất cả layout types
- **Current layout**: Track layout hiện tại
- **Cycle mechanism**: Chuyển đổi layout theo vòng lặp

---

### 6. core/keybinds.py - Keybind System

#### Parse Keybind

```python
def parse_keybind(self, keybind_str: str) -> Tuple[int, int]:
    """Parse keybind string thành (modifier_mask, keycode)"""
    parts = keybind_str.split('+')
    if len(parts) < 2:
        raise ValueError(f"Invalid keybind format: {keybind_str}")
        
    key = parts[-1].strip()
    modifiers = parts[:-1]
    
    # Parse modifiers
    mod_mask = 0
    for mod in modifiers:
        mod_name = mod.strip()
        if mod_name in self.modifier_masks:
            mod_mask |= self.modifier_masks[mod_name]
        else:
            raise ValueError(f"Unknown modifier: {mod_name}")
            
    # Parse key
    if key in self.key_symbols:
        keycode = self.key_symbols[key]
    else:
        # Thử parse như một số
        try:
            keycode = int(key)
        except ValueError:
            raise ValueError(f"Unknown key: {key}")
            
    return mod_mask, keycode
```

**Giải thích**:
- **String parsing**: Parse "Mod4+Return" thành modifier mask và keycode
- **Modifier combination**: OR các modifier masks lại với nhau
- **Key lookup**: Tìm keycode trong symbol table
- **Fallback**: Thử parse key như số nếu không tìm thấy

#### Handle Keypress

```python
def handle_keypress(self, event: xproto.KeyPressEvent):
    """Xử lý keypress event"""
    mod_mask = event.state
    keycode = event.detail
    
    keybind = (mod_mask, keycode)
    if keybind in self.keybinds:
        try:
            self.keybinds[keybind]()
            return True
        except Exception as e:
            print(f"Error executing keybind action: {e}")
    return False
```

**Giải thích**:
- **Event extraction**: Lấy modifier mask và keycode từ event
- **Dictionary lookup**: Tìm action function trong keybind dictionary
- **Action execution**: Thực thi action function
- **Error handling**: Bắt exception để tránh crash

---

### 7. core/events.py - Event Handling

#### MapRequest Handler

```python
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
```

**Giải thích**:
- **Window creation**: Tạo Window object cho cửa sổ mới
- **Registration**: Đăng ký window để theo dõi
- **Border setup**: Đặt border width và màu sắc
- **Map window**: Hiển thị cửa sổ
- **Auto focus**: Focus cửa sổ đầu tiên

#### Focus Management

```python
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
```

**Giải thích**:
- **State update**: Cập nhật trạng thái focus của cửa sổ cũ và mới
- **Visual feedback**: Thay đổi màu border để hiển thị cửa sổ được focus
- **X11 focus**: Gọi window.focus() để set focus trong X11

---

### 8. config.py - Configuration System

#### Config Loading

```python
def _load_config(self) -> Dict[str, Any]:
    """Load cấu hình từ file"""
    if os.path.exists(self.config_file):
        try:
            with open(self.config_file, 'r') as f:
                user_config = json.load(f)
            # Merge với default config
            return self._merge_configs(self.default_config, user_config)
        except Exception as e:
            print(f"Error loading config: {e}")
            print("Using default configuration")
            
    return self.default_config.copy()
```

**Giải thích**:
- **File existence check**: Kiểm tra config file có tồn tại không
- **JSON parsing**: Parse config file thành dictionary
- **Config merging**: Merge user config với default config
- **Fallback**: Sử dụng default config nếu có lỗi

#### Config Merging

```python
def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
    """Merge user config với default config"""
    result = default.copy()
    
    for key, value in user.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = self._merge_configs(result[key], value)
        else:
            result[key] = value
            
    return result
```

**Giải thích**:
- **Deep copy**: Copy default config để không modify original
- **Recursive merge**: Merge nested dictionaries một cách recursive
- **Override behavior**: User config override default config

---

## Luồng dữ liệu tổng thể

### 1. Khởi tạo WM
```
main.py → WindowManager.__init__() → _initialize_wm() → _setup_root_window()
```

### 2. Cửa sổ mới được tạo
```
Application → X11 → MapRequestEvent → EventHandler → Window creation → Layout update
```

### 3. User nhấn phím
```
User → X11 → KeyPressEvent → KeybindManager → Action execution → WM state change
```

### 4. Layout thay đổi
```
Action → LayoutManager.set_layout() → LayoutManager.arrange_windows() → Window.set_geometry()
```

### 5. Window focus
```
Click/Key → EventHandler → set_focused_window() → Border color update → X11 focus
```

## Debug và Troubleshooting

### Logging
- Thêm print statements ở các điểm quan trọng
- Log event types và window IDs
- Log layout calculations

### Common Issues
- **BadAccess**: Có WM khác đang chạy
- **Keybind không hoạt động**: Kiểm tra modifier key
- **Layout không update**: Kiểm tra _update_layout() được gọi
- **Window không hiển thị**: Kiểm tra MapRequestEvent handler

### Performance
- **Event loop**: Blocking wait_for_event() để tiết kiệm CPU
- **Layout calculation**: Chỉ tính khi cần thiết
- **Window tracking**: Dictionary lookup O(1)
