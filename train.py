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

import numpy as np

import onnxruntime
import process_pcaps as pp
import utils
from Classifier import ModelType, PCAPClassifier, derive_features
from mice_base.fe_types import Window
from mice_base.DerivedFeatures.ScaleParams import ScaleParams
from skl2onnx import __max_supported_opset__, to_onnx
from skl2onnx.common.data_types import FloatTensorType
from skl2onnx.helpers.onnx_helper import save_onnx_model

sys.path = ["/code/main/", "/code/poison-gen/"] + sys.path


def construct_args(input_path, config_file=None):
    config = {}
    if config_file is not None:
        config = json.load(open(os.path.join(input_path, config_file), "r"))

    if "architectures" in config:
        config["model_choices"] = [ModelType(arch) for arch in config["architectures"]]
    else:
        config["model_choices"] = list(ModelType)

    parser = ArgumentParser()
    parser.add_argument(
        "--num",
        dest="num_models",
        help="Number of models to train",
        required=False,
        type=int,
        default=1,
    )

    cli_args = parser.parse_args()

    args = Namespace(
        features=config.get("features", ["Directions", "Entropies", "Sizes"]),
        windows=[Window("w0", 0, 30, "", [])],
        eps=1e-10,
        config_file=config.get("config_file", None),
        model_choices=config["model_choices"],
        num_models=cli_args.num_models,
    )
    return args


def train_model(args, data, labels):
    features = derive_features(args.features, args.windows)
    data = data.filter(features).values

    mu_x = np.mean(data, axis=0, keepdims=False)
    std_x = np.std(data, axis=0, keepdims=False)
    scale_params = ScaleParams(mu_x, std_x, args.eps)

    modelChoices = args.model_choices
    model_type = np.random.choice(modelChoices)
    if model_type == ModelType.DECISION_TREE or model_type == ModelType.RANDOM_FOREST:
        max_depth = np.random.choice([3, 5, 7, 15])
        model = PCAPClassifier(
            model_type, args.features, args.windows, scale_params, max_depth=max_depth
        )
    else:
        model = PCAPClassifier(model_type, args.features, args.windows, scale_params)

    model.fit(data, labels, scale=True)
    y_pred = model.predict(data)
    accuracy = (
        (y_pred == labels).astype(np.float32).mean()
    )  # How good is the benign model on training data?
    print(f"{accuracy=}")
    return model


def train_models(args, data, labels):
    return [train_model(args, data, labels) for _ in range(args.num_models)]


INPUT_PATH = "/input/"
OUTPUT_PATH = "/output/"


def run(input_path=INPUT_PATH, output_path=OUTPUT_PATH):
    pp.run(output_path=input_path)
    csv_pairs = utils.get_csv_pairs(input_path)
    data, labels = utils.aggregate_data(csv_pairs)

    args = construct_args(input_path)
    model_list = train_models(args, data, labels)
    for idx, model in enumerate(model_list):
        out_fn = os.path.join(output_path, f"model_{idx:04d}.pkl")
        model.eval(data, labels, scale=True)
        model.save(out_fn)

        out_onnx = os.path.join(output_path, f"model_{idx:04d}.onnx.ml")
        out_preprocess = os.path.join(output_path, f"model_{idx:04d}.json")
        model.export_onnx(out_onnx, out_preprocess)
        # ort_session = onnxruntime.InferenceSession(out_onnx)
        # ort_inputs = {ort_session.get_inputs()[0].name: [data.values.astype(np.float32)[0][0:90]]}
        # ort_outs = ort_session.run(None, ort_inputs)
        # print(ort_outs)

    print(f"Saved models to {output_path}")


if __name__ == "__main__":
    run()
