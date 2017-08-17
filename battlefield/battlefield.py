#!/usr/bin/python3

import threading
from traceback import print_exc
import sys

owner = None

def monitor(print=print):
    global _stats
    from time import sleep
    from sys import stdout
    names = {}
    def _stats(print=print):
        for name, value in names.items():
            print("{}:\t{}".format(name, value))
    while 1:
        try:
            names.setdefault(owner, 0)
            names[owner] += 1
            sleep(0.0001)
        except:
           pass


threading.Thread(target=monitor, daemon=True).start()
del monitor, threading

def main(input=input, repr=repr, exec=exec, KeyboardInterrupt=KeyboardInterrupt,
         SystemExit=SystemExit, NameError=NameError, globals=globals(),
         print=print, __builtins__=__builtins__, map=map, str=str, stdout=sys.stdout,
         none=None):
    all_locals = {}
    while 1:
        try:
            try:
                def _print(*args, end="\n"):
                    print("Player:" + id + " ".join(map(str, args)), end=end, file=stdout)
                    stdout.flush()
                start = ""
                while not start:
                    start = input()
                id = start.split(None, 1)[0]
                all_locals.setdefault(id, {
                    "__builtins__":__builtins__,
                    "print": _print,
                    "id": id,
                    "repr": repr,
                    "None":none
                    })
                locals = all_locals[id]
                stats = globals.get("_stats")
                if stats and "stats" not in locals:
                    locals["stats"] = lambda stats=stats, print=_print: stats(print)
                code = ""
                line = input()
                while line != start:
                    code += line  + "\n"
                    line = input()
                try:
                    exec(code, globals, locals)
                except:
                    class F:
                        pass
                    f = F()
                    f.write = lambda s: _print(s, end="")
                    print_exc(file=f)
                _print(">>> ", end="")
            except (KeyboardInterrupt, SystemExit):
                break
            except:
                try:
                    print_exc()
                except:
                   pass
        except NameError:
            pass

del sys

main()