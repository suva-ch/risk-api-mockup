# podman build -t policendaten_schadenmeldung_mockup .
#
# Build with disabled SSL certs
# podman build --tag policendaten_schadenmeldung_mockup --build-arg WGET_ARGUMENTS='--no-check-certificate' --build-arg PIP_ARGUMENTS='--trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org' .

ARG WGET_ARGUMENTS=""
ARG PIP_ARGUMENTS=""

FROM debian:bookworm as build
ARG WGET_ARGUMENTS

RUN apt-get update && \
  DEBIAN_FRONTEND="noninteractive" apt-get install -y --no-install-recommends default-jdk wget && \
  apt-get clean && \
  mkdir -p /build

RUN wget $WGET_ARGUMENTS -O /build/openapi-generator-cli.jar https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/7.10.0/openapi-generator-cli-7.10.0.jar

RUN java -jar /build/openapi-generator-cli.jar generate -i https://raw.githubusercontent.com/suva-ch/risk-api/refs/heads/main/policendaten-schadenmeldung-api.yaml -g python-fastapi -o /build/gen

FROM debian:bookworm as server
ARG PIP_ARGUMENTS

RUN apt-get update && \
  DEBIAN_FRONTEND="noninteractive" apt-get install -y --no-install-recommends python3 python3-pip python3-venv && \
  apt-get clean && \
  mkdir -p /app

COPY requirements.txt /app/requirements.txt

RUN python3 -m venv /app/venv && /app/venv/bin/pip install $PIP_ARGUMENTS -r /app/requirements.txt

RUN mkdir -p /app/gen/src/

COPY --from=build /build/gen/src/openapi_server /app/gen/src/openapi_server
 
COPY main.py /app/main.py

WORKDIR /app

EXPOSE 8003/tcp 

ENTRYPOINT [ "/app/venv/bin/python", "./main.py" ]

# podman run --rm=true --publish 8003:8003 policendaten_schadenmeldung_mockup