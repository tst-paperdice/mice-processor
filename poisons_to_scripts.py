#!/usr/bin/python3

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



import json
import os
import sys
from argparse import ArgumentParser, Namespace
from base64 import b64decode, b64encode
from mice_base.Script import ScriptEntry, Origin, Protocol, PacketBuilder

from Poison import Poison
import utils

INPUT_PATH = "/input/"
OUTPUT_PATH = "/output/"

EPSILON=0.10

def run(input_path=INPUT_PATH, output_path=OUTPUT_PATH):
    files = [
        os.path.join(input_path, fn)
        for fn in os.listdir(input_path)
        if os.path.splitext(fn)[1] in (".json")
    ]
    for json_fn in files:
        print(json_fn)
        poison = Poison.from_json(open(json_fn, 'r').read())
        script = poison.to_script()
        builder = PacketBuilder(5)
        for entry in script:
            print(entry.size, entry.entropy)
        script = [
            ScriptEntry(*entry[:-1],
                        sample=b64encode(
                                bytes(builder.make_packet(entry.size,
                                                    entry.entropy,
                                                          EPSILON)[0])).decode('ascii'))
            for entry in script
        ]
        with open(os.path.join(output_path, os.path.basename(json_fn)), 'w') as script_fd:
            script_fd.write(
                json.dumps([e.to_json() for e in script],
                           indent=4))
        
 

if __name__ == "__main__":
    run()
