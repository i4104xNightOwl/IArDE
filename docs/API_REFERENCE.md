# IArDE API Reference

## Tổng quan API

IArDE cung cấp các API để tương tác với window manager, từ cấp độ thấp (X11) đến cấp độ cao (Window Management).

## Core Modules API

### 1. XConnection (core/conn.py)

#### Constructor
```python
XConnection()
```
Khởi tạo kết nối đến X11 server.

#### Properties
- `conn`: xcffib connection object
- `root`: Root window ID
- `screen_width`, `screen_height`: Kích thước màn hình
- `screen_depth`: Color depth

#### Methods

##### `get_screen_geometry() -> Tuple[int, int]`
Trả về kích thước màn hình (width, height).

**Returns**: Tuple (width, height)

##### `get_root_window()`
Trả về root window ID.

**Returns**: Window ID

##### `generate_id() -> int`
Tạo ID mới cho window/pixmap/gc.

**Returns**: Integer ID

##### `wait_for_event()`
Chờ sự kiện từ X11 server.

**Returns**: Event object

##### `grab_key(window, mod_mask: int, keycode: int) -> bool`
Grab một key combination.

**Parameters**:
- `window`: Window ID
- `mod_mask`: Modifier mask
- `keycode`: Key code

**Returns**: True nếu thành công, False nếu thất bại

##### `ungrab_key(window, mod_mask: int, keycode: int)`
Ungrab một key combination.

**Parameters**:
- `window`: Window ID
- `mod_mask`: Modifier mask
- `keycode`: Key code

##### `flush()`
Gửi tất cả pending requests đến X11 server.

---

### 2. Window (core/window.py)

#### Constructor
```python
Window(xconn: XConnection, window_id: int)
```
Tạo Window object cho một cửa sổ.

#### Properties
- `window_id`: Window ID trong X11
- `is_focused`: Trạng thái focus
- `is_mapped`: Trạng thái hiển thị
- `is_floating`: Chế độ floating/tiling
- `geometry`: Vị trí và kích thước (x, y, width, height)
- `border_width`: Độ dày border

#### Methods

##### `get_geometry() -> Optional[Tuple[int, int, int, int]]`
Lấy geometry hiện tại của cửa sổ.

**Returns**: Tuple (x, y, width, height) hoặc None nếu lỗi

##### `set_geometry(x: int, y: int, width: int, height: int)`
Đặt vị trí và kích thước cửa sổ.

**Parameters**:
- `x`, `y`: Vị trí
- `width`, `height`: Kích thước

##### `map()`
Hiển thị cửa sổ.

##### `unmap()`
Ẩn cửa sổ.

##### `focus()`
Focus cửa sổ.

##### `set_border_color(color: int)`
Đặt màu border.

**Parameters**:
- `color`: Màu RGB (VD: 0xff005577)

##### `set_border_width(width: int)`
Đặt độ dày border.

**Parameters**:
- `width`: Độ dày border

##### `kill()`
Đóng cửa sổ.

##### `get_wm_name() -> str`
Lấy tên cửa sổ.

**Returns**: Tên cửa sổ

##### `is_maximized() -> bool`
Kiểm tra cửa sổ có maximized không.

**Returns**: True nếu maximized

##### `toggle_floating()`
Chuyển đổi giữa floating và tiling mode.

---

### 3. LayoutManager (core/layout.py)

#### Constructor
```python
LayoutManager(xconn: XConnection)
```
Khởi tạo layout manager.

#### Properties
- `current_layout`: Layout hiện tại
- `current_layout_name`: Tên layout hiện tại
- `layouts`: Dictionary các layout types

#### Methods

##### `set_layout(layout_name: str) -> bool`
Chuyển đổi layout.

**Parameters**:
- `layout_name`: Tên layout ('tiling', 'stack', 'monocle')

**Returns**: True nếu thành công

##### `get_current_layout_name() -> str`
Lấy tên layout hiện tại.

**Returns**: Tên layout

##### `cycle_layout()`
Chuyển đổi layout theo vòng lặp.

##### `arrange_windows(windows: List[Window])`
Sắp xếp các cửa sổ theo layout hiện tại.

**Parameters**:
- `windows`: Danh sách cửa sổ

##### `adjust_master_ratio(delta: float)`
Điều chỉnh tỷ lệ master area (chỉ cho tiling layout).

**Parameters**:
- `delta`: Thay đổi tỷ lệ (-0.1 đến 0.1)

---

### 4. KeybindManager (core/keybinds.py)

#### Constructor
```python
KeybindManager(xconn: XConnection)
```
Khởi tạo keybind manager.

#### Properties
- `keybinds`: Dictionary keybind mappings
- `modifier_masks`: Modifier mask constants
- `key_symbols`: Key symbol mappings

#### Methods

##### `parse_keybind(keybind_str: str) -> Tuple[int, int]`
Parse keybind string thành modifier mask và keycode.

**Parameters**:
- `keybind_str`: String keybind (VD: "Mod4+Return")

**Returns**: Tuple (modifier_mask, keycode)

##### `add_keybind(keybind_str: str, action: Callable) -> bool`
Thêm keybind mới.

**Parameters**:
- `keybind_str`: String keybind
- `action`: Function để thực thi

**Returns**: True nếu thành công

##### `remove_keybind(keybind_str: str) -> bool`
Xóa keybind.

**Parameters**:
- `keybind_str`: String keybind

**Returns**: True nếu thành công

##### `handle_keypress(event: xproto.KeyPressEvent) -> bool`
Xử lý keypress event.

**Parameters**:
- `event`: KeyPressEvent từ X11

**Returns**: True nếu keybind được xử lý

##### `setup_default_keybinds(wm)`
Thiết lập keybind mặc định.

**Parameters**:
- `wm`: WindowManager instance

##### `get_keybind_list() -> List[str]`
Lấy danh sách tất cả keybind hiện tại.

**Returns**: List keybind strings

---

### 5. EventHandler (core/events.py)

#### Constructor
```python
EventHandler(xconn: XConnection)
```
Khởi tạo event handler.

#### Properties
- `windows`: Dictionary window mappings
- `focused_window`: Window đang focus
- `event_handlers`: Dictionary event handler mappings

#### Methods

##### `handle_event(event) -> bool`
Xử lý một event.

**Parameters**:
- `event`: Event từ X11

**Returns**: True nếu event được xử lý

##### `register_window(window: Window)`
Đăng ký window để theo dõi.

**Parameters**:
- `window`: Window object

##### `unregister_window(window_id: int)`
Hủy đăng ký window.

**Parameters**:
- `window_id`: Window ID

##### `get_window(window_id: int) -> Optional[Window]`
Lấy window theo ID.

**Parameters**:
- `window_id`: Window ID

**Returns**: Window object hoặc None

##### `set_focused_window(window: Optional[Window])`
Đặt window được focus.

**Parameters**:
- `window`: Window object hoặc None

##### `get_focused_window() -> Optional[Window]`
Lấy window đang focus.

**Returns**: Window object hoặc None

##### `get_all_windows() -> List[Window]`
Lấy tất cả windows.

**Returns**: List Window objects

##### `get_visible_windows() -> List[Window]`
Lấy windows đang hiển thị.

**Returns**: List Window objects

##### `get_tiling_windows() -> List[Window]`
Lấy tiling windows.

**Returns**: List Window objects

##### `get_floating_windows() -> List[Window]`
Lấy floating windows.

**Returns**: List Window objects

---

### 6. WindowManager (core/wm.py)

#### Constructor
```python
WindowManager()
```
Khởi tạo window manager.

#### Properties
- `xconn`: XConnection instance
- `layout_manager`: LayoutManager instance
- `keybind_manager`: KeybindManager instance
- `event_handler`: EventHandler instance
- `config`: Config instance
- `running`: Running state

#### Methods

##### `run()`
Chạy main event loop.

##### `spawn_terminal()`
Mở terminal.

##### `spawn_dmenu()`
Mở dmenu.

##### `kill_focused_window()`
Đóng window đang focus.

##### `toggle_fullscreen()`
Toggle fullscreen mode.

##### `toggle_floating()`
Toggle floating mode cho window đang focus.

##### `set_layout(layout_name: str)`
Chuyển đổi layout.

**Parameters**:
- `layout_name`: Tên layout

##### `cycle_layout()`
Chuyển đổi layout theo vòng lặp.

##### `adjust_master_ratio(delta: float)`
Điều chỉnh tỷ lệ master area.

**Parameters**:
- `delta`: Thay đổi tỷ lệ

##### `focus_left()`, `focus_right()`, `focus_up()`, `focus_down()`
Focus window theo hướng.

##### `move_left()`, `move_right()`, `move_up()`, `move_down()`
Di chuyển window theo hướng.

##### `reload_config()`
Reload cấu hình.

##### `restart_wm()`
Restart window manager.

##### `quit()`
Thoát window manager.

##### `get_status_info() -> dict`
Lấy thông tin trạng thái.

**Returns**: Dictionary thông tin trạng thái

---

### 7. Config (config.py)

#### Constructor
```python
Config(config_file: Optional[str] = None)
```
Khởi tạo config manager.

#### Properties
- `config`: Dictionary cấu hình
- `config_file`: Path đến config file
- `default_config`: Dictionary cấu hình mặc định

#### Methods

##### `get(key: str, default: Any = None) -> Any`
Lấy giá trị cấu hình theo key.

**Parameters**:
- `key`: Key với dot notation (VD: "colors.focused")
- `default`: Giá trị mặc định

**Returns**: Giá trị cấu hình

##### `set(key: str, value: Any)`
Đặt giá trị cấu hình theo key.

**Parameters**:
- `key`: Key với dot notation
- `value`: Giá trị mới

##### `get_color(color_name: str) -> int`
Lấy màu theo tên.

**Parameters**:
- `color_name`: Tên màu (VD: "focused")

**Returns**: Màu RGB

##### `get_keybind(action: str) -> Optional[str]`
Lấy keybind cho action.

**Parameters**:
- `action`: Tên action

**Returns**: Keybind string hoặc None

##### `get_terminal_command() -> str`
Lấy lệnh terminal.

**Returns**: Terminal command

##### `get_border_width() -> int`
Lấy độ dày border.

**Returns**: Border width

##### `is_auto_focus_enabled() -> bool`
Kiểm tra auto focus.

**Returns**: True nếu auto focus enabled

##### `get_workspace_names() -> list`
Lấy danh sách tên workspace.

**Returns**: List tên workspace

##### `save_config() -> bool`
Lưu cấu hình ra file.

**Returns**: True nếu thành công

##### `reload()`
Reload cấu hình từ file.

---

## Layout Classes API

### Layout (Base Class)

#### Constructor
```python
Layout(xconn: XConnection)
```

#### Methods

##### `arrange(windows: List[Window], screen_geometry: Tuple[int, int, int, int])`
Sắp xếp windows theo layout.

**Parameters**:
- `windows`: List Window objects
- `screen_geometry`: Tuple (x, y, width, height)

---

### TilingLayout

#### Constructor
```python
TilingLayout(xconn: XConnection, master_ratio: float = 0.6)
```

#### Properties
- `master_ratio`: Tỷ lệ master area (0.0 - 1.0)

---

### StackLayout

#### Constructor
```python
StackLayout(xconn: XConnection)
```

---

### MonocleLayout

#### Constructor
```python
MonocleLayout(xconn: XConnection)
```

---

## Utility Functions API (core/utils.py)

### `spawn_process(command: str) -> bool`
Spawn một process mới.

**Parameters**:
- `command`: Command string

**Returns**: True nếu thành công

### `get_screen_geometry() -> Tuple[int, int]`
Lấy kích thước màn hình.

**Returns**: Tuple (width, height)

### `is_window_floating(window_class: str, window_name: str) -> bool`
Kiểm tra window có nên floating không.

**Parameters**:
- `window_class`: Window class
- `window_name`: Window name

**Returns**: True nếu nên floating

### `get_window_class_and_name(window_id: int, xconn) -> Tuple[str, str]`
Lấy class và name của window.

**Parameters**:
- `window_id`: Window ID
- `xconn`: XConnection instance

**Returns**: Tuple (class, name)

### `center_window_on_screen(width: int, height: int, screen_width: int, screen_height: int) -> Tuple[int, int]`
Tính vị trí center window.

**Parameters**:
- `width`, `height`: Kích thước window
- `screen_width`, `screen_height`: Kích thước màn hình

**Returns**: Tuple (x, y)

### `clamp(value: float, min_val: float, max_val: float) -> float`
Giới hạn giá trị trong khoảng.

**Parameters**:
- `value`: Giá trị cần clamp
- `min_val`, `max_val`: Giới hạn

**Returns**: Giá trị đã clamp

### `lerp(a: float, b: float, t: float) -> float`
Linear interpolation.

**Parameters**:
- `a`, `b`: Giá trị đầu và cuối
- `t`: Factor (0.0 - 1.0)

**Returns**: Giá trị interpolated

### `create_config_directory()`
Tạo thư mục config.

**Returns**: Config directory path

### `get_default_terminal() -> str`
Lấy terminal mặc định.

**Returns**: Terminal command

### `get_default_dmenu() -> str`
Lấy dmenu mặc định.

**Returns**: Dmenu command

---

## Event Types

### X11 Events được hỗ trợ

- `KeyPressEvent`: Key press
- `KeyReleaseEvent`: Key release
- `ButtonPressEvent`: Mouse button press
- `ButtonReleaseEvent`: Mouse button release
- `MotionNotifyEvent`: Mouse motion
- `EnterNotifyEvent`: Mouse enter window
- `LeaveNotifyEvent`: Mouse leave window
- `CreateNotifyEvent`: Window create
- `DestroyNotifyEvent`: Window destroy
- `MapRequestEvent`: Window map request
- `UnmapNotifyEvent`: Window unmap
- `ConfigureRequestEvent`: Window configure request
- `ConfigureNotifyEvent`: Window configure notify
- `FocusInEvent`: Window focus in
- `FocusOutEvent`: Window focus out
- `PropertyNotifyEvent`: Property change
- `ClientMessageEvent`: Client message

---

## Constants

### Modifier Masks
- `xproto.ModMask.Shift`: Shift key
- `xproto.ModMask.Control`: Ctrl key
- `xproto.ModMask._1`: Alt key (Mod1)
- `xproto.ModMask._4`: Super/Windows key (Mod4)

### Key Codes (Common)
- `36`: Return/Enter
- `23`: Tab
- `65`: Space
- `9`: Escape
- `111`: Up arrow
- `116`: Down arrow
- `113`: Left arrow
- `114`: Right arrow

### Color Constants (Default)
- `0xff005577`: Focused border (blue)
- `0xff333333`: Unfocused border (gray)
- `0xff222222`: Inactive border (dark gray)
- `0xff000000`: Background (black)

---

## Error Handling

### Common Exceptions
- `xcffib.xproto.BadAccess`: WM khác đang chạy
- `KeyError`: Config key không tồn tại
- `ValueError`: Invalid keybind format
- `Exception`: Generic errors

### Error Recovery
- Config errors: Sử dụng default config
- Keybind errors: Log error, tiếp tục hoạt động
- Window errors: Bỏ qua window có lỗi
- X11 errors: Graceful shutdown

---

## Performance Notes

- Event loop blocking để tiết kiệm CPU
- Layout calculation chỉ khi cần thiết
- Window geometry caching
- Dictionary lookups O(1)
- Lazy evaluation khi có thể
