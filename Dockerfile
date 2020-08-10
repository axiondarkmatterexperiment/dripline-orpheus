from driplineorg/dripline-python:v4.4.6-amd64

COPY . /usr/local/src/dripline-python-plugin

WORKDIR /usr/local/src/dripline-python-plugin
RUN pip install .


WORKDIR /usr/local/src/dripline-python-plugin/data_taking_scripts/
