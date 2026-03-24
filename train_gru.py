import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.preprocessing import MinMaxScaler
import os

# 1. Point to your actual file path from the screenshot
# Note: It looks like it's inside a folder named 'data'
# Change this:
file_path = os.path.join('data', 'coin_Bitcoin.csv')

# To this:
file_path = 'coin_Bitcoin.csv'

if not os.path.exists(file_path):
    print(f"❌ Error: File not found at {file_path}")
    print("Make sure you are running the script from the folder that contains the 'data' folder!")
    exit()

# Load the CSV
df = pd.read_csv(file_path)

# 2. Simulate Arbitrage Spread
# Since the CSV only has one price, we simulate a 'Spread' based on 
# High/Low volatility to give the GRU something to learn.
df['spread'] = ((df['High'] - df['Low']) / df['Close']) * 100

# Drop any missing values
df = df.dropna()
print(f"✅ Data loaded. Training on {len(df)} price points.")

# 3. Preprocessing
dataset = df['spread'].values.reshape(-1, 1)
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(dataset)

sequence_length = 10
X, y = [], []
for i in range(sequence_length, len(scaled_data)):
    X.append(scaled_data[i-sequence_length:i, 0])
    y.append(scaled_data[i, 0])

X = np.array(X).reshape(-1, sequence_length, 1)
y = np.array(y).reshape(-1, 1)

# Convert to Tensors
X_t = torch.Tensor(X)
y_t = torch.Tensor(y)

# 4. The GRUNet Class (From your project screenshot)
class GRUNet(nn.Module):
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
    
    def init_hidden(self, batch_size):
        weight = next(self.parameters()).data
        hidden = weight.new(self.n_layers, batch_size, self.hidden_dim).zero_()
        return hidden

# 5. Training Settings
model = GRUNet(1, 50, 1, 2)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
train_loader = DataLoader(TensorDataset(X_t, y_t), batch_size=32, shuffle=True)

# 6. Run Training
print("🚀 Starting AI Training on Bitcoin Data...")
epochs = 5 # Small number for testing
for epoch in range(epochs):
    model.train()
    total_loss = 0
    for inputs, labels in train_loader:
        h = model.init_hidden(inputs.size(0))
        optimizer.zero_grad()
        out, h = model(inputs, h)
        loss = criterion(out, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    
    print(f"Epoch {epoch+1}/{epochs} | Avg Loss: {total_loss/len(train_loader):.6f}")

# 7. Save the Brain
torch.save(model.state_dict(), 'gru_model.pth')
np.save('scaler_params.npy', [scaler.data_min_, scaler.data_max_])
print("\n✅ SUCCESS: 'gru_model.pth' and 'scaler_params.npy' have been created.")