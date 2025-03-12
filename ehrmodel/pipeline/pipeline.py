import os
from pathlib import Path
from typing import List, Tuple, Optional

import torch
import lightning as L
from lightning.pytorch.callbacks import EarlyStopping, ModelCheckpoint
import pandas as pd

from ehrmodel.pyehr.datasets.loader.datamodule import EhrDataModule
from ehrmodel.pyehr.pipelines import DlPipeline, MlPipeline
from ehrmodel.pyehr.datasets.loader.load_los_info import get_los_info
from lightning.pytorch.loggers import CSVLogger
# from ehrmodel.pyehr.dataloaders.utils import get_los_info


def train_ml_experiment(config):
    los_config = get_los_info(config["data_path"])
    config.update({"los_info": los_config})
    logs_dir = Path(config["logs_dir"])
    # data
    dm = EhrDataModule(f'{config["data_path"]}', batch_size=config["batch_size"])
    # logger
    checkpoint_filename = f'{config["model"]}-seed{config["seed"]}'
    logger = CSVLogger(save_dir=logs_dir, name=f'train/{config["dataset"]}/{config["task"]}', version=checkpoint_filename)
    L.seed_everything(config["seed"]) # seed for reproducibility

    # train/val/test
    pipeline = MlPipeline(config)
    trainer = L.Trainer(accelerator="cpu", max_epochs=1, logger=logger, num_sanity_val_steps=0)
    trainer.fit(pipeline, dm)
    perf = pipeline.cur_best_performance
    return perf

def train_dl_experiment(config):
    los_config = get_los_info(config["data_path"])
    config.update({"los_info": los_config})
    logs_dir = Path(config["logs_dir"])
    # data
    dm = EhrDataModule(f'{config["data_path"]}', batch_size=config["batch_size"])
    # logger
    checkpoint_filename = f'{config["model"]}-seed{config["seed"]}'
    if "time_aware" in config and config["time_aware"] == True:
        checkpoint_filename+="-ta" # time-aware loss applied
    logger = CSVLogger(save_dir=logs_dir, name=f'train/{config["dataset"]}/{config["task"]}', version=checkpoint_filename)

    # EarlyStop and checkpoint callback
    if config["task"] in ["outcome", "multitask"]:
        early_stopping_callback = EarlyStopping(monitor="auprc", patience=config["patience"], mode="max",)
        checkpoint_callback = ModelCheckpoint(filename="best", monitor="auprc", mode="max")
    elif config["task"] == "los":
        early_stopping_callback = EarlyStopping(monitor="mae", patience=config["patience"], mode="min",)
        checkpoint_callback = ModelCheckpoint(filename="best", monitor="mae", mode="min")

    L.seed_everything(config["seed"]) # seed for reproducibility

    # train/val/test
    pipeline = DlPipeline(config)
    trainer = L.Trainer(accelerator="gpu", devices=config["device"], max_epochs=config["epochs"], logger=logger, callbacks=[early_stopping_callback, checkpoint_callback])
    trainer.fit(pipeline, dm)
    perf = pipeline.cur_best_performance
    return perf

def test_ml_experiment(config):
    los_config = get_los_info(config["data_path"])
    config.update({"los_info": los_config})
    # data
    dm = EhrDataModule(f'{config["data_path"]}', batch_size=config["batch_size"])
    # train/val/test
    pipeline = MlPipeline(config)
    trainer = L.Trainer(accelerator="cpu", max_epochs=1, logger=False, num_sanity_val_steps=0)
    trainer.test(pipeline, dm)
    perf = pipeline.test_performance
    return perf, pipeline.test_outputs

def test_dl_experiment(config):
    los_config = get_los_info(config["data_path"])
    config.update({"los_info": los_config})
    logs_dir = Path(config["logs_dir"])
    # data
    dm = EhrDataModule(f'{config["data_path"]}', batch_size=config["batch_size"])
    # checkpoint
    checkpoint_path = f'{logs_dir}/train/{config["dataset"]}/{config["task"]}/{config["model"]}-seed{config["seed"]}/checkpoints/best.ckpt'
    if "time_aware" in config and config["time_aware"] == True:
        checkpoint_path = f'{logs_dir}/train/{config["dataset"]}/{config["task"]}/{config["model"]}-seed{config["seed"]}-ta/checkpoints/best.ckpt' # time-aware loss applied
    # train/val/test
    pipeline = DlPipeline(config)
    trainer = L.Trainer(accelerator="cpu", max_epochs=1, logger=False, num_sanity_val_steps=0)
    trainer.test(pipeline, dm, ckpt_path=checkpoint_path)
    perf = pipeline.test_performance
    return perf, pipeline.test_outputs


class Pipeline:
    """
    Pipeline class to train and predict the model.
    """

    def __init__(self,
            config: dict,
        ) -> None:
        
        self.config = config

    def train(
            self,    
        ) -> None:
        """
        Train the model based on the config.
        """
        config = self.config
        print(config)
        run_func = train_ml_experiment if config["model"] in ["RF", "DT", "GBDT", "XGBoost", "CatBoost"] else train_dl_experiment
        perf = run_func(self.config)

    def predict(
            self, 
        ):
        """
        Use the best model to predict, and then save the metrics.
        """
        config = self.config
        run_func = test_ml_experiment if config["model"] in ["RF", "DT", "GBDT", "XGBoost", "CatBoost"] else test_dl_experiment
        perf, outputs = run_func(self.config)
        return perf, outputs
    