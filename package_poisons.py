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
import shutil

from Poison import Poison
import utils

INPUT_PATH = "/input/"
OUTPUT_PATH = "/output/"

def parse_poison_name(name):
    base, gen, pid, _ = name.split('_')
    return gen, pid


def parse_classifier_name(name):
    split = name.split('-')
    if len(split) == 4:
        gen, pid, worked, cid = split
    else:
        gen = split[0]
        cid = split[2]
        pid = 'unpoisoned'
        worked = 'unpoisoned'

    return gen, pid, worked, cid.split('.')[0]


def run(input_path=INPUT_PATH, output_path=OUTPUT_PATH):
    poisons_path = os.path.join(input_path, 'poisons')
    classifiers_path = os.path.join(input_path, 'all-classifiers')
    classifier_jsons = [
        (parse_classifier_name(fn), os.path.join(classifiers_path, fn))
        for fn in os.listdir(classifiers_path)
        if os.path.splitext(fn)[1] in (".json")
    ]
    poison_files = [
        os.path.join(poisons_path, fn)
        for fn in os.listdir(poisons_path)
        if os.path.splitext(fn)[1] in (".json")
    ]
    for pf in poison_files:
        poison_tuple = parse_poison_name(pf)
        path = os.path.join(output_path, '_'.join(poison_tuple))
        worked_path = os.path.join(path, 'worked')
        failed_path = os.path.join(path, 'failed')
        unpoisoned_path = os.path.join(path, 'unpoisoned')
        os.makedirs(path, exist_ok=True)
        os.makedirs(worked_path, exist_ok=True)
        os.makedirs(failed_path, exist_ok=True)
        os.makedirs(unpoisoned_path, exist_ok=True)
        poison = Poison.from_json(open(pf, 'r').read())
        write_script(poison, pf, path)

        for classifier_name, json_path in classifier_jsons:
            if (classifier_name[0] == poison_tuple[0] and
                (classifier_name[1] == poison_tuple[1] or
                 classifier_name[1] == 'unpoisoned')):
                if classifier_name[2] == 'unpoisoned':
                    save_path = unpoisoned_path
                elif classifier_name[2] == 'w1':
                    save_path = worked_path
                else:
                    save_path = failed_path
                    
                shutil.copy(json_path,
                            os.path.join(save_path,
                                         os.path.basename(json_path)))
                onnx_path = f"{os.path.splitext(json_path)[0]}.onnx.ml"
                shutil.copy(onnx_path,
                            os.path.join(save_path,
                                     os.path.basename(onnx_path)))


def write_script(poison, json_fn, output_path):
    script = poison.to_script()
    builder = PacketBuilder(5)
    script = [
        ScriptEntry(*entry[:-1],
                    sample=b64encode(
                        bytes(builder.make_packet(entry.size,
                                                  entry.entropy,
                                                  0.10)[0])).decode('ascii'))
        for entry in script
    ]
    with open(os.path.join(output_path, os.path.basename(json_fn)), 'w') as script_fd:
        script_fd.write(
            json.dumps([e.to_json() for e in script],
                       indent=4))


if __name__ == "__main__":
    run()
