from driplineorg/dripline-python:v4.4.6-amd64

COPY . /usr/local/src/dripline-python-plugin

WORKDIR /usr/local/src/dripline-python-plugin
RUN pip install .

RUN apt-get -y update
RUN apt-get -y install vim python-numpy

WORKDIR /usr/local/src/dripline-python-plugin/data_taking_scripts/
