import os
import zipfile
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_PATH = os.path.join(BASE_DIR, "Dataset2.zip")
EXTRACT_PATH = os.path.join(BASE_DIR, "data")

MODEL_PATH = os.path.join(BASE_DIR, "gru_model.h5")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")

# --------------------------
# Extract Dataset
# --------------------------
if not os.path.exists(EXTRACT_PATH):
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_PATH)

csv_file = None
for root, dirs, files in os.walk(EXTRACT_PATH):
    for file in files:
        if file.endswith(".csv"):
            csv_file = os.path.join(root, file)
            break

if csv_file is None:
    raise Exception("No CSV file found inside Dataset2.zip")

print("Using dataset:", csv_file)

df = pd.read_csv(csv_file)

required_cols = ["timestamp", "open", "high", "low", "close", "volume"]
for col in required_cols:
    if col not in df.columns:
        raise Exception(f"Missing column: {col}")

df = df.sort_values("timestamp")
df["return"] = df["close"].pct_change()
df["volatility"] = df["return"].rolling(20).std()
df["target"] = df["close"].shift(-1)

df.dropna(inplace=True)

features = ["open", "high", "low", "close", "volume", "return", "volatility"]

scaler = MinMaxScaler()
scaled = scaler.fit_transform(df[features])
joblib.dump(scaler, SCALER_PATH)

SEQ_LEN = 50

X, y = [], []

for i in range(len(scaled) - SEQ_LEN):
    X.append(scaled[i:i+SEQ_LEN])
    y.append(df["target"].iloc[i+SEQ_LEN])

X = np.array(X)
y = np.array(y)

split = int(len(X) * 0.8)

X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# --------------------------
# Build GRU Model
# --------------------------
model = Sequential([
    GRU(128, return_sequences=True, input_shape=(SEQ_LEN, len(features))),
    Dropout(0.3),
    GRU(64),
    Dropout(0.3),
    Dense(1)
])

model.compile(optimizer="adam", loss="mse")

early_stop = EarlyStopping(patience=5, restore_best_weights=True)

model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=20,
    batch_size=64,
    callbacks=[early_stop]
)

model.save(MODEL_PATH)

print("Model trained and saved successfully.")