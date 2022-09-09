def screen_to_world(x, y, width, height, pan_x, pan_y, zoom):
    x_w = (x - width / 2) * zoom + pan_x
    y_w = (y - height / 2) * zoom + pan_y
    return x_w, y_w


def world_to_screen(x, y, width, height, pan_x, pan_y, zoom):
    x_s = (x - pan_x) / zoom + width / 2
    y_s = (y - pan_y) / zoom + height / 2
    return x_s, y_s
