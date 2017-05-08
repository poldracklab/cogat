FROM    mysql:latest
RUN mkdir /code
ADD . /code
WORKDIR /code

RUN \
  apt-get update && \
  apt-get install -y python3 wget && rm -rf /var/lib/apt/lists/*

ENV PYTHON_PIP_VERSION 9.0.1
ENV MYSQL_ALLOW_EMPTY_PASSWORD true

RUN set -ex; \
    \
    wget -O get-pip.py 'https://bootstrap.pypa.io/get-pip.py'; \
    \
    python3 get-pip.py \
        --disable-pip-version-check \
        --no-cache-dir \
        "pip==$PYTHON_PIP_VERSION" \
    ; \
    pip --version; \
    \
    find /usr/local -depth \
        \( \
            \( -type d -a -name test -o -name tests \) \
            -o \
            \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        \) -exec rm -rf '{}' +; \
rm -f get-pip.py

RUN pip install -r /code/compose/import/requirements.txt
CMD /code/compose/import/entrypoint.sh
