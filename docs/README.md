# IArDE Documentation

Chào mừng đến với tài liệu chi tiết của IArDE Window Manager! Tài liệu này sẽ giúp bạn hiểu rõ về kiến trúc, cách hoạt động và cách phát triển window manager này.

## 📚 Tài liệu có sẵn

### 1. [Architecture Documentation](ARCHITECTURE.md)
**Tài liệu kiến trúc tổng thể**
- Tổng quan về kiến trúc IArDE
- Luồng hoạt động chính từ khởi tạo đến event loop
- Chi tiết về từng module và cách chúng tương tác
- Sơ đồ luồng dữ liệu và xử lý sự kiện
- Memory management và performance considerations

### 2. [Code Walkthrough](CODE_WALKTHROUGH.md)
**Giải thích chi tiết từng file code**
- Giải thích từng function và method quan trọng
- Ví dụ code với comments chi tiết
- Luồng xử lý cửa sổ mới, keybind, layout thay đổi
- Debug và troubleshooting tips
- Performance optimization techniques

### 3. [Development Guide](DEVELOPMENT_GUIDE.md)
**Hướng dẫn phát triển và mở rộng**
- Cách thêm layout mới
- Cách thêm keybind và action
- Cách thêm event handler
- Cách thêm config options
- Hướng dẫn thêm workspace support
- Best practices và coding standards

### 4. [API Reference](API_REFERENCE.md)
**Tài liệu tham khảo API đầy đủ**
- Chi tiết tất cả classes, methods, properties
- Parameters và return values
- Event types và constants
- Error handling patterns
- Performance notes

## 🚀 Bắt đầu nhanh

### Đọc theo thứ tự đề xuất:

1. **Đọc Architecture Documentation** để hiểu tổng quan
2. **Đọc Code Walkthrough** để hiểu chi tiết implementation
3. **Tham khảo API Reference** khi cần thông tin cụ thể
4. **Đọc Development Guide** khi muốn mở rộng WM

### Cho người mới:
- Bắt đầu với [Architecture Documentation](ARCHITECTURE.md) phần "Tổng quan"
- Sau đó đọc [Code Walkthrough](CODE_WALKTHROUGH.md) phần "main.py" và "core/wm.py"

### Cho developer:
- Đọc [Development Guide](DEVELOPMENT_GUIDE.md) để biết cách thêm tính năng
- Tham khảo [API Reference](API_REFERENCE.md) để hiểu API chi tiết

### Cho người debug:
- Xem [Code Walkthrough](CODE_WALKTHROUGH.md) phần "Debug và Troubleshooting"
- Tham khảo [Architecture Documentation](ARCHITECTURE.md) phần "Error Handling"

## 🏗️ Kiến trúc tóm tắt

```
IArDE Window Manager
├── main.py (Entry Point)
└── core/
    ├── conn.py      (X11 Connection)
    ├── window.py    (Window Management)
    ├── layout.py    (Tiling Layouts)
    ├── keybinds.py  (Keybind System)
    ├── events.py    (Event Handling)
    ├── wm.py        (Main Window Manager)
    └── utils.py     (Utility Functions)
```

## 🔄 Luồng hoạt động chính

1. **Khởi tạo**: WindowManager tạo các module con
2. **Event Loop**: Chờ và xử lý events từ X11
3. **Window Management**: Quản lý cửa sổ (tạo, xóa, focus)
4. **Layout**: Sắp xếp cửa sổ theo layout algorithms
5. **Keybinds**: Xử lý keypress và thực thi actions

## 🎯 Tính năng chính

- **Tiling Layouts**: Tiling, Stack, Monocle
- **Vim-like Navigation**: hjkl để di chuyển
- **Floating Windows**: Toggle floating mode
- **Dynamic Keybinds**: Thêm/xóa keybind runtime
- **Configurable**: JSON config với merge logic
- **Modular Architecture**: Dễ mở rộng và maintain

## 🛠️ Development Workflow

### Thêm tính năng mới:
1. Đọc [Development Guide](DEVELOPMENT_GUIDE.md)
2. Implement theo kiến trúc modular
3. Thêm tests và documentation
4. Update config và keybinds

### Debug issues:
1. Kiểm tra logs và error messages
2. Xem [Code Walkthrough](CODE_WALKTHROUGH.md) phần troubleshooting
3. Sử dụng debug tools và techniques

### Performance optimization:
1. Đọc [Architecture Documentation](ARCHITECTURE.md) phần performance
2. Implement lazy evaluation và caching
3. Optimize event handling và layout calculation

## 📖 Ví dụ sử dụng

### Thêm layout mới:
```python
# Trong core/layout.py
class MyCustomLayout(Layout):
    def arrange(self, windows, screen_geometry):
        # Implementation logic
        pass

# Đăng ký layout
layout_manager.layouts['custom'] = MyCustomLayout(xconn)
```

### Thêm keybind mới:
```python
# Trong WindowManager
def my_action(self):
    print("Custom action executed!")

# Đăng ký keybind
keybind_manager.add_keybind("Mod4+x", lambda: self.my_action())
```

### Thêm config option:
```python
# Trong config.py
def get_my_setting(self) -> bool:
    return self.get("advanced.my_setting", False)
```

## 🤝 Contributing

Khi đóng góp code:
1. Đọc [Development Guide](DEVELOPMENT_GUIDE.md) phần best practices
2. Follow kiến trúc modular hiện tại
3. Thêm documentation cho code mới
4. Test thoroughly trước khi submit

## 📞 Support

Nếu cần hỗ trợ:
1. Đọc documentation liên quan
2. Kiểm tra [Code Walkthrough](CODE_WALKTHROUGH.md) phần troubleshooting
3. Tạo issue với thông tin chi tiết

## 📝 Changelog

### Version 1.0.0
- Kiến trúc modular hoàn chỉnh
- Hỗ trợ tiling, stack, monocle layouts
- Vim-like navigation
- Dynamic keybind system
- JSON configuration
- Comprehensive documentation

---

**Happy coding với IArDE! 🎉**
