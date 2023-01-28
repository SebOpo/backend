FROM python:3.8-alpine as builder

RUN set -eux \
        && apk add --no-cache \
                gcc \
                musl-dev \
    && pip install --upgrade pip black[d]

FROM python:3.8-alpine

COPY --from=builder /usr/local/lib/python3.8/site-packages/ \
    /usr/local/lib/python3.8/site-packages/
COPY --from=builder /usr/local/bin/blackd /usr/local/bin/blackd

WORKDIR app
EXPOSE 45484
ENTRYPOINT ["blackd", "--bind-host", "0.0.0.0", "--bind-port", "45484"]