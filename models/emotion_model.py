# models/emotion_model.py

import numpy as np
import librosa
import joblib
import os

# Try to import TensorFlow, use mock if not available
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("⚠️ TensorFlow not available. Using mock emotion predictions.")

class EmotionRecognitionModel:
    def __init__(self):
        self.model = None
        self.emotion_labels = ['Angry', 'Happy', 'Neutral', 'Sad']
        self.sample_rate = 16000
        self.duration = 3  # seconds
        self.n_mfcc = 40
        
    def create_cnn_model(self):
        """Create CNN model for emotion recognition"""
        if not TENSORFLOW_AVAILABLE:
            print("Cannot create CNN model: TensorFlow not available")
            return None
            
        model = keras.Sequential([
            layers.Input(shape=(self.n_mfcc, 86, 1)),  # 86 time frames for 3 seconds at 16000 Hz
            
            # Conv Layer 1
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Conv Layer 2
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Conv Layer 3
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Conv Layer 4
            layers.Conv2D(512, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.GlobalAveragePooling2D(),
            
            # Dense layers
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            
            # Output layer
            layers.Dense(len(self.emotion_labels), activation='softmax')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.0001),
            loss='categorical_crossentropy',
            metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
        )
        
        self.model = model
        return model
    
    def extract_features(self, audio_data):
        """Extract MFCC and Mel-spectrogram features"""
        try:
            # Ensure audio is at correct sample rate
            if len(audio_data) > self.sample_rate * self.duration:
                audio_data = audio_data[:self.sample_rate * self.duration]
            elif len(audio_data) < self.sample_rate * self.duration:
                # Pad with zeros
                audio_data = np.pad(audio_data, (0, self.sample_rate * self.duration - len(audio_data)))
            
            # Extract MFCCs
            mfccs = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=self.n_mfcc)
            
            # Extract Mel-spectrogram
            mel_spec = librosa.feature.melspectrogram(y=audio_data, sr=self.sample_rate)
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            
            # Resize to fixed dimensions
            target_time_steps = 86
            if mfccs.shape[1] < target_time_steps:
                mfccs = np.pad(mfccs, ((0, 0), (0, target_time_steps - mfccs.shape[1])))
                mel_spec_db = np.pad(mel_spec_db, ((0, 0), (0, target_time_steps - mel_spec_db.shape[1])))
            else:
                mfccs = mfccs[:, :target_time_steps]
                mel_spec_db = mel_spec_db[:, :target_time_steps]
            
            # Combine features
            features = np.stack([mfccs, mel_spec_db[:self.n_mfcc, :]], axis=-1)
            features = np.expand_dims(features, axis=0)
            
            return features
        
        except Exception as e:
            print(f"Feature extraction error: {e}")
            return None
    
    def predict_emotion(self, audio_data):
        """Predict emotion from audio data"""
        if self.model is None:
            # Return mock predictions if model not loaded
            return self._mock_predict()
        
        features = self.extract_features(audio_data)
        if features is None:
            return self._mock_predict()
        
        predictions = self.model.predict(features, verbose=0)
        predicted_idx = np.argmax(predictions[0])
        confidence = np.max(predictions[0])
        
        # Calculate arousal and valence
        arousal = self._calculate_arousal(predictions[0])
        valence = self._calculate_valence(predictions[0])
        
        return {
            'emotion': self.emotion_labels[predicted_idx],
            'confidence': float(confidence),
            'arousal': arousal,
            'valence': valence,
            'all_predictions': dict(zip(self.emotion_labels, predictions[0].tolist()))
        }
    
    def _calculate_arousal(self, predictions):
        """Calculate arousal level based on emotion predictions"""
        # High arousal: Angry, Happy
        # Low arousal: Neutral, Sad
        arousal_map = {'Angry': 0.8, 'Happy': 0.7, 'Neutral': 0.3, 'Sad': 0.2}
        return sum(predictions[i] * arousal_map[self.emotion_labels[i]] for i in range(len(self.emotion_labels)))
    
    def _calculate_valence(self, predictions):
        """Calculate valence (positivity/negativity)"""
        # Positive: Happy
        # Negative: Angry, Sad
        # Neutral: Neutral
        valence_map = {'Angry': 0.2, 'Happy': 0.8, 'Neutral': 0.5, 'Sad': 0.2}
        return sum(predictions[i] * valence_map[self.emotion_labels[i]] for i in range(len(self.emotion_labels)))
    
    def _mock_predict(self):
        """Return mock predictions for demo purposes"""
        import random
        emotions = ['Angry', 'Happy', 'Neutral']
        emotion = random.choice(emotions)
        return {
            'emotion': emotion,
            'confidence': random.uniform(0.7, 0.95),
            'arousal': random.uniform(0.2, 0.9),
            'valence': random.uniform(0.2, 0.8),
            'all_predictions': {e: random.uniform(0.1, 0.4) for e in self.emotion_labels}
        }
    
    def save_model(self, path='models/emotion_model.h5'):
        """Save trained model"""
        if self.model:
            self.model.save(path)
            return True
        return False
    
    def load_model(self, path='models/emotion_model.h5'):
        """Load trained model"""
        if os.path.exists(path):
            self.model = keras.models.load_model(path)
            return True
        return False

# Initialize model
emotion_model = EmotionRecognitionModel()