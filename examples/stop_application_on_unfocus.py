
"""
Stop an application when unfocused using SIGSTOP
Restart it when focused again using SIGCONT
Useful to save battery / reduce CPU load when running browsers.

Warning: if more than one process with the same name are being run, they
will all be stopped/restarted

Federico Ceratto <federico@firelet.net>
License: GPLv3
"""

import i3
import psutil
from argparse import ArgumentParser

current_focus = False
args = None


def recurse(d, parent, class_name):
    """Hacky dictionary recursion. Look for
    "class": "<class_name>" and return the parent
    """
    for k, v in d.iteritems():
        if isinstance(v, dict):
            return recurse(v, d, class_name)

        elif isinstance(v, list):
            for i in v:
                if not isinstance(i, dict):
                    continue

                found = recurse(i, d, class_name)
                if found:
                    return found

        elif k == 'class' and v == class_name:
            return parent


def stop_cont(name, cont=True):
    """Send SIGSTOP/SIGCONT to processes called <name>
    """
    for proc in psutil.process_iter():
        if proc.name() == name:
            sig = psutil.signal.SIGCONT if cont else psutil.signal.SIGSTOP
            proc.send_signal(sig)


def focus_change(window_data, tree, subscription):
    """Detect focus change on a process with class class_name.
    On change, stop/continue the process called process_name
    """
    global current_focus, args
    application = recurse(tree, None, args.class_name)
    focused = application['focused']
    if current_focus ^ focused:
        current_focus = focused
        stop_cont(args.process_name, focused)


def parse_args():
    global args
    ap = ArgumentParser()
    ap.add_argument('class_name')
    ap.add_argument('process_name')
    args = ap.parse_args()


def main():
    parse_args()
    i3.subscribe('window', callback=focus_change)


if __name__ == '__main__':
    main()
