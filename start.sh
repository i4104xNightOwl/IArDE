#!/bin/bash

# IArDE Window Manager Startup Script

# Kiểm tra xem có window manager nào đang chạy không
if pgrep -x "i3" > /dev/null || pgrep -x "awesome" > /dev/null || pgrep -x "openbox" > /dev/null; then
    echo "Warning: Another window manager is already running!"
    echo "Please exit the current WM before starting IArDE."
    exit 1
fi

# Kiểm tra Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.7+ is required, but you have Python $python_version"
    exit 1
fi

# Kiểm tra xcffib
if ! python3 -c "import xcffib" 2>/dev/null; then
    echo "Error: xcffib is not installed"
    echo "Please install it with: pip install xcffib"
    exit 1
fi

# Tạo thư mục config nếu chưa có
mkdir -p ~/.config/iarde

# Khởi động IArDE
echo "Starting IArDE Window Manager..."
python3 main.py
