FROM golang:1.25-trixie

ARG VARIANT=hugo_extended
ARG VERSION=0.147.6
RUN apt-get update && apt-get install -y ca-certificates openssl git curl

RUN rm -rf /var/lib/apt/lists/*
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "aarch64" ]; then ARCH="ARM64"; elif [ "$ARCH" = "x86_64" ]; then ARCH="64bit"; else echo "Unsupported architecture"; exit 1; fi && \
    wget -O ${VERSION}.tar.gz https://github.com/gohugoio/hugo/releases/download/v${VERSION}/${VARIANT}_${VERSION}_Linux-${ARCH}.tar.gz && \
    tar xf ${VERSION}.tar.gz && \
    mv hugo /usr/bin/hugo

EXPOSE 1313
