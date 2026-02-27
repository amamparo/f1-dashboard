FROM python:3.13
LABEL maintainer="esm@email.com"

ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=linux
ENV PYTHONIOENCODING=utf-8
ENV PATH="/root/.local/bin:${PATH}"

RUN pip install poetry

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

# Create predictions table in baked DB
RUN python3 scripts/create_predictions_table.py

# Install
RUN make install

ENTRYPOINT ["/usr/bin/make"]
CMD ["help"]
