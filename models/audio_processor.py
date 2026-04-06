# models/audio_processor.py

import numpy as np
import librosa
import queue
import threading
import time
import streamlit as st
from scipy import signal

# Try to import sounddevice, but handle gracefully if not available (e.g., in Streamlit Cloud)
try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except (ImportError, OSError) as e:
    SOUNDDEVICE_AVAILABLE = False
    sd = None
    print(f"Warning: sounddevice not available: {e}. Audio recording features will be disabled.")

class AudioProcessor:
    def __init__(self, sample_rate=16000, chunk_duration=3):
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_samples = int(sample_rate * chunk_duration)
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.stream = None
        self.audio_callback = None
        
    def start_stream(self, callback=None):
        """Start audio stream using sounddevice"""
        if not SOUNDDEVICE_AVAILABLE:
            print("Error: sounddevice is not available in this environment.")
            print("This is common in cloud environments like Streamlit Cloud.")
            print("Please ensure packages.txt contains: libportaudio2 and libsndfile1")
            return False
        
        self.is_recording = True
        self.audio_callback = callback
        
        def audio_callback_wrapper(indata, frames, time_info, status):
            if status:
                print(f"Audio callback status: {status}")
            if self.is_recording:
                audio_data = indata.flatten()
                self.audio_queue.put(audio_data)
                if self.audio_callback:
                    self.audio_callback(audio_data)
        
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=audio_callback_wrapper,
                blocksize=self.chunk_samples,
                dtype=np.float32
            )
            self.stream.start()
            return True
        except Exception as e:
            print(f"Error starting audio stream: {e}")
            return False
    
    def stop_stream(self):
        """Stop audio stream"""
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
    
    def get_audio_chunk(self, timeout=1):
        """Get next audio chunk from queue"""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def preprocess_audio(self, audio_data):
        """Preprocess audio data"""
        # Ensure audio is float32
        audio_data = audio_data.astype(np.float32)
        
        # Convert to mono if needed
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
        
        # Normalize
        if np.max(np.abs(audio_data)) > 0:
            audio_data = audio_data / np.max(np.abs(audio_data))
        
        # Apply pre-emphasis filter
        pre_emphasis = 0.97
        if len(audio_data) > 1:
            audio_data = np.append(audio_data[0], audio_data[1:] - pre_emphasis * audio_data[:-1])
        
        # Remove silence
        audio_data = self.remove_silence(audio_data)
        
        return audio_data
    
    def remove_silence(self, audio_data, threshold=0.01):
        """Remove silence from audio"""
        non_silent = np.abs(audio_data) > threshold
        
        # Find first and last non-silent index
        non_silent_indices = np.where(non_silent)[0]
        if len(non_silent_indices) == 0:
            return audio_data
        
        start_idx = max(0, non_silent_indices[0] - int(0.1 * self.sample_rate))
        end_idx = min(len(audio_data), non_silent_indices[-1] + int(0.1 * self.sample_rate))
        
        return audio_data[start_idx:end_idx]
    
    def extract_pitch(self, audio_data):
        """Extract pitch (fundamental frequency)"""
        try:
            pitches, magnitudes = librosa.piptrack(y=audio_data, sr=self.sample_rate)
            pitch_values = pitches[magnitudes > np.max(magnitudes) * 0.8]
            
            if len(pitch_values) > 0:
                return float(np.mean(pitch_values))
            return 0.0
        except:
            return 0.0
    
    def extract_energy(self, audio_data):
        """Extract RMS energy"""
        if len(audio_data) > 0:
            return float(np.sqrt(np.mean(audio_data**2)))
        return 0.0
    
    def extract_speaking_rate(self, audio_data):
        """Estimate speaking rate"""
        try:
            # Detect onsets
            onset_frames = librosa.onset.onset_detect(y=audio_data, sr=self.sample_rate)
            if len(onset_frames) > 1:
                duration = len(audio_data) / self.sample_rate
                return float(len(onset_frames) / duration)
            return 0.0
        except:
            return 0.0
    
    def calculate_prosodic_features(self, audio_data):
        """Calculate prosodic features"""
        pitch = self.extract_pitch(audio_data)
        energy = self.extract_energy(audio_data)
        speaking_rate = self.extract_speaking_rate(audio_data)
        
        return {
            'pitch': pitch,
            'energy': energy,
            'speaking_rate': speaking_rate
        }
    
    def is_available(self):
        """Check if audio input is available"""
        if not SOUNDDEVICE_AVAILABLE:
            return False
        try:
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            return len(input_devices) > 0
        except:
            return False

@st.cache_resource
def get_audio_processor():
    """Get cached audio processor instance"""
    return AudioProcessor()

# Initialize audio processor with caching
audio_processor = get_audio_processor()