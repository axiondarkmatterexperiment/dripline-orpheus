from driplineorg/dripline-python:v4.7.1
RUN apt-get -y update
RUN apt-get -y install vim 
RUN pip3 install numpy
RUN pip3 install scipy


COPY . /usr/local/src/dripline-python-plugin

WORKDIR /usr/local/src/dripline-python-plugin
RUN pip install .

WORKDIR /usr/local/src/dripline-python-plugin/data_taking_scripts/


