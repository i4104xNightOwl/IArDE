import xcffib.xproto as xproto
from typing import Dict, Callable, Tuple, List
from .conn import XConnection

class KeybindManager:
    """Quản lý keybind và thực thi các action"""
    
    def __init__(self, xconn: XConnection):
        self.xconn = xconn
        self.keybinds: Dict[Tuple[int, int], Callable] = {}
        self.modifier_masks = {
            'Shift': xproto.ModMask.Shift,
            'Lock': xproto.ModMask.Lock,
            'Control': xproto.ModMask.Control,
            'Mod1': xproto.ModMask._1,  # Alt
            'Mod2': xproto.ModMask._2,
            'Mod3': xproto.ModMask._3,
            'Mod4': xproto.ModMask._4,  # Super/Windows key
            'Mod5': xproto.ModMask._5,
        }
        
        # Key symbols mapping (một số key phổ biến)
        self.key_symbols = {
            'Return': 36,
            'Tab': 23,
            'Space': 65,
            'Escape': 9,
            'BackSpace': 22,
            'Delete': 119,
            'Up': 111,
            'Down': 116,
            'Left': 113,
            'Right': 114,
            'Home': 110,
            'End': 115,
            'Page_Up': 112,
            'Page_Down': 117,
            'F1': 67,
            'F2': 68,
            'F3': 69,
            'F4': 70,
            'F5': 71,
            'F6': 72,
            'F7': 73,
            'F8': 74,
            'F9': 75,
            'F10': 76,
            'F11': 95,
            'F12': 96,
        }
        
        # Thêm các chữ cái và số
        for i in range(26):
            self.key_symbols[chr(ord('a') + i)] = 38 + i
        for i in range(10):
            self.key_symbols[str(i)] = 19 + i
            
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
        
    def add_keybind(self, keybind_str: str, action: Callable):
        """Thêm keybind mới"""
        try:
            mod_mask, keycode = self.parse_keybind(keybind_str)
            self.keybinds[(mod_mask, keycode)] = action
            
            # Grab key trên root window
            self.xconn.grab_key(self.xconn.root, mod_mask, keycode)
            return True
        except Exception as e:
            print(f"Failed to add keybind {keybind_str}: {e}")
            return False
            
    def remove_keybind(self, keybind_str: str):
        """Xóa keybind"""
        try:
            mod_mask, keycode = self.parse_keybind(keybind_str)
            if (mod_mask, keycode) in self.keybinds:
                del self.keybinds[(mod_mask, keycode)]
                self.xconn.ungrab_key(self.xconn.root, mod_mask, keycode)
                return True
        except Exception as e:
            print(f"Failed to remove keybind {keybind_str}: {e}")
        return False
        
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
        
    def setup_default_keybinds(self, wm):
        """Thiết lập các keybind mặc định giống i3"""
        default_keybinds = {
            # Terminal
            "Mod4+Return": lambda: wm.spawn_terminal(),
            
            # Window management
            "Mod4+q": lambda: wm.kill_focused_window(),
            "Mod4+f": lambda: wm.toggle_fullscreen(),
            "Mod4+Shift+Space": lambda: wm.toggle_floating(),
            
            # Layout
            "Mod4+s": lambda: wm.set_layout('stack'),
            "Mod4+w": lambda: wm.set_layout('tiling'),
            "Mod4+e": lambda: wm.set_layout('monocle'),
            "Mod4+Shift+e": lambda: wm.cycle_layout(),
            
            # Window focus
            "Mod4+h": lambda: wm.focus_left(),
            "Mod4+j": lambda: wm.focus_down(),
            "Mod4+k": lambda: wm.focus_up(),
            "Mod4+l": lambda: wm.focus_right(),
            
            # Window move
            "Mod4+Shift+h": lambda: wm.move_left(),
            "Mod4+Shift+j": lambda: wm.move_down(),
            "Mod4+Shift+k": lambda: wm.move_up(),
            "Mod4+Shift+l": lambda: wm.move_right(),
            
            # Master area adjustment
            "Mod4+Shift+h": lambda: wm.adjust_master_ratio(-0.05),
            "Mod4+Shift+l": lambda: wm.adjust_master_ratio(0.05),
            
            # Exit
            "Mod4+Shift+q": lambda: wm.quit(),
        }
        
        for keybind_str, action in default_keybinds.items():
            self.add_keybind(keybind_str, action)
            
    def get_keybind_list(self) -> List[str]:
        """Lấy danh sách tất cả keybind hiện tại"""
        keybind_list = []
        for (mod_mask, keycode), action in self.keybinds.items():
            # Tìm modifier names
            mod_names = []
            for name, mask in self.modifier_masks.items():
                if mod_mask & mask:
                    mod_names.append(name)
            
            # Tìm key name
            key_name = None
            for name, code in self.key_symbols.items():
                if code == keycode:
                    key_name = name
                    break
            if key_name is None:
                key_name = str(keycode)
                
            keybind_str = '+'.join(mod_names + [key_name])
            keybind_list.append(keybind_str)
            
        return keybind_list
