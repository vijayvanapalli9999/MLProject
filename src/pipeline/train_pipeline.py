import os
import sys
from src.exception import CustomException
from src.logger import logging
from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer

def run_training_pipeline():
    try:
        logging.info(">>> Training pipeline started.")

        # 1. Data Ingestion
        ingestion = DataIngestion()
        train_path, test_path = ingestion.initiate_data_ingestion()
        logging.info(f">>> Data ingestion completed. Train: {train_path}, Test: {test_path}")

        # 2. Data Transformation
        transformer = DataTransformation()
        train_arr, test_arr, _ = transformer.initiate_data_transformation(train_path, test_path)
        logging.info(">>> Data transformation completed.")

        # 3. Model Training
        trainer = ModelTrainer()
        score = trainer.initiate_model_trainer(train_arr, test_arr)
        logging.info(f">>> Model training completed with score: {score}")

    except Exception as e:
        logging.error(">>> Error occurred in training pipeline", exc_info=True)
        raise CustomException(e, sys)

if __name__ == "__main__":
    run_training_pipeline()
