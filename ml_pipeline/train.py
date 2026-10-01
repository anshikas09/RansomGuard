import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import onnx
import onnxruntime as ort

from ml_pipeline.dataset import SyntheticDatasetGenerator
from ml_pipeline.sequences import build_sequences_by_session, split_by_session
from ml_pipeline.features import fit_and_save_scaler

class RansomwareLSTM(nn.Module):
    def __init__(self, input_size=8, hidden_size=128, num_layers=2, output_size=1, dropout=0.3):
        super(RansomwareLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers,
            batch_first=True, dropout=dropout if num_layers > 1 else 0
        )
        self.fc1 = nn.Linear(hidden_size, 64)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        self.fc2 = nn.Linear(64, output_size)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_out = lstm_out[:, -1, :]
        out = self.fc1(last_out)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)
        return self.sigmoid(out)

def run_training_pipeline():
    data_dir = "./data"
    all_events_file = os.path.join(data_dir, "all_events.jsonl")

    if not os.path.exists(all_events_file):
        print("Dataset not found. Generating synthetic dataset...")
        generator = SyntheticDatasetGenerator(output_dir=data_dir)
        generator.generate_dataset(num_benign_sessions=100, num_malicious_sessions=50)

    events = []
    with open(all_events_file, "r") as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))

    print(f"Loaded {len(events)} events from dataset.")

    X_raw, y_raw, sids = build_sequences_by_session(events, seq_length=10)
    print(f"Generated sequence matrix X shape: {X_raw.shape}, y shape: {y_raw.shape}")

    scaler = fit_and_save_scaler(X_raw, scaler_path="./models/scaler.pkl")
    N, seq_len, num_feats = X_raw.shape
    X_flat = X_raw.reshape(-1, num_feats)
    X_scaled_flat = scaler.transform(X_flat)
    X_scaled = X_scaled_flat.reshape(N, seq_len, num_feats)

    X_train, y_train, X_val, y_val, X_test, y_test = split_by_session(X_scaled, y_raw, sids)

    os.makedirs("./models", exist_ok=True)
    np.save("./models/X_test.npy", X_test)
    np.save("./models/y_test.npy", y_test)

    train_ds = TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train).unsqueeze(1))
    val_ds = TensorDataset(torch.FloatTensor(X_val), torch.FloatTensor(y_val).unsqueeze(1))

    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=32, shuffle=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = RansomwareLSTM().to(device)

    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3)

    epochs = 40
    best_val_loss = float('inf')
    patience = 10
    patience_counter = 0

    print(f"Starting PyTorch LSTM Training on device: {device}...")

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0

        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)

            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)
                val_loss += loss.item()

        avg_train_loss = train_loss / len(train_loader)
        avg_val_loss = val_loss / len(val_loader)
        scheduler.step(avg_val_loss)

        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            patience_counter = 0
            torch.save(model.state_dict(), "./models/best_model.pth")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping triggered at epoch {epoch+1}")
                break

        if (epoch + 1) % 5 == 0:
            print(f"Epoch [{epoch+1}/{epochs}] - Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}")

    print("Model training complete. Loading best checkpoint for ONNX export...")
    model.load_state_dict(torch.load("./models/best_model.pth"))
    model.eval()

    dummy_input = torch.randn(1, 10, 8).to(device)
    onnx_path = "./models/ransomware_detector.onnx"

    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )

    print(f"ONNX Model exported to {onnx_path}")

    onnx_model = onnx.load(onnx_path)
    onnx.checker.check_model(onnx_model)
    print("ONNX model structure verified: OK")

    session = ort.InferenceSession(onnx_path)
    input_name = session.get_inputs()[0].name
    res = session.run(None, {input_name: dummy_input.cpu().numpy()})
    print(f"ONNX Runtime inference test passed: output shape {res[0].shape}, output score {res[0][0][0]:.4f}")

if __name__ == "__main__":
    run_training_pipeline()
