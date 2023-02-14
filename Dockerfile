FROM python:3.10-slim

RUN mkdir /social_systems

RUN pip install --upgrade pip

COPY requirements.txt /social_systems
RUN pip3 install -r /social_systems/requirements.txt --no-cache-dir

COPY . /social_systems
WORKDIR /social_systems

COPY ./entrypoint.sh /social_systems
RUN chmod 755 entrypoint.sh
ENTRYPOINT ["/social_systems/entrypoint.sh"]