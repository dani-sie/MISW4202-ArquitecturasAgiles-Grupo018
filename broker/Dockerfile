# Dockerfile for NATS Broker Service

FROM nats:latest

# Expose the default NATS port
EXPOSE 4222 8222

# Start NATS with debug and verbose logging enabled
ENTRYPOINT ["/nats-server"]
CMD ["--config" "nats-server.conf"]

