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

if __name__ == "__main__":
    main()
