from typing import Dict

from sklearn.datasets import load_iris, fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
import pickle
import pandas as pd
import logging
import os
from concurrent import futures
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler("model_train_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

model_dir_path = "/home/owner/Documents/DEV/MLOps/HW1/models"
regressor_dir_path = f'{model_dir_path}'
classifier_dir_path = f'{model_dir_path}'

class ModelTrainService():
    """
    Service class for training and managing machine learning models.

    Attributes:
        X_train_cl (pd.DataFrame): Training data for classification models.
        y_train_cl (pd.Series): Target data for classification models.
        X_train_reg (pd.DataFrame): Training data for regression models.
        y_train_reg (pd.Series): Target data for regression models.
        status_model (dict): Dictionary tracking the status of each model.
    """

    def __init__(self):
        """
        Initialize the ModelTrainService with datasets and status tracking.
        """
        logger.info("Initializing ModelTrainService")
        classification_dataset = load_iris()
        self.X_train_cl, self.y_train_cl = classification_dataset.data, classification_dataset.target
        logger.info("Loaded classification dataset")

        regression_dataset = fetch_california_housing()
        self.X_train_reg, self.y_train_reg = regression_dataset.data, regression_dataset.target
        logger.info("Loaded regression dataset")

        self.training_thread = None
        self.classifier_lock = threading.Lock()
        self.regressor_lock = threading.Lock()

        self.status_model = dict()
        for model in os.listdir(f"{model_dir_path}"):
            model_name = model.split(".")[0]
            self.status_model[model_name] = "ready"
        logger.info(f"Model statuses set: {self.status_model}")

    def train(self, model_class: str, hyper_params: Dict) -> str:
        """
        Train a model with the specified class and hyperparameters.

        Args:
            model_class (str): The class of the model to train.
            hyper_params (Dict): Dictionary of hyperparameters for the model.

        Returns:
            str: Status message indicating training success or failure.
        """
        logger.info(f"Training request received for model class: {model_class} with hyperparameters: {hyper_params}")
        if model_class not in self.available_model_classes():
            logger.error(f"Invalid model class: {model_class}")
            return
        try:
            if model_class == "GradientBoostingClassifier":
                logger.info("Starting training for GradientBoostingClassifier")
                model = GradientBoostingClassifier(**hyper_params)
                model.fit(self.X_train_cl, self.y_train_cl)
                logger.info("Training completed for GradientBoostingClassifier")
            elif model_class == "GradientBoostingRegressor":
                logger.info("Starting training for GradientBoostingRegressor")
                model = GradientBoostingRegressor(**hyper_params)
                model.fit(self.X_train_reg, self.y_train_reg)
                logger.info("Training completed for GradientBoostingRegressor")

            with open(f'{regressor_dir_path}/{model_class}.pkl', 'wb') as f:
                pickle.dump(model, f)
            self.status_model[model_class] = "ready"
            logger.info(f"Model {model_class} saved and status set to ready")
        except Exception as e:
            self.status_model[model_class] = e
            logger.error(f"Error during training of {model_class}: {str(e)}", exc_info=True)

    def predict(self, model_class: str, inference_data: pd.DataFrame):
        """
        Make predictions using a trained model.

        Args:
            model_class (str): The class of the model to use for prediction.
            inference_data (pd.DataFrame): The input data for prediction.

        Returns:
            pd.Series: The prediction results.

        Raises:
            ValueError: If the model class is invalid or still in training.
            FileNotFoundError: If no pretrained model is found.
            Exception: If an error occurs during prediction.
        """
        logger.info(f"Prediction request received for model class: {model_class}")
        if model_class == "GradientBoostingRegressor":
            path = regressor_dir_path
        elif model_class == "GradientBoostingClassifier":
            path = classifier_dir_path
        else:
            logger.error(f"Invalid model class for prediction: {model_class}")
            raise ValueError(f"Invalid model class: {model_class}")

        if os.path.exists(f'{path}/{model_class}.pkl'):
            status = self.status_model.get(model_class, KeyError(f"No status for {model_class} available"))
            if status == "ready":
                logger.info(f"Loading model {model_class} for prediction")
                with open(f'{regressor_dir_path}/{model_class}.pkl', 'rb') as f:
                    model = pickle.load(f)
                logger.info(f"Model {model_class} loaded successfully")
            elif status == "training":
                logger.warning(f"Model {model_class} is still training")
                raise ValueError(f"{model_class} is still training")
            else:
                logger.error(f"Model {model_class} encountered an error: {status}")
                raise status
        else:
            logger.error(f"No pretrained {model_class} available")
            raise FileNotFoundError(f"No pretrained {model_class} available")

        try:
            pred = model.predict(inference_data)
            logger.info(f"Prediction completed for model class: {model_class}")
            return pred
        except Exception as e:
            logger.error(f"Error during prediction for {model_class}: {str(e)}", exc_info=True)
            raise e

    def available_model_classes(self):
        """
        Get a list of available model classes.

        Returns:
            list: A list of available model classes.
        """
        logger.info("Fetching available model classes")
        return ["GradientBoostingRegressor", "GradientBoostingClassifier"]
