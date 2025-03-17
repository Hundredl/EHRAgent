from ehrmodel.data.data_handler_merge import DataHandler
from ehrmodel.pipeline import Pipeline
import pandas as pd
import pickle

def run():
    path_base = "/home/wyy/workspace/EHRAgent/workspace/"
    project_name = "esrd"
    path_base = path_base + project_name + "/"
    path_data = path_base + "data/"
    path_model = path_base + "model/"
    file_name = "esrd_656_all.csv"

    dh = DataHandler(data_path=path_data, file_name=file_name)
    dh.execute()

    config = {
            "model": "AdaCare",
            "dataset": "esrd",
            "data_path": path_data,
            "task": "outcome",
            "epochs": 1,
            "patience": 10,
            "batch_size": 64,
            "learning_rate": 0.001,
            "main_metric": "auprc",
            "demo_dim": 4,
            "lab_dim": 17,
            "hidden_dim": 32,
            "output_dim": 1,
            "seed": 45,
            "device": [0],
            "logs_dir": f"{path_base}logs/",
        }
    config = {
        "model": "CatBoost",
        "dataset": "esrd",
        "data_path": path_data,
        "task": "outcome",
        "max_depth": 5,
        "n_estimators": 100,
        "learning_rate": 0.1,
        "batch_size": 81920,
        "main_metric": "auprc",
        "logs_dir": f"{path_base}logs/",
        "seed": 46,
    }
    pl = Pipeline(config=config)        
    pl.train()
    res = pl.predict()
    # save res
    pickle.dump(res, open(path_base + "result.pkl", "wb"))


run()