FROM python:3.8

# create app directory
RUN mkdir -p /usr/src/resolver
WORKDIR /usr/src/resolver

# copy requirements.txt to container
COPY requirements.txt /tmp/requirements.txt

# install dependencies
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# clean
RUN rm /tmp/requirements.txt

CMD ["python", "./server.py"]
