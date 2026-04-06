# 🚀 Streamlit Cloud Deployment Guide

## Problem Fixed
**Error:** `OSError: PortAudio library not found`

**Cause:** The `sounddevice` library requires PortAudio (a native C library) that wasn't installed in the Streamlit Cloud environment.

---

## Solution Implemented

### 1. **Created `packages.txt`** ✓
This file tells Streamlit Cloud to install system dependencies:
- `libportaudio2` - PortAudio library for audio I/O
- `libsndfile1` - Audio file handling library

### 2. **Updated `audio_processor.py`** ✓
- Added graceful fallback if sounddevice unavailable
- Checks `SOUNDDEVICE_AVAILABLE` flag before using audio features
- Provides clear error messages when audio recording fails

### 3. **Created `.streamlit/config.toml`** ✓
- Streamlit configuration for cloud deployment
- Theme settings for professional UI
- Logging configuration

---

## Deployment Steps

### Step 1: Push Changes to GitHub
```bash
git add .
git commit -m "Setup: Add Streamlit Cloud deployment configuration"
git push origin main
```

### Step 2: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select repository: `Kelvin-Njagi/emotion.io`
4. Select branch: `main`
5. Set Main file path: `app.py`
6. Click **"Deploy"**

### Step 3: Wait for Deployment
- Streamlit will install dependencies from `requirements.txt`
- Streamlit will install system packages from `packages.txt`
- The app will start automatically

---

## File Structure
```
emotion.io/
├── app.py                    # Main application
├── run.py                    # Application runner
├── requirements.txt          # Python dependencies
├── packages.txt              # System dependencies (NEW)
├── .gitignore               # Git ignore rules
├── .streamlit/
│   └── config.toml          # Streamlit config (NEW)
├── auth/
│   ├── authentication.py
│   └── security.py
├── database/
│   ├── db_manager.py
│   └── schema.sql
├── models/
│   ├── audio_processor.py   # UPDATED: Graceful fallback
│   └── emotion_model.py
├── pages/
├── utils/
│   ├── logger.py
│   └── realtime_analytics.py
└── System Architecture
```

---

## Audio Features in Streamlit Cloud

### ⚠️ Important Note
**Real-time audio recording** (`sounddevice` streaming) may not work fully in Streamlit Cloud because:
- Streamlit Cloud is a server-side environment without direct user audio device access
- The browser-based interface doesn't have direct audio I/O

### ✅ Recommended Approach
For production use, consider:
1. **File Upload:** Let users upload pre-recorded audio files
2. **Web Audio API:** Use browser's Web Audio API for client-side recording
3. **External Service:** Send audio to a backend service for processing

---

## Troubleshooting

### If still getting OSError after deployment:
- Check the Logs tab in Streamlit Cloud app settings
- Verify `packages.txt` is in the repository root
- Try restarting the app using "Reboot" button in Manage app

### If audio features aren't working:
- Check that `audio_processor.py` has the updated error handling
- Use Streamlit's file uploader for audio input instead of recording
- Add this to your app for fallback:
  ```python
  uploaded_file = st.file_uploader("Upload audio file", type=['wav', 'mp3'])
  if uploaded_file:
      # Process uploaded audio
  ```

---

## Commands Reference

```bash
# Local testing
streamlit run app.py

# Push to GitHub
git add .
git commit -m "Deployment: Fix PortAudio issue for Streamlit Cloud"
git push origin main

# Check Streamlit logs
streamlit logs
```

---

## Support
- **Streamlit Docs:** https://docs.streamlit.io
- **Streamlit Cloud Docs:** https://docs.streamlit.io/deploy/streamlit-cloud
- **Sounddevice Docs:** https://python-sounddevice.readthedocs.io
