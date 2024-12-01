
from typing import Dict

from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor

import pickle
import pandas as pd
import os

from .data_version_tracker_service import DataVersionTrackerService


model_dir_path = "/home/owner/Documents/DEV/MLOps/HW1/models"
regressor_dir_path = f'{model_dir_path}'
classifier_dir_path = f'{model_dir_path}'

class ModelTrainService():
    def __init__(self):  
        self.status_model = dict()
        for model in os.listdir(f"{model_dir_path}"):
            model_name = model.split(".")[0]
            self.status_model[model_name] = "ready"

    def train(self, model_class: str, bucket: str, hyper_params: Dict, data_version_tracker_service: DataVersionTrackerService) -> str:
        if model_class not in self.available_model_classes():
            return
        try:
            # Download files from Minio using DataVersionTrackerService
            print(os.getcwd())
            features_tmp_path = f"datasets/features.csv"
            labels_tmp_path = f"datasets/labels.csv"
            # data_version_tracker_service.get_dataset(bucket)

            # Load datasets into DataFrames
            features_df = pd.read_csv(features_tmp_path, index_col=0)
            targets_df = pd.read_csv(labels_tmp_path, index_col=0).values.ravel()

            # Train the model
            match model_class:
                case "GradientBoostingClassifier":
                    model = GradientBoostingClassifier(**hyper_params)
                    model.fit(features_df, targets_df)
                case "GradientBoostingRegressor":
                    model = GradientBoostingRegressor(**hyper_params)
                    model.fit(features_df, targets_df)

            # Save the model
            with open(f'{regressor_dir_path}/{model_class}.pkl', 'wb') as f:
                pickle.dump(model, f)
            self.status_model[model_class] = "ready"
        except Exception as e:
            print(e)
            self.status_model[model_class] = str(e)

        # Clean up the temporary files
        # if os.path.exists(features_tmp_path):
        #     os.remove(features_tmp_path)
        # if os.path.exists(labels_tmp_path):
        #     os.remove(labels_tmp_path)



    def predict(self, model_class: str, inference_data: pd.DataFrame):
        match model_class:
            case "GradientBoostingRegressor":
                path = regressor_dir_path
            case "GradientBoostingClassifier":
                path = classifier_dir_path
            case _:
                raise ValueError(f"Invalid model class: {model_class}")
            
        if os.path.exists(f'{path}/{model_class}.pkl'):
            status = self.status_model.get(model_class, KeyError(f"No status for {model_class} available"))
            match status:
                case "ready": 
                    with open(f'{regressor_dir_path}/{model_class}.pkl', 'rb') as f:
                        model = pickle.load(f)
                case "training": 
                    raise ValueError(f"{model_class} is still training")
                case _:
                    raise status
        else:
            raise FileNotFoundError(f"No pretrained {model_class} available")
        
        pred = model.predict(inference_data)

        return pred
    
    def available_model_classes(self):
        return ["GradientBoostingRegressor", "GradientBoostingClassifier"]