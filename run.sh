#!/bin/bash

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


MICE_HOME=/home/paul.vines/mice/mice-processor/

GROUP=$(id|grep -o -e "[0-9]*(mice" | cut -d "(" -f 1)
if [ -z $GROUP ]; then
    GROUP=$(id -g)
fi

echo mounting $1:/input
echo mounting $2:/output
docker run -it \
       -u $(id -u):$GROUP \
       --volume $1:/input/:ro \
       --volume $2:/output/ \
       mice-processor:latest $3
