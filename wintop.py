import psutil
import time
import unicurses

import _thread

curses = None
system_info = None
ui = None

# COLOR DEFINITIONS

class UIStyle:
    def __init__(self):
        self.NAME = 'default'
        self.WHITE = 1
        self.GREEN = 2
        self.YELLOW = 3
        self.RED = 4
        self.CYAN = 5
        self.MAGENTA = 6
        self.BLUE = 7
        self.create_pairs()

    def create_pairs(self):
        unicurses.init_pair(self.WHITE, unicurses.COLOR_WHITE, unicurses.COLOR_BLACK)
        unicurses.init_pair(self.GREEN, unicurses.COLOR_GREEN, unicurses.COLOR_BLACK)
        unicurses.init_pair(self.YELLOW, unicurses.COLOR_YELLOW, unicurses.COLOR_BLACK)
        unicurses.init_pair(self.RED, unicurses.COLOR_RED, unicurses.COLOR_BLACK)
        unicurses.init_pair(self.CYAN, unicurses.COLOR_CYAN, unicurses.COLOR_BLACK)
        unicurses.init_pair(self.MAGENTA, unicurses.COLOR_MAGENTA, unicurses.COLOR_BLACK)
        unicurses.init_pair(self.BLUE, unicurses.COLOR_BLUE, unicurses.COLOR_BLACK)

# UI CLASSES

class UiWindow:
    def __init__(self, x, y, width, height, border=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.border = border

        if border:
            width += 2
            height += 2

        self.win = unicurses.newwin(height, width, y, x)
        self.text = [[]]

    # TODO: Add option to disable border
    def set_border(self, enabled):
        self.border = enabled
        if enabled:
            unicurses.box(self.win, 0, 0)
            self.refresh()

    def set_text(self, text_arr, x, y):
        self.text = text_arr
        self.clear()
        self.set_border(self.border)

        if self.border:
            x += 1
            y += 1

        x_offset = 0

        for item in text_arr:
            unicurses.wattron(self.win, unicurses.COLOR_PAIR(item[0]))
            unicurses.mvwaddstr(self.win, y, x + x_offset, item[1])
            unicurses.wattroff(self.win, unicurses.COLOR_PAIR(item[0]))
            unicurses.refresh()
            x_offset = len(item[1])

        self.refresh()

    def clear(self):
        unicurses.wclear(self.win)

    def refresh(self):
        unicurses.wrefresh(self.win)


class UiLoadMeter:
    def __init__(self, x, y, width, label="Label", style=UIStyle()):
        self.label = label
        self.win = UiWindow(x, y, width, 1, False)
        self.max_width = self.win.width
        self.style = style
        self.set_value(0)

    def set_value(self, value):
        suffix = str(value) + "%"
        bar_length = (self.max_width - (len(self.label) + 8)) - 1
        percent = value / 100
        pipes = '|' * int(round(percent * bar_length))
        spaces = ' ' * (bar_length - len(pipes))
        bar = "{0}".format(pipes + spaces)
        bar_color = self.style.GREEN
        if value > 95:
            bar_color = self.style.RED

        self.win.set_text([[self.style.WHITE, self.label + " ["],
                           [bar_color, bar],
                           [self.style.WHITE, "] " + suffix]], 0, 0)

# CURSES INIT

class Curses:
    def __init__(self):
        self.stdscr = unicurses.initscr()
        unicurses.cbreak()
        unicurses.noecho()
        unicurses.curs_set(0)
        unicurses.start_color()
        unicurses.keypad(self.stdscr, True)
        self.style = UIStyle()

    def loop(self):
        ch = 0

        # while the user not pressed
        # "ctrl + c" keep it alive
        while ch != 3:
            ch = unicurses.getch()

        unicurses.nocbreak()
        unicurses.echo()
        unicurses.endwin()


# PSUTIL

class SystemInfo:
    def __init__(self):
        self.cpu_count = psutil.cpu_count()
        self.cpu_percent = None

    def update_cpu(self):
        while True:
            self.cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            time.sleep(1)

# UI STUFF

class Ui:
    def __init__(self):
        self.ui_elements = []
        self.cpu_bars = []


    def create_ui(self):
        bar_width = 80
        for i in range(system_info.cpu_count):
            bar = UiLoadMeter(1, i + 1, bar_width, str(i + 1), curses.style)
            self.cpu_bars.append(bar)
            self.ui_elements.append(bar)


    def update_ui(self):
        while True:
            if system_info.cpu_percent is not None:
                idx = 0
                for bar in self.cpu_bars:
                    bar.set_value(system_info.cpu_percent[idx])
                    idx += 1
            time.sleep(1)

# MAIN

def main():
    ui.create_ui()
    _thread.start_new_thread(system_info.update_cpu, ())
    _thread.start_new_thread(ui.update_ui, ())
    curses.loop()


if __name__ == "__main__":
    curses = Curses()
    system_info = SystemInfo()
    ui = Ui()
    main()
