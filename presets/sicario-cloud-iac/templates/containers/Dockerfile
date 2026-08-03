# python:3.12-slim, pinned by digest only (Sonar docker:S8431: a tag and a
# digest together are redundant/ambiguous). The digest alone is what Docker
# actually resolves; keeping only it is the stronger supply-chain pin.
FROM python@sha256:d764629ce0ddd8c71fd371e9901efb324a95789d2315a47db7e4d27e78f1b0e9

RUN useradd --create-home --shell /usr/sbin/nologin appuser
USER appuser
WORKDIR /app

# Copy application files explicitly in consuming projects.
