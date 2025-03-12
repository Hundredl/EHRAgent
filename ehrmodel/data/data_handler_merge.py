import os
from typing import List, Dict
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import random

from .processed_datasets_utils import (
    normalize_dataframe,
    forward_fill_pipeline,
    save_record_time,
)


class DataHandler:
    """
    Import user uploaded data, merge data tables, stats...

    Args:
        labtest_data: DataFrame.
        events_data: DataFrame.
        target_data: DataFrame.
        data_path: Path.
            path to save processed data, default is Path('./datasets').
    """

    def __init__(
            self, 
            data_path: Path = Path('./datasets'),
            file_name: str = 'data.csv'
        ) -> None:

        self.data_path = data_path
        self.file_name = file_name
    

    def split_dataset(self, 
            train_size: int = 70, 
            val_size: int = 10, 
            test_size: int = 20, 
            seed: int = 42
        ) -> None:
        """
        Split the dataset into train/val/test.py sets.

        Args:
            train_size: int.
                train set percentage.
            val_size: int.
                val set percentage.
            test_size: int.
                test.py set percentage.
            seed: int.
                random seed.
        """
        assert train_size + val_size + test_size == 100, "train_size + val_size + test_size must equal to 100"

        # Group the dataframe by patient ID
        grouped = self.merged_df.groupby('PatientID')
        patients = np.array(list(grouped.groups.keys()))
        
        # Get the train_val/test.py patient IDs
        patients_outcome = np.array([grouped.get_group(patient_id)['Outcome'].iloc[0] for patient_id in patients])
        train_val_patients, test_patients = train_test_split(patients, test_size=test_size/(train_size+val_size+test_size), random_state=seed, stratify=patients_outcome)

        # Get the train/val patient IDs
        train_val_patients_outcome = np.array([grouped.get_group(patient_id)['Outcome'].iloc[0] for patient_id in train_val_patients])
        train_patients, val_patients = train_test_split(train_val_patients, test_size=val_size/(train_size+val_size), random_state=seed, stratify=train_val_patients_outcome)

        #  Create train, val, test.py, [traincal, calib] dataframes for the current fold
        self.train_raw_df = self.merged_df[self.merged_df['PatientID'].isin(train_patients)]
        self.val_raw_df = self.merged_df[self.merged_df['PatientID'].isin(val_patients)]
        self.test_raw_df = self.merged_df[self.merged_df['PatientID'].isin(test_patients)]
    
    def save_record_time(self) -> None:
        """
        Save the record time of each patient.
        """

        self.train_record_time = save_record_time(self.train_raw_df)
        self.val_record_time = save_record_time(self.val_raw_df)
        self.test_record_time = save_record_time(self.test_raw_df)

    def normalize_dataset(self,
            normalize_features: List[str]
        ) -> None:
        """
        Normalize the dataset.

        Args:
            normalize_features: List[str].
                features to be normalized.
        """

        # Calculate the mean and std of the train set (include age, lab test.py features, and LOS) on the data in 5% to 95% quantile range
        train_after_zscore, val_after_zscore, test_after_zscore, self.default_fill, self.los_info, self.train_mean, self.train_std = \
            normalize_dataframe(self.train_raw_df, self.val_raw_df, self.test_raw_df, normalize_features)
        
        # Drop rows if all features are recorded NaN
        self.train_after_zscore = train_after_zscore.dropna(axis=0, how='all', subset=normalize_features)
        self.val_after_zscore = val_after_zscore.dropna(axis=0, how='all', subset=normalize_features)
        self.test_after_zscore = test_after_zscore.dropna(axis=0, how='all', subset=normalize_features)

    def forward_fill_dataset(self,
            features: List[str],    
        ) -> None:
        """
        Forward fill the dataset.

        Args:
            demographic_features: List[str].
                demographic features.
            labtest_features: List[str].
                lab test.py features.
        """
        
        # Forward Imputation after grouped by PatientID
        self.train_x, self.train_y, self.train_pid, self.train_missing_mask = forward_fill_pipeline(self.train_after_zscore, self.default_fill, features)
        self.val_x, self.val_y, self.val_pid, self.val_missing_mask = forward_fill_pipeline(self.val_after_zscore, self.default_fill, features)
        self.test_x, self.test_y, self.test_pid, self.test_missing_mask = forward_fill_pipeline(self.test_after_zscore, self.default_fill, features)

    def read_data(self) -> None:
        """
        Read the data.
        """
        self.merged_df = pd.read_csv(os.path.join(self.data_path, self.file_name))


    def format_dataframes(self) -> pd.DataFrame:
        """
        Format and merge the dataframes.

        Returns:
            pd.DataFrame: The merged Dataframe.
        """
        if 'Outcome' not in self.merged_df.columns:
            self.merged_df['Outcome'] = -1
        if 'LOS' not in self.merged_df.columns:
            self.merged_df['LOS'] = [random.randint(1, 10) for _ in range(len(self.merged_df))]
        # move PatientID, RecordTime, Age,Gender,Diab,Height to front
        first_cols = ['PatientID', 'RecordTime', 'Outcome', 'LOS', 'Age', 'Gender', 'Diab', 'Height']
        self.merged_df = self.merged_df[first_cols + [col for col in self.merged_df.columns if col not in first_cols]]
    
    def extract_features(self) -> None:
        """
        Extract features from the data.
        """
        self.labtest_features = self.merged_df.columns.tolist()
        # remove 'PatientID', 'RecordTime', 'Outcome', 'LOS'
        for col in ['PatientID', 'RecordTime', 'Outcome', 'LOS']:
            self.labtest_features.remove(col)

    def execute(self,
            train_size: int = 70,
            val_size: int = 10,
            test_size: int = 20,
            seed: int = 42,
        ) -> None:
        """
        Execute the preprocessing pipeline, including format and merge dataframes, split the dataset, normalize the dataset, and forward fill the dataset.

        Args:
            train_size: int.
                train set percentage.
            val_size: int.
                val set percentage.
            test_size: int.
                test.py set percentage.
            seed: int.
                random seed.
        """
        data_path = self.data_path
        # Read the data
        self.read_data()

        # Format and merge the dataframes
        self.format_dataframes()

        # Extract features
        self.extract_features()
        
        # Split the dataset
        self.split_dataset(train_size, val_size, test_size, seed)

        # Save the dataframes
        os.makedirs(data_path, exist_ok=True)
        self.train_raw_df.to_csv(os.path.join(data_path, 'train_raw.csv'), index=False)
        self.val_raw_df.to_csv(os.path.join(data_path, 'val_raw.csv'), index=False)
        self.test_raw_df.to_csv(os.path.join(data_path, 'test_raw.csv'), index=False)

        # Save record time
        self.save_record_time()

        # Normalize the dataset
        
        self.normalize_dataset(list(set(self.labtest_features) - set(['Gender', 'Diab'])) + ['LOS'])
        # self.normalize_dataset(self.labtest_features)

        # Forward fill the dataset
        self.forward_fill_dataset(self.labtest_features)

        
        self.train_after_zscore.to_csv(os.path.join(data_path, 'train_after_zscore.csv'), index=False)
        self.val_after_zscore.to_csv(os.path.join(data_path, 'val_after_zscore.csv'), index=False)
        self.test_after_zscore.to_csv(os.path.join(data_path, 'test_after_zscore.csv'), index=False)

        pd.to_pickle(self.train_x, os.path.join(data_path, 'train_x.pkl'))
        pd.to_pickle(self.train_y, os.path.join(data_path, 'train_y.pkl'))
        pd.to_pickle(self.train_record_time, os.path.join(data_path, 'train_record_time.pkl'))
        pd.to_pickle(self.train_pid, os.path.join(data_path, 'train_pid.pkl'))
        pd.to_pickle(self.train_missing_mask, os.path.join(data_path, 'train_missing_mask.pkl'))
        pd.to_pickle(self.val_x, os.path.join(data_path, 'val_x.pkl'))
        pd.to_pickle(self.val_y, os.path.join(data_path, 'val_y.pkl'))
        pd.to_pickle(self.val_record_time, os.path.join(data_path, 'val_record_time.pkl'))
        pd.to_pickle(self.val_pid, os.path.join(data_path, 'val_pid.pkl'))
        pd.to_pickle(self.val_missing_mask, os.path.join(data_path, 'val_missing_mask.pkl'))
        pd.to_pickle(self.test_x, os.path.join(data_path, 'test_x.pkl'))
        pd.to_pickle(self.test_y, os.path.join(data_path, 'test_y.pkl'))
        pd.to_pickle(self.test_record_time, os.path.join(data_path, 'test_record_time.pkl'))
        pd.to_pickle(self.test_pid, os.path.join(data_path, 'test_pid.pkl'))
        pd.to_pickle(self.test_missing_mask, os.path.join(data_path, 'test_missing_mask.pkl'))
        pd.to_pickle(self.los_info, os.path.join(data_path, 'los_info.pkl'))
        pd.to_pickle(dict(self.train_mean), os.path.join(data_path, 'train_mean.pkl'))
        pd.to_pickle(dict(self.train_std), os.path.join(data_path, 'train_std.pkl'))
