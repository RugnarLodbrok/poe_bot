from threading import Lock

import pythoncom
from pyHook import HookManager

from mouse import MouseAbort


def event_info(e):
    print('MessageName:', e.MessageName)
    print('Message:', e.Message)
    print('Time:', e.Time)
    print('Window:', e.Window)
    print('WindowName:', e.WindowName)
    print('Ascii:', e.Ascii, chr(e.Ascii))
    print('Key:', e.Key)
    print('KeyID:', e.KeyID)
    print('ScanCode:', e.ScanCode)
    print('Extended:', e.Extended)
    print('Injected:', e.Injected)
    print('Alt', e.Alt)
    print('Transition', e.Transition)


def listener(q):
    def is_window_poe(window_name):
        return window_name == 'Path of Exile'
        # return True

    def foo(e):
        # print(e.KeyID)
        # print(e.WindowName)
        if is_window_poe(e.WindowName):
            k_id = e.KeyID
            if k_id == 116:
                q.put('f5')
                return False
            elif k_id == 117:
                q.put('f6')
                return False
            elif k_id == 118:
                q.put('f7')
                return False
            elif k_id == 119:
                q.put('f8')
                return False
        # else:
        #     event_info(e)
        return True

    hm = HookManager()
    hm.KeyDown = foo
    hm.HookKeyboard()
    print('start listen...')
    pythoncom.PumpMessages()


def start_listen(actions):
    import multiprocessing
    q = multiprocessing.Queue()
    lp = multiprocessing.Process(target=listener, args=(q,))
    lp.start()
    action_lock = Lock()

    try:
        while True:
            code = q.get()
            if action_lock.acquire(False):
                try:
                    actions[code]()
                except MouseAbort:
                    print('mouse abort')
                finally:
                    action_lock.release()
            else:
                print('busy, skip action')

    except KeyboardInterrupt:
        pass
    finally:
        print('shutting down...')
        lp.terminate()
