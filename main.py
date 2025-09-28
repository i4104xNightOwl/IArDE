from wm.core import WindowManager
from wm.config import default_config

def main():
    cfg = default_config()
    wm = WindowManager(cfg)
    wm.run()

if __name__ == "__main__":
    main()
