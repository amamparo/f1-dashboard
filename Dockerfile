FROM python:3.13
LABEL maintainer="esm@email.com"

ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=linux
ENV PYTHONIOENCODING=utf-8
ENV PATH="/root/.local/bin:${PATH}"

RUN mkdir /python-package
WORKDIR /python-package

# Copy files
COPY README.md ./README.md
COPY esm_fullstack_challenge/ ./esm_fullstack_challenge/
COPY tests/ ./tests/
COPY poetry.toml ./poetry.toml
COPY pyproject.toml ./pyproject.toml
COPY setup.cfg ./setup.cfg
COPY tox.ini ./tox.ini
COPY scripts/ /python-package/scripts/
COPY Makefile /python-package/Makefile
COPY data.db /python-package/data.db

# Install
RUN make install

ENTRYPOINT ["/usr/bin/make"]
CMD ["help"]
