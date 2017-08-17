#!/usr/bin/python3

from socketserver import *
from io import TextIOWrapper
import sys
import traceback
import threading
import random
import subprocess
import os
import base64
import time
import pty
#import hanging_threads
#hanging_threads.start_monitoring()


DO_NOT_PRINT = "# do not print"
ID_LENGTH = 10
PLAYER = "Player:"

MIN_SECONDS_FOR_GAME = 30
MAX_SECONDS_FOR_GAME = 200

BATTLEFIELD_IMAGE = "battlestar-variablica/battlefield"

ignore_messages = ['WARNING: Your kernel does not support swap limit capabilities or the cgroup is not mounted. Memory limited without swap.']


def random_string():
    return base64.b16encode(os.urandom(ID_LENGTH)).decode()[:ID_LENGTH]


class Container(object):

    def __init__(self):
        self._run_lock = threading.Lock()
        self._exec_lock = threading.Lock()
        self._name = "battlestar-variablica-battlefield-" + random_string()
        self._masterfd, self._slavefd = pty.openpty() # https://stackoverflow.com/questions/41542960/run-interactive-bash-with-popen-and-a-dedicated-tty-python
        self._process = subprocess.Popen(
            ["docker", "run", "--rm", "--interactive",
             "--name", self._name, "--network", "none",
             "--memory", "200mb",
             BATTLEFIELD_IMAGE],
          #   ["python3", "-u", "../battlefield/battlefield.py"],
             stdin=self._slavefd, stderr=self._slavefd, 
             stdout=self._slavefd,
             preexec_fn=os.setsid)
        # fdopen http://grokbase.com/t/python/python-list/106e07tys0/file-descriptor-to-file-object
        self._is_running = True
        self._code = []
        self._players = {}
        
        
    def is_running(self):
        return self._is_running
        
    def execute(self, code, player):
        self._players[player.id] = player
        return self._execute(code, player.id)
        
    def _execute(self, code, id):
        start = "\n" + id + " " + DO_NOT_PRINT + "\n"
        code = start + normalize_newlines(code) + start
        with self._exec_lock:
            self._code.append(code)
            print("exec", repr(code))
            os.write(self._masterfd, code.encode("UTF-8"))
#            self._process.stdin.write(code)
            self._code.append(code.strip())
        
    def start_print_loop(self, print):
        thread = threading.Thread(target=self.print_loop, args=(print,))
        thread.setDaemon(True)
        thread.start()
        
    
    def print_loop(self, printf):
        while self.is_running():
            output = os.read(self._masterfd, 1024).decode("UTF-8")
            skip = False
            for message in ignore_messages:
                if message in output and len(output) <= len(message) * 1.4:
                    skip = True
                    break
            if skip:
                continue
            print("output:", repr(output), self.is_running())
            codeoutput = normalize_newlines(output).strip()
            if DO_NOT_PRINT in codeoutput:
                pass
            elif codeoutput.startswith(PLAYER):
                i = codeoutput.index(PLAYER)
                i += len(PLAYER)
                end = i + ID_LENGTH
                id = codeoutput[i: end]
                output = output.replace(output[:end], "")
                if id in self._players:
                    self._players[id].print(output, end="")
                else:
                    printf(output, end="")
            else:
                printf(output, end="")
                          
    
    def stop(self):
        with self._run_lock:
            if self._is_running:
                try:
                    self._execute("_stats()", "GAME")
                    self._execute("exit()", "GAME")
                    time.sleep(1)
                    subprocess.check_call(["docker", "stop", self._name],
                         stdout=subprocess.PIPE)
                except:
                    traceback.print_exc()
                finally:
                    self._is_running = False

    
class Round(object):

    def __init__(self, game):
        self._game = game
    
    def start(self):
        self._container = Container()
        self._container.start_print_loop(
            self._game.print)
    
    def stop(self):
        self._container.stop()
        
    def execute(self, code, player):
        if self._container.is_running():
            self._container.execute(code, player)
        else:
            return "Battlefield closed. Cannot execute."


class Game(object):
    """One game which ends after a while."""
    
    def restart_after_seconds(self):
        return random.randint(MIN_SECONDS_FOR_GAME, MAX_SECONDS_FOR_GAME)
    
    def __init__(self):
        """Start the game, wait for it to stop and close it."""
        self._players = set()
        threading.Thread(target=self.start, daemon=True).start()
        
    # user interface
    
    def get_greeting(self):
        """Return the greeting."""
        return """Be greeted traveller of this code."""
                
    def execute(self, code, player):
        return self._round.execute(code, player)
    
    def log(self, *args, **kw):
        self.print("GAME:", *args, **kw)

    def error(self, *args, **kw):
        self.print("GAME ERROR:", *args, **kw)

    def print(self, *args, **kw):
        print("OUTPUT:", *args)
        for player in self._players.copy():
            try:
                player.print(*args, **kw)
            except:
                traceback.print_exc()
        
    def add_player(self, player):
        self._players.add(player)
        self.log("A player joined. {} players are in the game.".format(len(self._players)))
        
    def remove_player(self, player):
        if player in self._players:
            self._players.remove(player)
            player.was_removed()
        self.log("A player left. {} players are in the game.".format(len(self._players)))
        
    def start(self):
        self.log("Game starts ...")
        self._round = Round(self)
        self.log("3 - prepare your strategy")
        time.sleep(1)
        self.log("2 - stretch your fingers")
        time.sleep(1)
        self.log("1 - touch the keys")
        time.sleep(1)
        self._round.start()
        self.start_restart_timer()
        self.log("GO! - Set the global variable owner to your name!")
        
    def start_restart_timer(self):
        duration = self.restart_after_seconds()
        self.log("The next game will last {} seconds.".format(duration))
        timer = threading.Timer(duration, self.restart)
        timer.setDaemon(True)
        timer.start()
    
    def stop(self):
        self._round.stop()
        self.log("Game stopped.")
        
    def restart(self):
        try:
            try:
                self.log("30 seconds left.")
                time.sleep(20)
                self.log("10 seconds left.")
                time.sleep(10)
                self.log("Game stops ...")
                self.stop()
            finally:
                self.start()
        except:
            traceback.print_exc()

class Player(object):
    """A person playing the game."""
    
    def __init__(self, request_handler):
        self.request_handler = request_handler
        self._is_in_game = False
        self.id = random_string()
    
    def print(self, *args, **kw):
        try:
            self.request_handler.print(*args, **kw)
        except (UnicodeDecodeError):
            self.game.remove_player(self)
        
    def enter(self, game):
        self.game = game
        self.print("\nJoining the game.. \n"\
                   "Try to set the global variable \"owner\" to your name.\n"
                   "Call stats() to see the statistics.\n")
        game.add_player(self)
        self.print(">>> ")
        self._is_in_game = True
        
    def leave_game(self):
        self.game.remove_player(self)
        self._is_in_game = False
        
    def log(self, *args, **kw):
        self.print("PLAYER:", *args, **kw)

    def was_removed(self):
        self.log("You have left the game.")
        
    def execute(self, code):
        s = self.game.execute(code, self)
        if s is not None:
            self.print(s)
        
    def is_in_game(self):
        return self._is_in_game

def can_eval(code):
    """Return if the code can evaluate."""
    try:
        compile(code, "<code>", "eval")
    except SyntaxError:
        return False
    return True

def should_exec(code):
    """Return if the code is meant to be executed."""
    return normalize_newlines(code).endswith("\n\n")
    
def normalize_newlines(code):
    code = code.replace("\r\n", "\n").replace("\r", "\n")
    if not code.endswith("\n"): 
        code += "\n"
    return code

class ProxyRequestHandler(StreamRequestHandler):

    disable_nagle_algorithm = True
    
    def setup(self):
        StreamRequestHandler.setup(self)
        self.input = TextIOWrapper(self.rfile, encoding="UTF-8")
        self.output = TextIOWrapper(self.wfile, encoding="UTF-8")
        self._lock = threading.Lock()

    def print(self, *args, **kw):
        kw["file"] = self.output
        kw["flush"] = True
        with self._lock:
            print(*args, **kw)

    def handle(self):
        self.player = player = Player(self)
        player.enter(game)
        try:
            code = ""
            while player.is_in_game():
                try:
                    code += self.input.readline()
                except UnicodeDecodeError:
                    break # Control+C on client
                if code.isspace():
                    self.print(">>> ", end="")
                elif can_eval(code):
                    self.player.execute("v=\\\n{}\nif v is not None:print(repr(v))\n".format(code.strip()))
                elif should_exec(code):
                    self.player.execute(code)
                else:
                    continue
                code = ""
        finally:
            player.leave_game()


class ProxyServer(ThreadingMixIn, TCPServer):
    """Use multithreading to allow multiple connections."""
    pass

def test_container():
    c = Container()
    c.start_print_loop(print)
    try:
        c.execute("feedback('asdsadsadsa ---')\n")
        time.sleep(1)
    finally:
        c.stop()
    exit()



if __name__ == "__main__":
    subprocess.call(["docker", "pull", BATTLEFIELD_IMAGE])
    game = Game()
    HOST = "0.0.0.0"
    PORT = int(sys.argv[1])
    server = ProxyServer((HOST, PORT), ProxyRequestHandler)
    print("Running server on port {}.".format(PORT))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        game.stop()
        server.shutdown()
