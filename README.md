# 🎙️ Speech-Driven Emotion Recognition System

## Overview
A Streamlit-based web application that analyzes speech to recognize emotions using audio processing and machine learning.

---

## 🌟 Features

- **Real-time Audio Processing** - Process audio files and streams
- **Emotion Recognition** - Detect emotions: Angry, Happy, Neutral, Sad
- **Arousal & Valence Analysis** - Measure emotional intensity and positivity
- **User Authentication** - Secure login system
- **Real-time Analytics** - Track emotion patterns over time
- **Professional Dashboard** - Interactive visualizations with Plotly

---

## 📁 Project Structure

```
emotion.io/
├── app.py                      # Main Streamlit application
├── run.py                      # Application launcher
├── requirements.txt            # Python dependencies
├── packages.txt               # System dependencies (Streamlit Cloud)
├── .gitignore                 # Git ignore rules
├── DEPLOYMENT.md              # Detailed deployment guide
├── README.md                  # This file
│
├── auth/                      # Authentication module
│   ├── __init__.py
│   ├── authentication.py      # User login/signup
│   └── security.py            # Password hashing & security
│
├── database/                  # Database module
│   ├── __init__.py
│   ├── db_manager.py          # Database operations
│   └── schema.sql             # Database schema
│
├── models/                    # ML Models module
│   ├── __init__.py
│   ├── audio_processor.py     # Audio feature extraction
│   └── emotion_model.py       # Emotion recognition model
│
├── pages/                     # Streamlit pages (if using multi-page)
│   └── (future pages)
│
└── utils/                     # Utility modules
    ├── __init__.py
    ├── logger.py              # Logging system
    └── realtime_analytics.py  # Analytics engine
```

---

## 🚀 Quick Start (Local Development)

### 1. **Clone Repository**
```bash
git clone https://github.com/Kelvin-Njagi/emotion.io.git
cd emotion.io
```

### 2. **Set Up Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Run Application Locally**
```bash
streamlit run app.py
```
The app will open at `http://localhost:8501`

---

## 📦 Dependencies

### Core Dependencies
- **streamlit** - Web framework for data apps
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **librosa** - Audio feature extraction
- **scikit-learn** - Machine learning utilities
- **plotly** - Interactive visualizations

### Optional (for advanced use)
- **tensorflow** - Deep learning (remove for lightweight deployment)
  - Only needed if using CNN emotion model
  - Use scikit-learn fallback for lightweight environments

### System Dependencies (Streamlit Cloud)
- **libportaudio2** - Audio I/O library
- **libsndfile1** - Audio file processing

---

## 🔧 Configuration

### Environment Variables
Create `.env` file for sensitive data:
```bash
# Database
DATABASE_URL=sqlite:///emotion_recognition.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Streamlit Config
See `.streamlit/config.toml` for:
- Theming
- Logging levels
- Client settings

---

## 🌐 Deployment to Streamlit Cloud

### Prerequisites
- GitHub account with this repository
- Streamlit Cloud account (share.streamlit.io)

### Deployment Steps

1. **Ensure all changes are pushed to GitHub**
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

2. **Go to Streamlit Cloud**
   - Visit https://share.streamlit.io
   - Click **"New app"**

3. **Configure App**
   - **Repository**: Kelvin-Njagi/emotion.io
   - **Branch**: main
   - **Main file**: app.py

4. **Advanced Options** (if needed)
   - Set environment variables in "Secrets"
   - Configure Python version if needed

5. **Deploy**
   - Click **"Deploy"**
   - Wait for installation to complete (~2-3 minutes)

### What Streamlit Cloud Does
- ✓ Installs packages from `requirements.txt`
- ✓ Installs system packages from `packages.txt`
- ✓ Runs `streamlit run app.py`
- ✓ Hosts at `https://yourusername-emotion-io.streamlit.app`

---

## 🔧 Troubleshooting

### Installation Errors

**Problem**: "PortAudio library not found"
- **Solution**: Ensure `packages.txt` contains system dependencies
- **Status**: Already fixed ✓

**Problem**: "TensorFlow installation fails"
- **Solution**: TensorFlow removed from default deployment
- **Reason**: Too heavy for Streamlit Cloud
- **Fallback**: Uses scikit-learn with mock predictions

**Problem**: "Old packages cached"
- **Solution**: 
  1. In Streamlit Cloud, go to "Manage app"
  2. Click "Reboot"
  3. Clear browser cache

### Audio Issues

**Problem**: Audio recording doesn't work on Streamlit Cloud
- **Expected**: Audio recording on server-side environment isn't supported
- **Solution**: Use `st.file_uploader()` for audio files instead
- **Example**: 
  ```python
  uploaded_file = st.file_uploader("Upload audio", type=['wav', 'mp3'])
  ```

### Database Issues

**Problem**: Database connection errors
- **Solution**: Check `DATABASE_URL` in `.env` file
- **Streamlit Cloud**: Use SQLite (embedded) or external database with credentials in Secrets

---

## 📊 Model Information

### Emotion Labels
- **Angry** - High arousal, negative valence
- **Happy** - High arousal, positive valence  
- **Neutral** - Medium arousal, neutral valence
- **Sad** - Low arousal, negative valence

### Features Used
- **MFCC** (Mel-frequency cepstral coefficients) - Speech characteristics
- **Mel-spectrogram** - Frequency distribution over time

### Predictions Include
- Emotion label
- Confidence score (0.0-1.0)
- Arousal level (0.0-1.0) - Intensity of emotion
- Valence level (0.0-1.0) - Positivity/negativity
- All emotion probabilities

---

## 🔐 Security

### Authentication
- Bcrypt password hashing
- JWT token-based sessions
- Secure password validation

### Best Practices
- Never commit `.env` files with credentials
- Use Streamlit "Secrets" for sensitive data in cloud
- Regular dependency updates

---

## 📈 Analytics

The system tracks:
- User login history
- Emotion predictions over time
- Emotion frequency and patterns
- Real-time statistics dashboard

---

## 🧪 Testing Locally

### Test Audio Processing
```python
from models.audio_processor import AudioProcessor
processor = AudioProcessor()
# Load and process audio
```

### Test Emotion Model
```python
from models.emotion_model import emotion_model
import numpy as np

# Create dummy audio data
audio = np.random.randn(16000 * 3)  # 3 seconds at 16kHz
prediction = emotion_model.predict_emotion(audio)
print(prediction)
```

---

## 📝 Git Workflow

### New Features
```bash
git checkout -b feature/your-feature
git add .
git commit -m "Add: description of changes"
git push origin feature/your-feature
# Create Pull Request on GitHub
```

### Bug Fixes
```bash
git checkout -b fix/bug-description
# Make fixes
git add .
git commit -m "Fix: description of fix"
git push origin fix/bug-description
```

### Deployment to Cloud
```bash
git checkout main
git pull origin main
# Make sure changes are tested
git push origin main
# Streamlit Cloud auto-deploys from main branch
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Commit with clear messages
5. Push to your fork
6. Create a Pull Request

---

## 📚 Documentation

- [Streamlit Documentation](https://docs.streamlit.io)
- [Streamlit Cloud Docs](https://docs.streamlit.io/deploy/streamlit-cloud)
- [Librosa Documentation](https://librosa.org)
- [Scikit-learn Documentation](https://scikit-learn.org)

---

## 📧 Support

- **Issues**: Create GitHub issue with detailed description
- **Questions**: Check Streamlit forums
- **Email**: njagikelvin60@gmail.com

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🎯 Roadmap

- [ ] Add real-time streaming analysis
- [ ] Improve emotion model accuracy
- [ ] Add multiple language support
- [ ] Mobile app version
- [ ] API endpoints
- [ ] Advanced analytics dashboard

---

**Last Updated**: April 6, 2026  
**Status**: ✅ Ready for Production
