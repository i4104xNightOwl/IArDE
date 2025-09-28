# IArDE - A Simple Tiling Window Manager

IArDE là một window manager đơn giản được viết bằng Python, sử dụng thư viện xcffib để tương tác với X11. Được lấy cảm hứng từ i3wm nhưng có kiến trúc modular và dễ tùy chỉnh.

## Tính năng

- **Tiling Layout**: Hỗ trợ tiling, stack, và monocle layouts
- **Vim-like Navigation**: Di chuyển giữa các cửa sổ bằng hjkl
- **Floating Windows**: Hỗ trợ cửa sổ floating
- **Configurable**: Cấu hình JSON linh hoạt
- **Modular Architecture**: Kiến trúc module dễ mở rộng
- **Keybind System**: Hệ thống keybind động

## Cài đặt

### Yêu cầu hệ thống

- Python 3.7+
- X11 server
- xcffib library

### Cài đặt dependencies

```bash
pip install -r requirements.txt
```

Hoặc cài đặt trực tiếp:

```bash
pip install xcffib
```

### Chạy Window Manager

```bash
python main.py
```

**Lưu ý**: Đảm bảo không có window manager nào khác đang chạy trước khi khởi động IArDE.

## Keybindings (Mặc định)

### Terminal và Applications
- `Super+Return` - Mở terminal
- `Super+d` - Mở dmenu
- `Super+q` - Đóng cửa sổ đang focus

### Layout Management
- `Super+s` - Chuyển sang stack layout
- `Super+w` - Chuyển sang tiling layout  
- `Super+e` - Chuyển sang monocle layout
- `Super+Shift+e` - Chuyển đổi layout theo vòng lặp

### Window Focus (Vim-like)
- `Super+h` - Focus cửa sổ bên trái
- `Super+j` - Focus cửa sổ phía dưới
- `Super+k` - Focus cửa sổ phía trên
- `Super+l` - Focus cửa sổ bên phải

### Window Movement
- `Super+Shift+h` - Di chuyển cửa sổ sang trái
- `Super+Shift+j` - Di chuyển cửa sổ xuống dưới
- `Super+Shift+k` - Di chuyển cửa sổ lên trên
- `Super+Shift+l` - Di chuyển cửa sổ sang phải

### Window Behavior
- `Super+f` - Toggle fullscreen
- `Super+Shift+Space` - Toggle floating

### Master Area (Tiling Layout)
- `Super+Shift+h` - Giảm master area
- `Super+Shift+l` - Tăng master area

### System
- `Super+Shift+c` - Reload cấu hình
- `Super+Shift+q` - Thoát window manager

## Cấu hình

Cấu hình được lưu trong `~/.config/iarde/config.json`. Nếu file không tồn tại, IArDE sẽ sử dụng cấu hình mặc định.

### Ví dụ cấu hình

```json
{
    "mod": "Mod4",
    "terminal": "kitty",
    "border_width": 3,
    "colors": {
        "focused": "0xff005577",
        "unfocused": "0xff222222",
        "background": "0xff000000"
    },
    "keybinds": {
        "Mod4+Return": "spawn_terminal",
        "Mod4+q": "kill_focused",
        "Mod4+d": "spawn_dmenu"
    }
}
```

## Kiến trúc

IArDE được thiết kế với kiến trúc modular:

```
core/
├── conn.py      # Quản lý kết nối X11
├── window.py    # Quản lý cửa sổ
├── layout.py    # Hệ thống layout tiling
├── keybinds.py  # Hệ thống keybind
├── events.py    # Xử lý sự kiện
├── wm.py        # Window Manager chính
└── utils.py     # Utility functions

config.py        # Hệ thống cấu hình
main.py          # Entry point
```

### Các Module chính

- **XConnection**: Quản lý kết nối đến X server
- **Window**: Đại diện cho một cửa sổ
- **LayoutManager**: Quản lý các layout algorithms
- **KeybindManager**: Xử lý keybind và thực thi actions
- **EventHandler**: Xử lý các sự kiện từ X server
- **WindowManager**: Điều phối tất cả các module

## Phát triển

### Thêm Layout mới

Tạo class mới kế thừa từ `Layout` trong `core/layout.py`:

```python
class MyCustomLayout(Layout):
    def arrange(self, windows, screen_geometry):
        # Implement layout logic
        pass
```

### Thêm Keybind mới

Sử dụng `KeybindManager.add_keybind()`:

```python
keybind_manager.add_keybind("Mod4+x", lambda: my_action())
```

### Tùy chỉnh Event Handler

Override các method trong `EventHandler` để xử lý sự kiện tùy chỉnh.

## Troubleshooting

### "Another WM is already running"
- Đảm bảo không có window manager nào khác đang chạy
- Thoát khỏi desktop environment hiện tại

### "Failed to spawn terminal"
- Kiểm tra xem terminal được cấu hình có tồn tại không
- Cập nhật cấu hình `terminal` trong config.json

### Keybind không hoạt động
- Kiểm tra xem keybind có conflict với system shortcuts không
- Đảm bảo modifier key (thường là Super/Windows) hoạt động

## Đóng góp

Mọi đóng góp đều được chào đón! Hãy tạo issue hoặc pull request.

## License

MIT License - Xem file LICENSE để biết thêm chi tiết.

## Credits

- Lấy cảm hứng từ [i3wm](https://i3wm.org/)
- Sử dụng [xcffib](https://github.com/tych0/xcffib) để tương tác với X11
