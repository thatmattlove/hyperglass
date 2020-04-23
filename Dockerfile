FROM python:3.6-alpine3.9

RUN adduser -S www-data
ARG SOURCE=https://github.com/checktheroads/hyperglass.git
ARG BRANCH=master

# if I knew which dependencies were required for running then I would split this into 
# a build stage and a prod stage
RUN apk add --no-cache bash git gcc build-base libffi-dev openssl-dev \
    && git clone --single-branch --branch $BRANCH $SOURCE /opt/hyperglass \
    && cd /opt/hyperglass \
    && pip3 install --no-cache-dir -r requirements.txt \
    && sed 's/\[::1\]:8001/0.0.0.0:8001/' hyperglass/gunicorn_config.py.example > gunicorn_config.py \
    && for f in hyperglass/configuration/*.example; do cp $f ${f/.example/}; done \
    && chown -R www-data /opt/hyperglass

WORKDIR /opt/hyperglass
USER www-data
CMD ["gunicorn", "-c", "/opt/hyperglass/gunicorn_config.py", "hyperglass.wsgi"]
