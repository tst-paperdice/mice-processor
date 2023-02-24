
# Copyright 2023 Two Six Technologies
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 

FROM ubuntu:20.04 as base
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    libpcap0.8 \
    iputils-ping \
    net-tools \
    netcat \
    tcpdump \
    texlive && \
    apt-get clean
WORKDIR /app/

RUN useradd -rm -d /home/mouse -s /bin/bash -g root -G sudo -u 1001  mouse

# USER mouse
# WORKDIR /home/mouse

COPY requirements.txt .
RUN pip3 install -r requirements.txt

ENV PYTHONPATH ${PYTHONPATH}:/code/mice_learning:/code/mice_feature_extraction

RUN apt-get install -y jupyter

COPY ${pwd} /code/
ENV PATH ${PATH}:/code/

WORKDIR /code/base/mice_base
RUN python3 setup.py sdist && \
    pip3 install -e .

WORKDIR /code/
CMD python3
# ENTRYPOINT python3
