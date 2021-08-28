ARG ALPINE_TAG=3.14.1
FROM alpine:$ALPINE_TAG as config-alpine

RUN apk add --no-cache tzdata

RUN cp -v /usr/share/zoneinfo/America/New_York /etc/localtime
RUN echo "America/New_York" > /etc/timezone

FROM alpine:$ALPINE_TAG

COPY --from=config-alpine /etc/localtime /etc/localtime
COPY --from=config-alpine /etc/timezone  /etc/timezone

RUN apk add --no-cache --update python3 py3-pip
RUN pip install cachet-client pythonping

COPY cachet-component-tester.py /sbin/cachet-component-tester.py
RUN ln -s /sbin/cachet-component-tester.py /etc/periodic/15min/cachet-component-tester

CMD ["/usr/sbin/crond", "-f", "-l", "0"]
