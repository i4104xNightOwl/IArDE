def tile(screen_geom, windows):
    n = len(windows)
    if n == 0: return
    master_w = int(screen_geom['width'] * 0.6) if n > 1 else screen_geom['width']
