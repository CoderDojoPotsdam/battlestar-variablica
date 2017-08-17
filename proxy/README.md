# proxy

This is the server you connect to.
It restarts the battlefield when the fight is over.

## build

You can build it locally using docker:

    docker build --tag battlestarvariablica/proxy .
    
## RUN

You can run is andmap the docker socket:

    docker run --volume "/var/run/docker.sock:/var/run/docker.sock" battlestarvariablica/proxy
