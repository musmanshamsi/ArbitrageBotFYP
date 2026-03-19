import joblib
import numpy as np
from tensorflow.keras.models import load_model

class Predictor:

    def __init__(self):
        self.model = None
        self.scaler = None

    def load(self, model_path, scaler_path):
        self.model = load_model(model_path)
        self.scaler = joblib.load(scaler_path)

    def predict(self, data_sequence):
        scaled = self.scaler.transform(data_sequence)
        scaled = np.expand_dims(scaled, axis=0)
        price_pred, trend_pred = self.model.predict(scaled)
        return price_pred[0][0], trend_pred[0][0]