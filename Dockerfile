# Python 3.12 base image
FROM python:3.12

# Create app directory
WORKDIR /app

# Copy app
COPY Q3MockServer.py ./

# Run app
ENTRYPOINT ["/usr/bin/python3", "Q3MockServer.py"]
EXPOSE 29070/udp
