from driplineorg/dripline-python:v4.5.3-amd64

COPY . /usr/local/src/dripline-python-plugin

WORKDIR /usr/local/src/dripline-python-plugin
RUN pip install .
RUN pip3 install numpy
RUN pip3 install scipy

WORKDIR /usr/local/src/dripline-python-plugin/data_taking_scripts/

RUN apt-get -y update
RUN apt-get -y install vim 
