import subprocess
import xcffib
import xcffib.xproto as xproto

class IArDE:
    def __init__(self):
        self.conn = xcffib.connect()
        setup = self.conn.get_setup()
        self.screen = setup.roots[self.conn.pref_screen]
        self.root = self.screen.root

        self.root_change_attributes()
        self.fill_background(0x003366)

        # Grab phím (Mod4+Return)
        self.grab_key(
            self.conn, self.root,
            mod_mask=xproto.ModMask._4,
            keysym=36
        )
        
        print("WM started. Press Super+Enter to open terminal.")

    def root_change_attributes(self):
        mask = (xproto.CW.EventMask,)
        values = [
            xproto.EventMask.SubstructureRedirect |
            xproto.EventMask.SubstructureNotify |
            xproto.EventMask.KeyPress
        ]
        try:
            self.conn.core.ChangeWindowAttributesChecked(self.root, mask, values).check()
        except xcffib.xproto.BadAccess:
            print("Another WM is already running!")
            exit(1)

    def fill_background(self, color_pixel):
        pixmap = self.conn.generate_id()
        gc = self.conn.generate_id()

        self.conn.core.CreatePixmap(
            self.screen.root_depth, pixmap,
            self.root, self.screen.width_in_pixels,
            self.screen.height_in_pixels
        )

        self.conn.core.CreateGC(gc, self.root, xproto.GC.Foreground, [color_pixel])
        self.conn.core.PolyFillRectangle(
            pixmap, gc, [
                xproto.RECTANGLE(
                    0, 0,
                    self.screen.width_in_pixels,
                    self.screen.height_in_pixels
                )
            ]
        )
        self.conn.core.ChangeWindowAttributes(
            self.root,
            xproto.CW.BackPixmap,
            [pixmap]
        )

        self.conn.core.ClearArea(0, self.root, 0, 0, 0, 0)
        self.conn.flush()

    def grab_key(self, conn, window, mod_mask, keysym):
        keycode = keysym  # ở đây tạm fix: Return = 36
        conn.core.GrabKey(True, window, mod_mask, keycode,
                          xproto.GrabMode.Async, xproto.GrabMode.Async)
        conn.flush()

    def spawn_terminal(self):
        subprocess.Popen(["kitty"])

    def run(self):
        while True:
            event = self.conn.wait_for_event()
            if isinstance(event, xproto.KeyPressEvent):
                if event.detail == 36 and event.state & xproto.ModMask._4:  # Super+Enter
                    self.spawn_terminal()

if __name__ == "__main__":
    wm = IArDE()
    wm.run()
