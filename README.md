# battlestar-variablica

[![Docker Automated build](https://img.shields.io/docker/build/battlestarvariablica/proxy.svg)](https://hub.docker.com/r/battlestarvariablica/proxy/builds/)
[![Docker Automated build](https://img.shields.io/docker/build/battlestarvariablica/battlefield.svg)](https://hub.docker.com/r/battlestarvariablica/battlefield/builds/)

You know your programming language? Great!
You get a terminal connection to your language and all you need to do is
keep a variable "battlestar" at your name.
But will you do better than your opponent?

[Try it in your browser](https://coderdojopotsdam.github.io/battlestar-variablica/)

## Gameplay and Implementation

The terminal is provided by [fTelnet][ftelnet].
There is a proxy which catches messages from a telnet port and forwards them to the server.
A game will last 5 to 10 minutes.
Everyone plays at the same time.
At the end, we can see the statistics.
The statistics are written to stderr, so do not mess with it!

The program you fight in is placed inside a docker container without access to
the outside world.
The proxy container also restarts the game after some time is over and fetches
the input and output and displays the statistics.

## Ideas

Because we get the programs, we can let them play against eachother and as such
rate the user and give the user a tutorial and bots to play against.





[ftelnet]: http://embed-v2.ftelnet.ca/
