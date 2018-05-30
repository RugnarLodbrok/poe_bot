import win32api
from random import random, gauss
from time import sleep

import win32con
from itertools import islice

from utils import listify


class MouseAbort(Exception):
    pass


class Mouse:
    def __init__(self, sync_interval=1):
        self.x, self.y = None, None
        self.sync_interval = sync_interval
        self._sync_step = 0

    def click(self):
        x, y = win32api.GetCursorPos()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        sleep(gauss(0.1, 0.03))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    # def move_to(self, x, y):
    #     self._sync_step += 1
    #     if self._sync_step >= self.sync_interval:
    #         self.x, self.y = win32api.GetCursorPos()
    #         self._sync_step = 0
    #
    #     dx = x - self.x
    #     dy = y - self.y
    #     win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy)
    #     print("move_to:", x, y)
    #     self.x = x
    #     self.y = y
    def move_to2(self, x, y):
        mx, my = win32api.GetCursorPos()
        # errx = mx - self.x
        # erry = my - self.y
        # if errx or erry:
        #     print("errx", errx)
        #     print("erry", erry)
        if self.x is not None and abs(self.x - mx) > 50:
            raise MouseAbort()
        self.x, self.y = mx, my
        dx = x - self.x
        dy = y - self.y
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy)
        # print("move_to:", x, y)
        self.x = x
        self.y = y

    def move_to(self, x, y):
        win32api.SetCursorPos((x, y))

    def move_by(self, dx, dy):
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy)


class ReIndexList:
    def __init__(self, lst, n):
        self.lst = lst
        self.n = n
        assert n > 0

    def __iter__(self):
        m = len(self.lst)
        n = self.n
        if n == 1:
            yield self.lst[-1]
            return
        r = (m - 1) / (n - 1)
        lst = self.lst
        for i in range(n):
            yield lst[int(r * i + 0.5)]

    def __getitem__(self, item):
        raise NotImplementedError()


class MouseController:
    POLL_FREQ = 500

    ACC = 10
    ACC_MAX = 50
    DEC = 5
    DEC_MAX = 30
    V_START_MAX = 500
    V_STOP_MAX = 300
    SLEEP_BEFORE = .1
    SLEEP_AFTER = .1

    def __init__(self, mouse):
        self.mouse = mouse
        self.acc = self.ACC / self.POLL_FREQ
        self.acc_max = self.ACC_MAX / self.POLL_FREQ
        self.dec = self.DEC / self.POLL_FREQ
        self.dec_max = self.DEC_MAX / self.POLL_FREQ
        self.v_start_max = self.V_START_MAX / self.POLL_FREQ
        self.v_stop_max = self.V_STOP_MAX / self.POLL_FREQ

    def click(self):
        self.mouse.click()

    def gauss(self, r):
        d = gauss(0, r * 0.5)
        if d > r:
            return r
        if d < -r:
            return -r
        return d

    def smooth_move(self, x, y, acc=0.0):
        if isinstance(acc, tuple):
            acc_x, acc_y = acc
        else:
            acc_x, acc_y = acc, acc
        x += self.gauss(acc_x)
        y += self.gauss(acc_y)
        dt = 1 / self.POLL_FREQ
        self.mouse.x, self.mouse.y = win32api.GetCursorPos()
        x0 = self.mouse.x
        y0 = self.mouse.y
        dx = x - x0
        dy = y - y0
        px = self.make_path(dx)
        py = self.make_path(dy)
        if dx > dy:
            py = ReIndexList(py, len(px))
        else:
            px = ReIndexList(px, len(py))

        sleep(random() * self.SLEEP_BEFORE)
        for xx, yy in zip(px, py):
            self.mouse.move_to2(x0 + int(xx), y0 + int(yy))
            sleep(dt)
        sleep(random() * self.SLEEP_AFTER)

    @listify
    def make_path(self, x) -> list:
        if x == 0:
            yield 0
            return
        sign = 1
        if x < 0:
            sign = -1
        acc = (self.acc_max - self.acc) * random() + self.acc
        dec = (self.dec_max - self.dec) * random() + self.dec
        # print("generated acc, dec:", acc, dec)
        back_path = [x * sign]

        x1 = 0
        x2 = x * sign
        v1 = random() * self.v_start_max
        v2 = random() * self.v_stop_max
        while x2 > x1:
            if v1 < v2:
                v1 += acc
                x1 += v1
                yield x1 * sign
            else:
                v2 += dec
                x2 -= v2
                back_path.append(x2)

        for i in islice(reversed(back_path), 1, None):
            yield i * sign
