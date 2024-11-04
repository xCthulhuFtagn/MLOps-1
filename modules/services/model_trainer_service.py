
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
regressor_dir_path = f'{model_dir_path}/regressor'
classifier_dir_path = f'{model_dir_path}/classifier'

class ModelTrainService():
    def __init__(self):
        classification_dataset = load_iris()
        self.X_train_cl, self.y_train_cl = classification_dataset.data, classification_dataset.target
        # self.X_train_cl, self.X_test_cl, self.y_train_cl, self.y_test_cl = train_test_split(X, y, test_size=0.2)
        # Id
        # SepalLengthCm
        # SepalWidthCm
        # PetalLengthCm
        # PetalWidthCm
        # Species (target)

        regression_dataset = fetch_california_housing()
        self.X_train_reg, self.y_train_reg = classification_dataset.data, classification_dataset.target
        # self.X_train_reg, self.X_test_reg, self.y_train_reg, self.y_test_reg = train_test_split(X, y, test_size=0.2)
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
        self.training_status = "ready"
        self.classifier_lock = threading.Lock()
        self.regressor_lock = threading.Lock()

    def train(self, model_class: str, hyper_params: Dict) -> str:
        try:
            match model_class:
                case "GradientBoostingRegressor":
                    if self.is_model_in_training(model_class):
                        raise ValueError("Regressor is already being trained")
                    self.regressor_lock.acquire()

                    model = GradientBoostingRegressor(*hyper_params)
                    model.train(self.X_train_reg, self.y_train_reg)
                    with open(f'{regressor_dir_path}/model.pkl') as f:
                        pickle.dump(model,f)
                        self.regressor_lock.release()
                case "GradientBoostingClassifier":
                    if self.is_model_in_training(model_class):
                        raise ValueError("Classifier is already being trained")
                    self.classifier_lock.acquire()

                    model = GradientBoostingClassifier(*hyper_params)
                    X, y = self.classification_dataset.data, self.classification_dataset.target
                    model.train(self.X_train_cl, self.y_train_cl)
                    with open(f'{classifier_dir_path}/model.pkl') as f:
                        pickle.dump(model,f)
                        self.classifier_lock.release()
                case _:
                    raise ValueError(f"Invalid model class: {model_class}")
        except Exception as e:
            print(f"Error in train: {e}")

    def predict(self, model_class: str, inference_data: pd.DataFrame):
        match model_class:
            case "GradientBoostingRegressor":
                # check if model exists
                if os.path.exists(f'{regressor_dir_path}/model.pkl'):
                    model = pickle.load(f'{regressor_dir_path}/model.pkl')
                else:
                    raise FileNotFoundError("No pretrained regressors available")
                pred = model.predict(inference_data)
            case "GradientBoostingClassifier":
                if os.path.exists(f'{classifier_dir_path}/model.pkl'):
                    model = pickle.load(f'{regressor_dir_path}/model.pkl')
                else:
                    raise FileNotFoundError("No pretrained classifiers available")
                pred = model.predict(inference_data)
            case _:
                raise ValueError(f"Invalid model class: {model_class}")
        return pred
    
    def available_model_classes(self):
        return ["GradientBoostingRegressor", "GradientBoostingClassifier"]
    
    def is_model_in_training(self, model_class: str):
        match model_class:
            case "GradientBoostingRegressor":
                return not self.regressor_lock.locked()
            case "GradientBoostingClassifier":
                return not self.classifier_lock.locked()
            case _:
                raise ValueError(f"Invalid model class: {model_class}")