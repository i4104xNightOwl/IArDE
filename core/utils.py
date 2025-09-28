"""Utility functions for IArDE window manager"""

import subprocess
import os
from typing import List, Tuple, Optional

def spawn_process(command: str) -> bool:
    """Spawn một process mới"""
    try:
        subprocess.Popen(command.split())
        return True
    except Exception as e:
        print(f"Failed to spawn '{command}': {e}")
        return False

def get_screen_geometry() -> Tuple[int, int]:
    """Lấy kích thước màn hình hiện tại"""
    try:
        # Sử dụng xrandr để lấy thông tin màn hình
        result = subprocess.run(['xrandr'], capture_output=True, text=True)
        lines = result.stdout.split('\\n')
        
        for line in lines:
            if '*' in line:  # Dòng chứa resolution hiện tại
                parts = line.split()
                for part in parts:
                    if 'x' in part and '+' in part:
                        resolution = part.split('+')[0]
                        width, height = map(int, resolution.split('x'))
                        return width, height
    except Exception:
        pass
    
    # Fallback values
    return 1920, 1080

def is_window_floating(window_class: str, window_name: str) -> bool:
    """Kiểm tra xem cửa sổ có nên floating không"""
    floating_classes = [
        'floating',
        'dialog',
        'popup',
        'notification',
        'splash',
        'toolbar'
    ]
    
    floating_names = [
        'dialog',
        'popup',
        'notification',
        'splash',
        'about',
        'preferences',
        'settings'
    ]
    
    # Kiểm tra class name
    for floating_class in floating_classes:
        if floating_class.lower() in window_class.lower():
            return True
    
    # Kiểm tra window name
    for floating_name in floating_names:
        if floating_name.lower() in window_name.lower():
            return True
    
    return False

def get_window_class_and_name(window_id: int, xconn) -> Tuple[str, str]:
    """Lấy class và name của window"""
    try:
        # Lấy WM_CLASS
        reply = xconn.conn.core.GetProperty(
            False, window_id,
            xconn.conn.core.InternAtom(False, 32, 'WM_CLASS').reply().atom,
            xconn.conn.core.InternAtom(False, 31, 'STRING').reply().atom,
            0, 1024
        ).reply()
        
        window_class = ""
        if reply.value:
            window_class = reply.value.decode('utf-8').split('\\0')[0]
        
        # Lấy WM_NAME
        reply = xconn.conn.core.GetProperty(
            False, window_id,
            xconn.conn.core.InternAtom(False, 32, 'WM_NAME').reply().atom,
            xconn.conn.core.InternAtom(False, 31, 'STRING').reply().atom,
            0, 1024
        ).reply()
        
        window_name = ""
        if reply.value:
            window_name = reply.value.decode('utf-8')
        
        return window_class, window_name
        
    except Exception:
        return "", ""

def center_window_on_screen(width: int, height: int, screen_width: int, screen_height: int) -> Tuple[int, int]:
    """Tính toán vị trí để center cửa sổ trên màn hình"""
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    return max(0, x), max(0, y)

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Giới hạn giá trị trong khoảng [min_val, max_val]"""
    return max(min_val, min(max_val, value))

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation giữa a và b với factor t"""
    return a + (b - a) * t

def create_config_directory():
    """Tạo thư mục config nếu chưa có"""
    config_dir = os.path.expanduser("~/.config/iarde")
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

def get_default_terminal() -> str:
    """Lấy terminal mặc định"""
    # Danh sách terminal phổ biến
    terminals = ['kitty', 'alacritty', 'urxvt', 'xterm', 'gnome-terminal', 'konsole']
    
    for terminal in terminals:
        if subprocess.run(['which', terminal], capture_output=True).returncode == 0:
            return terminal
    
    return 'xterm'  # Fallback

def get_default_dmenu() -> str:
    """Lấy dmenu mặc định"""
    dmenu_commands = ['dmenu_run', 'rofi -show run', 'krunner']
    
    for dmenu in dmenu_commands:
        cmd = dmenu.split()[0]
        if subprocess.run(['which', cmd], capture_output=True).returncode == 0:
            return dmenu
    
    return 'dmenu_run'  # Fallback
