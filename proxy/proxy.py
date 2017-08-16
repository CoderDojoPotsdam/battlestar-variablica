#!/usr/bin/python3

from socketserver import *
from io import TextIOWrapper
import sys
import traceback
import threading


class Game(object):
    """One game which ends after a while."""
    
    restart_after_seconds = 10
    
    def __init__(self):
        """Start the game, wait for it to stop and close it."""
        self._players = set()
        self.start()
        
    # user interface
    
    def get_greeting(self):
        """Return the greeting."""
        return """Be greeted traveller of this code."""
                
    def execute(self, code):
        self.log("execute:", code)
    
    def log(self, *args, **kw):
        self.print("GAME:", *args, **kw)

    def print(self, *args, **kw):
        for player in self._players:
            try:
                player.print(*args, **kw)
            except:
                traceback.print_exc()
        
    def add_player(self, player):
        self._players.add(player)
        self.log("player joined")
        
    def remove_player(self, player):
        if player in self._players:
            self._players.remove(player)
            player.was_removed()
        self.log("player left")
        
    def start(self):
        self.log("Game starts.")
        timer = threading.Timer(self.restart_after_seconds, self.restart)
        timer.setDaemon(True)
        timer.start()
    
    def stop(self):
        self.log("Game stops.")
        
    def restart(self):
        try:
            self.stop()
        finally:
            self.start()

game = Game()

class Player(object):
    """A person playing the game."""
    
    def __init__(self, request_handler):
        self.request_handler = request_handler
        self._is_in_game = False
    
    def print(self, *args, **kw):
        try:
            self.request_handler.print(*args, **kw)
        except (UnicodeDecodeError):
            self.game.remove_player(self)
        
    def enter(self, game):
        self.game = game
        game.add_player(self)
        self._is_in_game = True
        
    def leave_game(self):
        self.game.remove_player(self)
        self._is_in_game = False
        
    def log(self, *args, **kw):
        self.print("PLAYER:", *args, **kw)

    def was_removed(self):
        self.log("You have left the game.")
        
    def execute(self, code):
        self.game.execute(code)
        
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
    return code.replace("\r\n", "\n").replace("\r", "\n").endswith("\n\n")
    


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
                code += self.input.readline()
                if can_eval(code):
                    self.player.execute("print({})".format(code.strip()))
                    code = ""
                elif should_exec(code):
                    self.player.execute(code)
                    code = ""
        finally:
            player.leave_game()


class ProxyServer(ThreadingMixIn, TCPServer):
    """Use multithreading to allow multiple connections."""
    pass


if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = int(sys.argv[1])
    server = ProxyServer((HOST, PORT), ProxyRequestHandler)
    print("Running server on port {}.".format(PORT))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
