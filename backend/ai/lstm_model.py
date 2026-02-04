"""
LSTM/GRU Model for Time Series Prediction with Attention and Transfer Learning
Predicts price direction and provides confidence scores
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import numpy as np
import pandas as pd
from typing import Tuple, Optional, Dict, List
import logging
from sklearn.preprocessing import StandardScaler
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AttentionLayer(nn.Module):
    """Multi-Head Attention Layer for temporal dependencies"""
    
    def __init__(self, hidden_dim: int, num_heads: int = 4):
        super(AttentionLayer, self).__init__()
        self.attention = nn.MultiheadAttention(hidden_dim, num_heads, batch_first=True)
        self.ln = nn.LayerNorm(hidden_dim)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        attn_out, _ = self.attention(x, x, x)
        return self.ln(x + attn_out)


class SequenceDataset(Dataset):
    """PyTorch Dataset for time series sequences"""
    
    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)
        
        assert len(X) == len(y), "Length mismatch"
    
    def __len__(self) -> int:
        return len(self.X)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.X[idx], self.y[idx]


class PricePredictionLSTM(nn.Module):
    """
    LSTM-based model for price direction prediction
    Architecture: LSTM → Attention → Dense
    """
    
    def __init__(self, input_dim: int, hidden_dim: int = 128, 
                 num_layers: int = 2, num_classes: int = 3,
                 dropout: float = 0.3, use_attention: bool = True):
        super(PricePredictionLSTM, self).__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.use_attention = use_attention
        
        # LSTM layer
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, 
                           batch_first=True, dropout=dropout if num_layers > 1 else 0)
        
        # Attention (optional)
        if use_attention:
            self.attention = AttentionLayer(hidden_dim, num_heads=4)
        
        # Classification head
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes)
        )
        
        # Confidence (separate head for uncertainty)
        self.confidence_head = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
            nn.Sigmoid()  # Output in [0, 1]
        )
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # LSTM forward
        lstm_out, (h_n, c_n) = self.lstm(x)  # (batch, seq_len, hidden)
        
        # Attention
        if self.use_attention:
            lstm_out = self.attention(lstm_out)
        
        # Use last timestep
        last_out = lstm_out[:, -1, :]  # (batch, hidden)
        
        # Classification
        logits = self.fc(last_out)
        
        # Confidence
        confidence = self.confidence_head(last_out)
        
        return logits, confidence


class PricePredictor:
    """Trains and serves LSTM for price prediction with transfer learning"""
    
    def __init__(self, input_dim: int, hidden_dim: int = 128,
                 device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.model = PricePredictionLSTM(input_dim, hidden_dim).to(device)
        self.scaler = StandardScaler()
        
        logger.info(f"LSTM Predictor initialized on {device}")
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
             X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None,
             epochs: int = 100, batch_size: int = 32, 
             learning_rate: float = 0.001) -> Dict:
        """Train the LSTM model with class weights for imbalanced data"""
        
        # Handle class imbalance
        unique, counts = np.unique(y_train, return_counts=True)
        class_weights = torch.tensor(counts.max() / counts, dtype=torch.float).to(self.device)
        
        criterion = nn.CrossEntropyLoss(weight=class_weights)
        confidence_criterion = nn.BCELoss()
        
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=10)
        
        train_dataset = SequenceDataset(X_train, y_train)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        if X_val is not None:
            val_dataset = SequenceDataset(X_val, y_val)
            val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
        history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
        
        self.model.train()
        
        for epoch in range(epochs):
            train_loss = 0.0
            train_correct = 0
            train_total = 0
            
            for X_batch, y_batch in train_loader:
                X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)
                
                optimizer.zero_grad()
                
                logits, confidence = self.model(X_batch)
                
                # Classification loss + confidence regularization
                cls_loss = criterion(logits, y_batch)
                conf_target = torch.where(
                    torch.arange(logits.size(1)).unsqueeze(0).to(self.device) == y_batch.unsqueeze(1),
                    torch.ones_like(logits),
                    torch.zeros_like(logits)
                ).max(dim=1)[0].float().unsqueeze(1)
                
                conf_loss = confidence_criterion(confidence, conf_target)
                loss = cls_loss + 0.1 * conf_loss
                
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()
                
                train_loss += loss.item()
                _, predicted = torch.max(logits.data, 1)
                train_total += y_batch.size(0)
                train_correct += (predicted == y_batch).sum().item()
            
            avg_train_loss = train_loss / len(train_loader)
            train_acc = 100 * train_correct / train_total
            
            history['train_loss'].append(avg_train_loss)
            history['train_acc'].append(train_acc)
            
            # Validation
            if X_val is not None:
                val_loss, val_acc = self.evaluate(val_loader)
                history['val_loss'].append(val_loss)
                history['val_acc'].append(val_acc)
                scheduler.step(val_loss)
                
                if (epoch + 1) % 10 == 0:
                    logger.info(f"Epoch {epoch+1}/{epochs} - "
                              f"Train Loss: {avg_train_loss:.4f}, Acc: {train_acc:.2f}% - "
                              f"Val Loss: {val_loss:.4f}, Acc: {val_acc:.2f}%")
            else:
                if (epoch + 1) % 10 == 0:
                    logger.info(f"Epoch {epoch+1}/{epochs} - Train Loss: {avg_train_loss:.4f}, Acc: {train_acc:.2f}%")
        
        return history
    
    def evaluate(self, val_loader: DataLoader) -> Tuple[float, float]:
        """Evaluate model on validation set"""
        self.model.eval()
        criterion = nn.CrossEntropyLoss()
        
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)
                
                logits, _ = self.model(X_batch)
                loss = criterion(logits, y_batch)
                
                val_loss += loss.item()
                _, predicted = torch.max(logits.data, 1)
                val_total += y_batch.size(0)
                val_correct += (predicted == y_batch).sum().item()
        
        self.model.train()
        
        return val_loss / len(val_loader), 100 * val_correct / val_total
    
    def predict(self, X: np.ndarray) -> Tuple[int, float]:
        """
        Predict price direction with confidence
        Returns: (class, confidence)
        class: 0=down, 1=sideways, 2=up
        """
        X_tensor = torch.tensor(X, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        self.model.eval()
        with torch.no_grad():
            logits, confidence = self.model(X_tensor)
            probs = torch.nn.functional.softmax(logits, dim=1)
            pred_conf, prediction = torch.max(probs, 1)
        
        return int(prediction.item()), float(pred_conf.item())
    
    def save(self, path: str):
        """Save model and scaler"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'scaler': self.scaler
        }, path)
        logger.info(f"LSTM model saved to {path}")
    
    def load(self, path: str):
        """Load model and scaler"""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.scaler = checkpoint['scaler']
        logger.info(f"LSTM model loaded from {path}")
    
    def transfer_learn(self, X_new: np.ndarray, y_new: np.ndarray,
                      freeze_layers: int = 1, epochs: int = 30) -> Dict:
        """
        Transfer learning: Fine-tune on new data
        freeze_layers: Number of LSTM layers to freeze
        """
        # Freeze early layers
        layer_count = 0
        for name, param in self.model.named_parameters():
            if 'lstm' in name and layer_count < freeze_layers:
                param.requires_grad = False
                layer_count += 1
        
        logger.info(f"Frozen {layer_count} LSTM layers for transfer learning")
        
        # Train with lower learning rate
        return self.train(X_new, y_new, epochs=epochs, learning_rate=0.0001)


if __name__ == "__main__":
    # Example
    predictor = PricePredictor(input_dim=20, hidden_dim=128)
    
    # Create dummy data
    X_train = np.random.randn(500, 50, 20)  # (samples, sequence_len, features)
    y_train = np.random.randint(0, 3, 500)  # 0=down, 1=sideways, 2=up
    
    X_val = np.random.randn(100, 50, 20)
    y_val = np.random.randint(0, 3, 100)
    
    history = predictor.train(X_train, y_train, X_val, y_val, epochs=10)
    
    # Predict
    X_test = np.random.randn(1, 50, 20)
    direction, confidence = predictor.predict(X_test[0])
    print(f"Predicted direction: {['down', 'sideways', 'up'][direction]}, Confidence: {confidence:.2%}")
