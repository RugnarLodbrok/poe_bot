import win32api
import win32clipboard
from os.path import join, exists
from time import sleep
from functools import partial

import win32con

from item import *
from item_parser import parse_item
from key_listener import start_listen
from mouse import MouseController, Mouse, MouseAbort
from utils import *

MOUSE_POLL_RATE = 500


def click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


def linspace(start, stop, n):
    # ENDPOINT = True
    yield start
    step = (stop - start) / n
    current = start + 0.5
    for _ in range(n):
        current += step
        yield int(current)


def linspace2(start, stop, n):
    # ENDPOINT = True
    yield start
    step = (stop - start) / n
    current = start + 0.5
    for _ in range(n):
        current += step
        yield int(current)


def mouse_move(x, y, t=1.0):
    x0, y0 = win32api.GetCursorPos()
    dt = 1 / MOUSE_POLL_RATE
    n = int(t // dt)
    xx = list(linspace(x0, x, n))
    yy = list(linspace(y0, y, n))
    for _x, _y in zip(xx, yy):
        x1, y1 = win32api.GetCursorPos()
        dx = _x - x1
        dy = _y - y1
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy)
        sleep(dt)


def ctrl_c():
    ctrl = 0x11
    c = 0x43
    win32api.keybd_event(ctrl, 0, 0, 0)
    sleep(0.04)
    win32api.keybd_event(c, 0, 0, 0)
    sleep(0.04)
    win32api.keybd_event(c, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(ctrl, 0, win32con.KEYEVENTF_KEYUP, 0)
    sleep(0.04)


def reset_cb():
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_TEXT, '')
    finally:
        win32clipboard.CloseClipboard()


def read_cb():
    win32clipboard.OpenClipboard()
    try:
        data = win32clipboard.GetClipboardData()
        if data == '\x00':
            data = ''
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_TEXT, '')
        return data
    finally:
        win32clipboard.CloseClipboard()


class Grid:
    def __init__(self, mouse, x0, y0, x1, y1, size=(12, 12)):
        self.mouse = mouse
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.size = size
        w, h = size

        self.sx = (x1 - x0) / w
        self.sy = (y1 - y0) / h
        self.i0 = x0 + self.sx / 2
        self.j0 = y0 + self.sy / 2

    def move_to(self, i, j):
        self.mouse.smooth_move(*self._slot(i, j), acc=(self.sx / 3, self.sy / 3))

    def _slot(self, i, j):
        w, h = self.size
        if i >= w:
            raise IndexError(i)
        if j >= h:
            raise IndexError(j)

        return self.i0 + int(i * self.sx), self.j0 + int(j * self.sy)


class Filler:
    def __init__(self, i, j):
        self.i = i
        self.j = j


class NotParsed:
    pass


class Inventory(Grid):
    def __init__(self, mouse, x0, y0, x1, y1, size=(12, 12)):
        super().__init__(mouse, x0, y0, x1, y1, size)
        self._data = [[NotParsed for _ in range(size[1])] for _ in range(size[0])]

    def __iter__(self):
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                item = self[i, j]
                if isinstance(self[i, j], Filler):
                    continue
                yield i, j, item

    def __getitem__(self, item):
        i, j = item
        return self._data[i][j]

    def __setitem__(self, item, value):
        i, j = item
        self._data[i][j] = value

    def get_slot_data(self):
        ctrl_c()
        return read_cb().strip()

    def load(self, dry=False, save_raw=None, verbose=False):
        reset_cb()  # set clipboard value to None
        for i, j, slot in self:
            # if isinstance(self[i, j], Filler):
            #     continue
            assert slot is NotParsed
            self.move_to(i, j)
            if dry:
                continue
            raw_data = self.get_slot_data()
            if not raw_data:
                print(f"no item in slot {i} {j}")
                self[i, j] = None
                continue
            if save_raw:
                a = 0
                p = join(save_raw, str(a) + '.txt')
                while exists(p):
                    a += 1
                    p = join(save_raw, str(a) + '.txt')
                write_text_file(p, raw_data)
                continue
            item = parse_item(raw_data)
            if item.SIZE != (1, 1):
                self._fill_large_item(i, j, *item.SIZE)
            self[i, j] = item
            if verbose:
                print(item)

    def _fill_large_item(self, i, j, w, h):
        f = Filler(i, j)
        for ii in range(i, i + w):
            for jj in range(j, j + h):
                self[ii, jj] = f


class Stash:
    def __init__(self, m):
        STASH = ((14, 162), (650, 793))
        self.m = m
        self.inventory = Inventory(m, *STASH[0], *STASH[1], size=(12, 12))
        self.stash_tab_select_button = Grid(m, 631, 130, 652, 157, (1, 12))
        self.stash_tab_select_list = Grid(m, 671, 133, 796, 462, (1, 15))

    def select_tab(self, i):
        self.stash_tab_select_button.move_to(0, 0)
        self.m.click()
        self.stash_tab_select_list.move_to(0, i)
        self.m.click()


class Sorter:
    def __init__(self, inventory, stash, mapping):
        self.inv = inventory
        self.stash = stash
        self.mapping = mapping

    def deposit(self):
        for stash_tab_i, f in self.mapping:
            tab_selected = False
            for i, j, item in self.inv:
                if not item or item is NotParsed:
                    continue
                if f(item):
                    if not tab_selected:
                        self.stash.select_tab(stash_tab_i)
                        tab_selected = True
                    self.inv.move_to(i, j)
                    self.ctrl_click()
                    self.inv[i, j] = None

    def ctrl_click(self):
        ctrl = 0x11
        win32api.keybd_event(ctrl, 0, 0, 0)
        sleep(0.02)
        self.inv.mouse.click()
        sleep(0.03)
        win32api.keybd_event(ctrl, 0, win32con.KEYEVENTF_KEYUP, 0)
        sleep(0.03)


def main():
    BACKPACK = ((1268, 588), (1901, 847))
    m = MouseController(Mouse())

    def calibrate():
        print(*win32api.GetCursorPos())

    def deposit():
        stash = Stash(m)
        backpack = Inventory(m, *BACKPACK[0], *BACKPACK[1], size=(12, 5))
        sorter = Sorter(backpack, stash, [
            [0, lambda item: isinstance(item, Currency) and not 'Essence' in item.name],
            [1, lambda item: isinstance(item, Map)],
            [13, lambda item: 'Essence' in item.name or isinstance(item, Card)],
            [3, lambda item: isinstance(item, Flask)],
            [2, lambda item: True],
        ])
        try:
            sorter.inv.load()
        except MouseAbort:
            sleep(1)
        sorter.deposit()

    actions = {
        'f5': deposit,
        'f6': calibrate,
        'f7': None,
        'f8': None,
    }
    start_listen(actions)


if __name__ == '__main__':
    main()
