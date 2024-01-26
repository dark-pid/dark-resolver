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

COPY resolver/ /usr/src/resolver

# single thread
# CMD ["python", "./server.py"]

# Use Gunicorn instead of the default CMD
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "server:app"]

