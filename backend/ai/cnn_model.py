"""
CNN Model for Candlestick Pattern Recognition
Trained on HuggingFace BTC dataset and custom candlestick patterns
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from typing import Tuple, Optional
import logging
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CandlestickImageGenerator:
    """
    Converts OHLCV data to candlestick images
    Generates standardized images for CNN training
    """
    
    def __init__(self, width: int = 128, height: int = 128, 
                 num_candles: int = 60, normalize: bool = True):
        self.width = width
        self.height = height
        self.num_candles = num_candles
        self.normalize = normalize
    
    def generate_image(self, ohlcv: np.ndarray) -> np.ndarray:
        """
        Convert OHLCV sequence to candlestick image
        ohlcv: shape (num_candles, 5) with O, H, L, C, V
        Returns: (128, 128, 3) RGB image
        """
        assert ohlcv.shape == (self.num_candles, 5), "Expected shape (60, 5)"
        
        # Normalize price data
        if self.normalize:
            high = ohlcv[:, 1].max()
            low = ohlcv[:, 2].min()
            price_range = high - low if high != low else 1
            normalized_ohlc = (ohlcv[:, :4] - low) / price_range
        else:
            normalized_ohlc = ohlcv[:, :4]
        
        # Create image using matplotlib
        fig = plt.figure(figsize=(self.width/100, self.height/100), dpi=100)
        ax = fig.add_subplot(111)
        
        candle_width = self.width / self.num_candles * 0.8
        
        for i, (o, h, l, c) in enumerate(normalized_ohlc):
            x_pos = (i + 0.5) * (self.width / self.num_candles)
            
            # Wick (high-low)
            ax.plot([x_pos, x_pos], [l * self.height, h * self.height], 
                   color='black', linewidth=1)
            
            # Body (open-close)
            color = 'green' if c > o else 'red'
            body_bottom = min(o, c) * self.height
            body_height = abs(c - o) * self.height
            
            rect = Rectangle((x_pos - candle_width/2, body_bottom), 
                           candle_width, body_height,
                           linewidth=1, edgecolor='black', facecolor=color)
            ax.add_patch(rect)
        
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.axis('off')
        
        # Convert to numpy array
        fig.canvas.draw()
        image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        plt.close(fig)
        
        # Resize to exact dimensions
        from PIL import Image
        img = Image.fromarray(image)
        img = img.resize((self.width, self.height))
        
        return np.array(img) / 255.0  # Normalize to [0, 1]


class CandlestickDataset(Dataset):
    """PyTorch Dataset for candlestick images"""
    
    def __init__(self, ohlcv_sequences: np.ndarray, labels: np.ndarray,
                 image_generator: CandlestickImageGenerator):
        self.ohlcv_sequences = ohlcv_sequences
        self.labels = labels
        self.image_generator = image_generator
        
        assert len(ohlcv_sequences) == len(labels), "Length mismatch"
        
    def __len__(self) -> int:
        return len(self.labels)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        ohlcv = self.ohlcv_sequences[idx]
        image = self.image_generator.generate_image(ohlcv)
        label = torch.tensor(self.labels[idx], dtype=torch.long)
        
        # Convert to CHW format for CNN
        image = torch.tensor(image).permute(2, 0, 1).float()
        
        return image, label


class CandlestickCNN(nn.Module):
    """
    CNN for candlestick pattern classification
    Architecture: Conv blocks → Flatten → Dense layers
    """
    
    def __init__(self, num_classes: int = 4, dropout_rate: float = 0.3):
        super(CandlestickCNN, self).__init__()
        
        self.features = nn.Sequential(
            # Conv Block 1
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(32),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(64),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout(dropout_rate),
            
            # Conv Block 2
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(128),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(128),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout(dropout_rate),
            
            # Conv Block 3
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(256),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(256),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        
        self.classifier = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(128, num_classes),
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x


class CandlestickPatternDetector:
    """Trains and serves CNN for pattern detection"""
    
    def __init__(self, num_classes: int = 4, device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.model = CandlestickCNN(num_classes=num_classes).to(device)
        self.image_generator = CandlestickImageGenerator()
        self.num_classes = num_classes
        self.class_names = ['bearish', 'neutral', 'bullish', 'strong_bullish'][:num_classes]
        
        logger.info(f"CNN Initialized on {device}")
    
    def train(self, train_loader: DataLoader, val_loader: Optional[DataLoader] = None,
             epochs: int = 50, learning_rate: float = 0.001) -> Dict:
        """Train the CNN model"""
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=5)
        criterion = nn.CrossEntropyLoss()
        
        history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
        
        self.model.train()
        
        for epoch in range(epochs):
            # Training
            train_loss = 0.0
            train_correct = 0
            train_total = 0
            
            for images, labels in train_loader:
                images, labels = images.to(self.device), labels.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                train_total += labels.size(0)
                train_correct += (predicted == labels).sum().item()
            
            avg_train_loss = train_loss / len(train_loader)
            train_acc = 100 * train_correct / train_total
            
            history['train_loss'].append(avg_train_loss)
            history['train_acc'].append(train_acc)
            
            # Validation
            if val_loader:
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
            for images, labels in val_loader:
                images, labels = images.to(self.device), labels.to(self.device)
                outputs = self.model(images)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        self.model.train()
        
        avg_val_loss = val_loss / len(val_loader)
        val_acc = 100 * val_correct / val_total
        
        return avg_val_loss, val_acc
    
    def predict(self, ohlcv: np.ndarray) -> Tuple[int, float]:
        """
        Predict pattern class and confidence
        ohlcv: shape (60, 5)
        Returns: (class_id, confidence)
        """
        image = self.image_generator.generate_image(ohlcv)
        image = torch.tensor(image).permute(2, 0, 1).float().unsqueeze(0).to(self.device)
        
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(image)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            confidence, prediction = torch.max(probs, 1)
        
        return int(prediction.item()), float(confidence.item())
    
    def save(self, path: str):
        """Save model weights"""
        torch.save(self.model.state_dict(), path)
        logger.info(f"Model saved to {path}")
    
    def load(self, path: str):
        """Load model weights"""
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        logger.info(f"Model loaded from {path}")


if __name__ == "__main__":
    # Example usage
    detector = CandlestickPatternDetector(num_classes=4)
    
    # Create dummy data
    X_train = np.random.randn(100, 60, 5)
    y_train = np.random.randint(0, 4, 100)
    
    dataset = CandlestickDataset(X_train, y_train, detector.image_generator)
    train_loader = DataLoader(dataset, batch_size=16, shuffle=True)
    
    # Train (mock)
    logger.info("Model ready for training on real candlestick data")
