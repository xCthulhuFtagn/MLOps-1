
from typing import Dict

from sklearn.datasets import load_iris, fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
import pickle
import pandas as pd

import os
from concurrent import futures
import threading

model_dir_path = "/home/owner/Documents/DEV/MLOps/HW1/models"
regressor_dir_path = f'{model_dir_path}'
classifier_dir_path = f'{model_dir_path}'

class ModelTrainService():
    def __init__(self):
        classification_dataset = load_iris()
        self.X_train_cl, self.y_train_cl = classification_dataset.data, classification_dataset.target
        # Id
        # SepalLengthCm
        # SepalWidthCm
        # PetalLengthCm
        # PetalWidthCm
        # Species (target)

        regression_dataset = fetch_california_housing()
        self.X_train_reg, self.y_train_reg = classification_dataset.data, classification_dataset.target
        # MedInc	
        # HouseAge	
        # AveRooms	
        # AveBedrms	
        # Population	
        # AveOccup	
        # Latitude	
        # Longitude
        # Price (target)
        self.training_thread = None
        self.classifier_lock = threading.Lock()
        self.regressor_lock = threading.Lock()
        
        print("set status model")
        self.status_model = dict()
        for model in os.listdir(f"{model_dir_path}"):
            model_name = model.split(".")[0]
            self.status_model[model_name] = "ready"

    def train(self, model_class: str, hyper_params: Dict) -> str:
        if model_class not in self.available_model_classes(): return
        try:
            match model_class:
                case "GradientBoostingClassifier":
                    model = GradientBoostingClassifier(*hyper_params)
                    model.fit(self.X_train_cl, self.y_train_cl)
                case "GradientBoostingRegressor": 
                    model = GradientBoostingRegressor(*hyper_params)
                    model.fit(self.X_train_reg, self.y_train_reg)
            with open(f'{regressor_dir_path}/{model_class}.pkl', 'wb') as f:
                pickle.dump(model,f)
            self.status_model[model_class] = "ready" 
        except Exception as e:
            self.status_model[model_class] = e

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