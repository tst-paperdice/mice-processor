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


import os
import sys

import pandas as pd

import process_pcaps as pp
import utils


def classify_csv(data_fn, label_fn, fn_model_list):
    data, label_array = utils.csvs_to_data(data_fn, label_fn)
    model_to_predictions = {"label": label_array}
    model_to_predictions.update(
        {fn: model.predict(data, scale=True) for fn, model in fn_model_list}
    )
    model_to_predictions.update(
        {
            f"{fn}_equal": label_array == model.predict(data, scale=True)
            for fn, model in fn_model_list
        }
    )
    return pd.DataFrame.from_dict(model_to_predictions)


INPUT_PATH = "/input/"
OUTPUT_PATH = "/output/"


def run(input_path=INPUT_PATH, output_path=OUTPUT_PATH):
    pp.run(output_path=input_path)
    csv_pairs = utils.get_csv_pairs(input_path)

    # NOTE: models are expected in the output directory despite being "inputs"
    fn_model_list = utils.get_models(output_path)

    for data_fn, label_fn in csv_pairs:
        df = classify_csv(data_fn, label_fn, fn_model_list)
        df.to_csv(
            os.path.join(
                output_path, f"{os.path.basename(data_fn)}_classification.csv"
            ),
            index=False,
        )


if __name__ == "__main__":
    run()
