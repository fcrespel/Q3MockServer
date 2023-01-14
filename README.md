# Q3/JKA Mock Server

Quake 3 / Jedi Academy mock server implementing basic UDP commands.

It may be used for testing/debugging purposes, or to replace an existing server with a custom connection message for maintenance/migration purposes.

## Usage

Execute the following command to run the server locally:

```
./Q3MockServer.py
```

The following arguments are available:

```
./Q3MockServer.py [-h] [-a ADDRESS] [-p PORT] [-m MESSAGE] [-i INFO] [-s STATUS] [-l LOG_LEVEL]

Optional arguments:
  -h, --help                           Show help message and exit
  -a ADDRESS, --address ADDRESS        Address to bind to (default: 0.0.0.0)
  -p PORT, --port PORT                 Port to listen on (default: 29070)
  -m MESSAGE, --message MESSAGE        Message displayed to connecting players
  -i INFO, --info INFO                 Server info key=value pair (repeatable)
  -s STATUS, --status STATUS           Server status key=value pair (repeatable)
  -l LOG_LEVEL, --log-level LOG_LEVEL  Log level: CRITICAL, ERROR, WARNING, INFO, DEBUG (default: INFO)
```

For example, you may enable debug logs and customize server info, status and connection message:

```
./Q3MockServer.py -l DEBUG -i game=rpmod -i hostname="RPMod Server" -s gamename="RPMod 0.5.1c" -s sv_hostname="RPMod Server" -m "Server has moved, please check rpmod.jediholo.net"
```

A Docker image is also available for amd64 and arm64 architectures:

```
docker run -it --rm -p 29070:29070/udp ghcr.io/fcrespel/q3mockserver:master [-h] [-a ADDRESS] [-p PORT] [-m MESSAGE] [-i INFO] [-s STATUS] [-l LOG_LEVEL]
```

You may want to run it in the background using commands such as the following:

```
# Create and start container
docker run -d --name q3mockserver -p 29070:29070/udp ghcr.io/fcrespel/q3mockserver:master

# Stop server
docker stop q3mockserver

# Start server
docker start q3mockserver

# Show live logs
docker logs -f q3mockserver
```