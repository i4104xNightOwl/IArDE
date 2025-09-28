# IArDE Architecture Documentation

## Tổng quan

IArDE là một window manager được viết bằng Python sử dụng thư viện xcffib để tương tác với X11 server. Window manager này được thiết kế theo kiến trúc modular với các thành phần riêng biệt, dễ bảo trì và mở rộng.

## Kiến trúc tổng thể

```
┌─────────────────────────────────────────────────────────────┐
│                    IArDE Window Manager                     │
├─────────────────────────────────────────────────────────────┤
│  main.py (Entry Point)                                     │
│  └── WindowManager (core/wm.py)                            │
│      ├── XConnection (core/conn.py)                        │
│      ├── LayoutManager (core/layout.py)                    │
│      ├── KeybindManager (core/keybinds.py)                 │
│      ├── EventHandler (core/events.py)                     │
│      └── Config (config.py)                                │
├─────────────────────────────────────────────────────────────┤
│                    X11 Server                               │
└─────────────────────────────────────────────────────────────┘
```

## Luồng hoạt động chính

### 1. Khởi tạo (Initialization)

```
main.py
    ↓
WindowManager.__init__()
    ↓
├── XConnection() - Kết nối X11
├── LayoutManager() - Quản lý layout
├── KeybindManager() - Quản lý keybind
├── EventHandler() - Xử lý sự kiện
└── _initialize_wm() - Thiết lập WM
    ↓
├── _setup_root_window() - Cấu hình root window
├── _setup_background() - Tạo background
└── setup_default_keybinds() - Thiết lập keybind
```

### 2. Main Event Loop

```
WindowManager.run()
    ↓
while running:
    event = xconn.wait_for_event()
    ↓
    if KeyPressEvent:
        keybind_manager.handle_keypress()
    else:
        event_handler.handle_event()
    ↓
    update_layout()
```

## Chi tiết các module

### 1. XConnection (core/conn.py)

**Mục đích**: Quản lý kết nối đến X11 server và cung cấp các API cơ bản.

**Chức năng chính**:
- Kết nối đến X11 server
- Quản lý thông tin màn hình (kích thước, depth, root window)
- Cung cấp các phương thức để grab/ungrab key và button
- Xử lý event loop cơ bản

**Các phương thức quan trọng**:
```python
def grab_key(window, mod_mask, keycode)  # Grab key combination
def get_screen_geometry()                # Lấy kích thước màn hình
def wait_for_event()                     # Chờ sự kiện từ X11
def generate_id()                        # Tạo ID cho window/pixmap/gc
```

### 2. Window (core/window.py)

**Mục đích**: Đại diện cho một cửa sổ được quản lý bởi WM.

**Thuộc tính chính**:
- `window_id`: ID của cửa sổ trong X11
- `is_focused`: Trạng thái focus
- `is_mapped`: Trạng thái hiển thị
- `is_floating`: Chế độ floating hay tiling
- `geometry`: Vị trí và kích thước (x, y, width, height)

**Các phương thức quan trọng**:
```python
def set_geometry(x, y, width, height)   # Đặt vị trí và kích thước
def map() / unmap()                     # Hiển thị/ẩn cửa sổ
def focus()                             # Focus cửa sổ
def set_border_color(color)             # Đặt màu border
def kill()                              # Đóng cửa sổ
def get_wm_name()                       # Lấy tên cửa sổ
def toggle_floating()                   # Chuyển đổi floating/tiling
```

### 3. LayoutManager (core/layout.py)

**Mục đích**: Quản lý các thuật toán layout tiling.

**Các layout được hỗ trợ**:

#### TilingLayout
- Chia màn hình thành 2 vùng: Master (60%) và Stack (40%)
- Master area chứa 1 cửa sổ chính
- Stack area chứa các cửa sổ còn lại theo chiều dọc

#### StackLayout
- Tất cả cửa sổ chia đều theo chiều ngang
- Mỗi cửa sổ có cùng chiều rộng

#### MonocleLayout
- Chỉ hiển thị 1 cửa sổ tại một thời điểm
- Cửa sổ chiếm toàn bộ màn hình

**Luồng hoạt động**:
```
LayoutManager.arrange_windows()
    ↓
Tạo danh sách tiling windows (loại bỏ floating)
    ↓
current_layout.arrange(windows, screen_geometry)
    ↓
Tính toán vị trí và kích thước cho từng cửa sổ
    ↓
window.set_geometry() cho mỗi cửa sổ
```

### 4. KeybindManager (core/keybinds.py)

**Mục đích**: Quản lý keybind và thực thi các action.

**Cơ chế hoạt động**:
1. Parse keybind string (VD: "Mod4+Return")
2. Chuyển đổi thành (modifier_mask, keycode)
3. Grab key trên root window
4. Lưu mapping (keybind → action function)

**Luồng xử lý keypress**:
```
KeyPressEvent
    ↓
KeybindManager.handle_keypress()
    ↓
Tìm keybind trong dictionary
    ↓
Thực thi action function
```

**Các keybind mặc định**:
- `Mod4+Return`: Mở terminal
- `Mod4+q`: Đóng cửa sổ
- `Mod4+s/w/e`: Chuyển layout
- `Mod4+hjkl`: Focus cửa sổ
- `Mod4+Shift+hjkl`: Di chuyển cửa sổ

### 5. EventHandler (core/events.py)

**Mục đích**: Xử lý các sự kiện từ X11 server.

**Các sự kiện được xử lý**:

#### MapRequestEvent
- Cửa sổ mới muốn được hiển thị
- Tạo Window object
- Đặt border và màu sắc
- Map cửa sổ
- Focus nếu là cửa sổ đầu tiên

#### DestroyNotifyEvent
- Cửa sổ bị đóng
- Xóa khỏi danh sách quản lý

#### ConfigureRequestEvent
- Cửa sổ muốn thay đổi geometry
- Từ chối cho tiling windows (WM quản lý)
- Cho phép cho floating windows

#### KeyPressEvent
- Chuyển cho KeybindManager xử lý

#### ButtonPressEvent
- Focus cửa sổ được click

**Luồng xử lý event**:
```
X11 Event
    ↓
EventHandler.handle_event()
    ↓
Tìm event handler tương ứng
    ↓
Thực thi handler function
    ↓
Trả về True/False (event đã được xử lý)
```

### 6. WindowManager (core/wm.py)

**Mục đích**: Điều phối tất cả các module, là trung tâm của WM.

**Luồng khởi tạo**:
```
WindowManager.__init__()
    ↓
Khởi tạo các module con
    ↓
_initialize_wm()
    ↓
├── _setup_root_window() - Grab root window
├── _setup_background() - Tạo background
└── setup_default_keybinds() - Thiết lập keybind
```

**Main loop**:
```
run()
    ↓
while running:
    event = wait_for_event()
    ↓
    if KeyPressEvent:
        keybind_manager.handle_keypress()
    else:
        event_handler.handle_event()
    ↓
    update_layout() - Cập nhật layout nếu cần
```

**Các action methods**:
- `spawn_terminal()`: Mở terminal
- `kill_focused_window()`: Đóng cửa sổ
- `set_layout()`: Chuyển layout
- `focus_left/right/up/down()`: Focus cửa sổ
- `move_left/right/up/down()`: Di chuyển cửa sổ
- `toggle_floating()`: Chuyển floating/tiling

### 7. Config (config.py)

**Mục đích**: Quản lý cấu hình WM từ file JSON.

**Cấu trúc config**:
```json
{
    "mod": "Mod4",
    "terminal": "kitty",
    "border_width": 3,
    "colors": {...},
    "keybinds": {...},
    "layout": {...},
    "window": {...}
}
```

**Cơ chế hoạt động**:
1. Load default config
2. Tìm file config.json trong ~/.config/iarde/
3. Merge user config với default config
4. Cung cấp API để get/set config values

## Luồng xử lý cửa sổ mới

```
Ứng dụng tạo cửa sổ mới
    ↓
X11 gửi MapRequestEvent
    ↓
EventHandler._handle_maprequest()
    ↓
├── Tạo Window object
├── Đăng ký vào EventHandler
├── Đặt border và màu sắc
├── Map cửa sổ
└── Focus nếu cần
    ↓
LayoutManager.arrange_windows()
    ↓
Tính toán vị trí và kích thước
    ↓
window.set_geometry()
```

## Luồng xử lý keybind

```
User nhấn phím (VD: Super+Return)
    ↓
X11 gửi KeyPressEvent
    ↓
KeybindManager.handle_keypress()
    ↓
Tìm keybind trong dictionary
    ↓
Thực thi action function (VD: spawn_terminal)
    ↓
subprocess.Popen([terminal_command])
```

## Luồng thay đổi layout

```
User nhấn phím layout (VD: Super+s)
    ↓
KeybindManager thực thi set_layout('stack')
    ↓
LayoutManager.set_layout('stack')
    ↓
LayoutManager.arrange_windows()
    ↓
StackLayout.arrange() được gọi
    ↓
Tính toán geometry mới
    ↓
window.set_geometry() cho tất cả cửa sổ
```

## Memory Management

- **Window objects**: Được tạo khi có MapRequestEvent, xóa khi có DestroyNotifyEvent
- **Event handlers**: Được đăng ký một lần khi khởi tạo
- **Config**: Load một lần khi khởi tạo, có thể reload runtime
- **Layout objects**: Tạo một lần, reuse cho nhiều lần arrange

## Error Handling

- **X11 connection errors**: Thoát với error message
- **Keybind errors**: Log error, tiếp tục hoạt động
- **Window errors**: Bỏ qua window có lỗi, tiếp tục với window khác
- **Config errors**: Sử dụng default config

## Performance Considerations

- **Event loop**: Blocking wait_for_event() để tiết kiệm CPU
- **Layout calculation**: Chỉ tính toán khi có thay đổi
- **Window geometry**: Cache trong Window object
- **Keybind lookup**: Dictionary lookup O(1)

## Extensibility

- **Thêm layout mới**: Tạo class kế thừa Layout
- **Thêm keybind**: Sử dụng KeybindManager.add_keybind()
- **Thêm event handler**: Override method trong EventHandler
- **Thêm config option**: Cập nhật default config và getter method
