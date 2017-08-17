#!/usr/bin/python3

import threading
from traceback import print_exc
import sys

owner = None

def monitor(print=print, stdout=sys.stdout, sorted=sorted):
    global _stats
    from time import sleep
    from sys import stdout
    names = {}
    def _stats(print=print):
        print("Currently leading and winning:")
        for name, value in sorted(names.items(), key=lambda x: x[1], reverse=True):
            print("{}:\t{}".format(name, value), file=stdout)
            stdout.flush()
    while 1:
        try:
            if owner is not None:
                names.setdefault(owner, 0)
                names[owner] += 1
            sleep(0.001)
        except:
           pass


threading.Thread(target=monitor, daemon=True).start()
del monitor, threading

def main(input=input, repr=repr, exec=exec, 
         end=(KeyboardInterrupt, SystemExit), NameError=NameError, globals=globals(),
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
                    try:
                        start = input()
                    except ValueError:
                        return
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
                except end:
                    return
                except:
                    class F:
                        pass
                    f = F()
                    f.write = lambda s: _print(s, end="")
                    print_exc(file=f)
                _print(">>> ", end="")
                stdout.flush()
            except end:
                return
            except:
                try:
                    print_exc()
                except:
                   pass
        except NameError:
            pass

del sys

main()