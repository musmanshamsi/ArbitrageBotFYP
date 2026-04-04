import numpy as np
import os

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("WARNING: PyTorch not installed. GRU model predictions will be unavailable.")
    print("Install with: py -3.10 -m pip install torch")
    
    # Mock nn.Module for graceful fallback
    class nn:
        class Module:
            pass
    torch = None

class GRUNet(nn.Module if TORCH_AVAILABLE else object):
    def __init__(self, input_dim=1, hidden_dim=50, output_dim=1, n_layers=2, drop_prob=0.2):
        super(GRUNet, self).__init__()
        self.hidden_dim = hidden_dim
        self.n_layers = n_layers
        self.gru = nn.GRU(input_dim, hidden_dim, n_layers, batch_first=True, dropout=drop_prob)
        self.fc = nn.Linear(hidden_dim, output_dim)
        self.relu = nn.ReLU()
        
    def forward(self, x, h):
        out, h = self.gru(x, h)
        out = self.fc(self.relu(out[:, -1]))
        return out, h

class Predictor:
    def __init__(self):
        self.model = None
        self.device = None
        self.min_val = None
        self.max_val = None
        
        if TORCH_AVAILABLE:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")

    def load(self, model_path='gru_model.pth', scaler_path='scaler_params.npy'):
        if not TORCH_AVAILABLE:
            print("WARNING: PyTorch unavailable - model prediction disabled")
            return
            
        self.model = GRUNet(1, 50, 1, 2).to(self.device)
        
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.eval()
            print("[OK] PyTorch Model Loaded.")
        else:
            print(f"[ERROR]: {model_path} not found!")

        if os.path.exists(scaler_path):
            params = np.load(scaler_path)
            self.min_val = params[0]
            self.max_val = params[1]
            print("[OK] Scaler Loaded.")

    def predict(self, data_sequence):
        if not TORCH_AVAILABLE or self.model is None or self.min_val is None:
            return 0.0

        data_sequence = np.array(data_sequence).flatten()
        scaled = (data_sequence - self.min_val) / (self.max_val - self.min_val)
        input_tensor = torch.Tensor(scaled).view(1, 10, 1).to(self.device)
        
        with torch.no_grad():
            h = torch.zeros(2, 1, 50).to(self.device)
            prediction, _ = self.model(input_tensor, h)
            
        predicted_val = prediction.item() 
        unscaled_pred = predicted_val * (self.max_val - self.min_val) + self.min_val
        
        return unscaled_pred

if __name__ == "__main__":
    p = Predictor()
    p.load()
    dummy_input = [0.01, 0.012, 0.011, 0.015, 0.014, 0.016, 0.013, 0.011, 0.012, 0.015]
    result = p.predict(dummy_input)
    print(f"Next Predicted Spread: {float(result):.6f}%")