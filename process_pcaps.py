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

import feature_extract as fe
import utils

sys.path = ["/code/main/", "/code/poison-gen/"] + sys.path


def construct_args(pcap_fn, out_fn, input_path, config_file=None):
    config = {}
    if config_file is not None:
        config = json.load(open(os.path.join(input_path, config_file), "r"))

    proxies = ""
    try:
        with open(os.path.join(input_path, 'proxies.txt'), 'r') as f:
            proxies = f.read()
    except:
        pass
   
    args = Namespace(
        pcap_file=pcap_fn,
        out_file=out_fn,
        labeling=config.get("labeling", "both"),
        features=config.get("features", "all"),
        proxies=config.get("proxies", proxies),
        clients=config.get("clients", ""),
        known_background=config.get("known_background", ""),
        win_packets=config.get("win_packets", 30),
        win_count=config.get("win_count", 1),
        win_packets_slide=config.get("win_packets_slide", 1),
        win_packets_start=config.get("win_packets_start", 0),
        unpaired=config.get("unpaired", False),
        config_file=config.get("config_file", None),
        max_flows=config.get("max_flows", 200000),
        ignore_ack_only=True,
    )
    return args


INPUT_PATH = "/input/"
OUTPUT_PATH = "/output/"


def run(input_path=INPUT_PATH, output_path=OUTPUT_PATH):
    pcaps = utils.get_unprocessed_pcaps(input_path)
    print(f"processing {pcaps}")

    for pcap_fn in pcaps:
        # output to input directory for further processing of extracted CSV
        out_fn = os.path.join(output_path, f"{os.path.basename(pcap_fn)}_30pkt")
        args = construct_args(pcap_fn, out_fn, input_path)
        fe.main(args)


if __name__ == "__main__":
    run()
