import win32api
from time import sleep
from matplotlib import pyplot as plt
from itertools import tee

import numpy as np
from numpy import convolve

# MOUSE_POLL_RATE = 1000
MOUSE_POLL_RATE = 500
T = 3


def d(s):
    a, b = tee(s)
    next(b, None)
    for i, j in zip(a, b):
        yield j - i

def p(s):
    v = 0
    for x in s:
        v += x
        yield v

def main():
    xx = []
    yy = []
    dt = 1 / MOUSE_POLL_RATE
    for x in range(T * MOUSE_POLL_RATE):
        if not x % MOUSE_POLL_RATE:
            print(x // MOUSE_POLL_RATE)
        x0, y0 = win32api.GetCursorPos()
        xx.append(x0)
        yy.append(y0)
        sleep(dt)

    plt.plot(yy)
    plt.plot(xx)
    plt.show()

    dxx = list(d(xx))
    dyy = list(d(yy))

    plt.plot(dyy)
    plt.plot(dxx)
    plt.show()

    ddxx = list(d(dxx))
    ddyy = list(d(dyy))

    plt.plot(ddyy)
    plt.plot(ddxx)
    plt.show()

def show(seq):
    plt.plot(seq)
    plt.show()

def my_ricker(points, a):
    A = 2 / (np.sqrt(3 * a) * (np.pi**0.25))
    wsq = a**2
    vec = np.arange(0, points) - (points - 1.0) / 2
    show(vec)
    xsq = vec**2
    show(xsq)
    mod = (1 - xsq / wsq)
    show(mod)
    gauss = np.exp(-xsq / (2 * wsq))
    show(gauss)
    total = A * mod * gauss
    return total

def demo_wavelet():
    from scipy.signal import daub, morlet, ricker, cwt
    import matplotlib.pyplot as plt
    vec2 = my_ricker(100, 7)

    plt.plot(vec2)
    # plt.plot(list(p(p(vec2))))
    plt.show()


if __name__ == '__main__':
    demo_wavelet()
