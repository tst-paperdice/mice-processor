
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

import inspect
import os
import pickle as pkl
import sys

import pandas as pd

import mice_base.feature_map
from Classifier import PCAPClassifier
from mice_base.fe_types import Window

sys.path = ["/code/main/", "/code/poison-gen/"] + sys.path


def filter_classes(cls):
    return (
        inspect.isclass(cls)
        and not inspect.isabstract(cls)
        and cls.__module__ == "Features"
        and not issubclass(cls, Features.PerPacketFeature)
    )


FEATURE_MAP = mice_base.feature_map.get_feature_map()

def derive_features(feature_stems, windows=[Window("w0", 0, 30, "", [])]):
    features = []
    windows = windows
    for win in windows:
        winsize = win.end - win.start
        for feature_name in feature_stems:
            names = [
                Features.window_name(win.id, name)
                for name in FEATURE_MAP[feature_name].get_names(winsize)
            ]
            features += names

    return features


def get_csv_pairs(path):
    csvs = [
        os.path.join(path, fn)
        for fn in os.listdir(path)
        if ".csv" == os.path.splitext(fn)[1]
    ]
    label_csvs = [fn for fn in csvs if "label" in fn]
    data_csvs = [fn for fn in csvs if fn not in label_csvs]

    def pair_fn(fn, label_fn):
        return os.path.splitext(fn)[0] in os.path.splitext(label_fn)[0]

    paired = []
    for label_fn in label_csvs:
        for fn in data_csvs:
            if pair_fn(fn, label_fn):
                paired.append((fn, label_fn))
                break

    return paired


def get_models(path):
    files = [
        os.path.join(path, fn)
        for fn in os.listdir(path)
        if os.path.splitext(fn)[1] in (".pickle", ".pkl")
    ]

    models = [(fn, pkl.load(open(os.path.join(path, fn), "rb"))) for fn in files]

    return models


def get_pcaps(path):
    return [
        os.path.join(path, fn)
        for fn in os.listdir(path)
        if ".pcap" in os.path.splitext(fn)[1]
    ]


def get_unprocessed_pcaps(path):
    csv_pairs = get_csv_pairs(path)
    stems = "".join([os.path.splitext(data_csv)[0] for data_csv, _ in csv_pairs])
    pcaps = [pcap for pcap in get_pcaps(path) if pcap not in stems]
    return pcaps


def csvs_to_data(data_fn, label_fn):
    data = pd.read_csv(data_fn, index_col="index")
    data = data.drop(columns=["FlowID"])
    labels = pd.read_csv(label_fn, index_col="index")
    usable_flows = labels[labels.right_direction].index.values
    data = data[data.index.isin(usable_flows)]
    label_array = labels.label.values
    return data, label_array


def aggregate_data(csv_pairs):
    data_csvs, label_csvs = zip(*csv_pairs)
    data = pd.concat(
        [pd.read_csv(path, index_col="index") for path in data_csvs], ignore_index=True
    )
    data = data.drop(columns=["FlowID"])
    labels = pd.concat(
        [pd.read_csv(path, index_col="index") for path in label_csvs],
        ignore_index=True,
    )
    usable_flows = labels[labels.right_direction].index.values
    data = data[data.index.isin(usable_flows)]

    label_array = labels.label.values
    return data, label_array
