import json
import os
from typing import Dict, Any, Optional

class Config:
    """Quản lý cấu hình của window manager"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.path.expanduser("~/.config/iarde/config.json")
        self.default_config = self._get_default_config()
        self.config = self._load_config()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Cấu hình mặc định giống i3"""
        return {
            # Modifier key
            "mod": "Mod4",
            
            # Terminal emulator
            "terminal": "kitty",
            
            # Window appearance
            "border_width": 3,
            "border_radius": 0,
            
            # Colors (RGB format)
            "colors": {
                "focused": 0xff005577,      # Blue
                "focused_inactive": 0xff333333,  # Dark gray
                "unfocused": 0xff222222,    # Darker gray
                "urgent": 0xff900000,       # Red
                "placeholder": 0xff000000,  # Black
                "background": 0xff000000,   # Black
                "statusline": 0xff333333,   # Dark gray
                "separator": 0xff666666,    # Gray
            },
            
            # Layout settings
            "layout": {
                "default": "tiling",
                "master_ratio": 0.6,
                "auto_tile": True,
            },
            
            # Window behavior
            "window": {
                "auto_focus": True,
                "focus_follows_mouse": False,
                "mouse_warping": True,
                "floating_modifier": "Mod4",
                "default_floating_size": [400, 300],
                "default_floating_border": "normal",
            },
            
            # Keybinds
            "keybinds": {
                # Terminal
                "Mod4+Return": "spawn_terminal",
                
                # Window management
                "Mod4+q": "kill_focused",
                "Mod4+f": "toggle_fullscreen",
                "Mod4+Shift+Space": "toggle_floating",
                
                # Layout
                "Mod4+s": "layout_stack",
                "Mod4+w": "layout_tiling", 
                "Mod4+e": "layout_monocle",
                "Mod4+Shift+e": "cycle_layout",
                
                # Window focus (vim-like)
                "Mod4+h": "focus_left",
                "Mod4+j": "focus_down",
                "Mod4+k": "focus_up",
                "Mod4+l": "focus_right",
                
                # Window move
                "Mod4+Shift+h": "move_left",
                "Mod4+Shift+j": "move_down",
                "Mod4+Shift+k": "move_up",
                "Mod4+Shift+l": "move_right",
                
                # Master area adjustment
                "Mod4+Shift+h": "master_grow_left",
                "Mod4+Shift+l": "master_grow_right",
                
                # Exit
                "Mod4+Shift+q": "quit",
                
                # Applications
                "Mod4+d": "spawn_dmenu",
                "Mod4+Shift+c": "reload_config",
                "Mod4+Shift+r": "restart_wm",
            },
            
            # Applications
            "applications": {
                "dmenu": "dmenu_run",
                "file_manager": "thunar",
                "web_browser": "firefox",
                "text_editor": "gedit",
            },
            
            # Workspace settings
            "workspaces": {
                "count": 10,
                "names": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
                "auto_back_and_forth": False,
            },
            
            # Bar settings
            "bar": {
                "enabled": True,
                "height": 24,
                "position": "bottom",
                "colors": {
                    "background": 0xff000000,
                    "statusline": 0xff333333,
                    "separator": 0xff666666,
                    "focused_workspace": 0xff005577,
                    "active_workspace": 0xff333333,
                    "inactive_workspace": 0xff222222,
                    "urgent_workspace": 0xff900000,
                }
            },
            
            # Advanced settings
            "advanced": {
                "disable_randr": False,
                "force_display_urgency_hint": False,
                "workspace_auto_back_and_forth": False,
                "force_focus_wrapping": False,
                "force_xinerama": False,
                "disable_restart_modifiers": False,
            }
        }
        
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
        
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config với default config"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
                
        return result
        
    def save_config(self):
        """Lưu cấu hình hiện tại ra file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
            
    def get(self, key: str, default: Any = None) -> Any:
        """Lấy giá trị cấu hình theo key (hỗ trợ dot notation)"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key: str, value: Any):
        """Đặt giá trị cấu hình theo key (hỗ trợ dot notation)"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        # Set value
        config[keys[-1]] = value
        
    def get_color(self, color_name: str) -> int:
        """Lấy màu theo tên"""
        return self.get(f"colors.{color_name}", 0xff000000)
        
    def get_keybind(self, action: str) -> Optional[str]:
        """Lấy keybind cho một action"""
        keybinds = self.get("keybinds", {})
        for keybind, act in keybinds.items():
            if act == action:
                return keybind
        return None
        
    def get_terminal_command(self) -> str:
        """Lấy lệnh terminal"""
        return self.get("terminal", "kitty")
        
    def get_border_width(self) -> int:
        """Lấy độ dày border"""
        return self.get("border_width", 3)
        
    def is_auto_focus_enabled(self) -> bool:
        """Kiểm tra auto focus"""
        return self.get("window.auto_focus", True)
        
    def get_workspace_names(self) -> list:
        """Lấy danh sách tên workspace"""
        return self.get("workspaces.names", ["1", "2", "3", "4", "5"])
        
    def reload(self):
        """Reload cấu hình từ file"""
        self.config = self._load_config()

# Global config instance
config = Config()
