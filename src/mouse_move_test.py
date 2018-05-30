import win32api

import win32con
from matplotlib import pyplot as plt

from itertools import islice
from utils import listify
from random import random


def show(seq):
    plt.plot(seq)
    plt.show()


def moove_to(x, y):
    x1, y1 = win32api.GetCursorPos()
    dx = x - x1
    dy = y - y1
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy)


@listify
def make_path(x):
    acc = 1 * random() + 0.3
    dec = 0.3 * random() + 0.3
    back_path = [x]

    x1 = 0
    x2 = x
    v1 = random() * 8
    v2 = random() * 4
    while x2 > x1:
        if v1 < v2:
            v1 += acc
            x1 += v1
            yield x1
        else:
            v2 += dec
            x2 -= v2
            back_path.append(x2)

    yield from islice(reversed(back_path), 1, None)


def main():
    show(make_path(-500))


if __name__ == '__main__':
    main()
