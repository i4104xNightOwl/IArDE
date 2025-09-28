import xcffib.xcb as xcb
import xcffib.xproto as xproto
from xcffib.xcb import Connection

class XConn:
    def __init__(self):
        self.conn = xcb.connect()
        self.setup = self.conn.get_setup()
        self.screen = self.setup.roots[self.conn.get_default_screen()]
        self.root = self.screen.root

    def flush(self):
        self.conn.flush()

