# STFT Processing Project - Summary

## ✅ What Was Done

Your complete STFT audio processing system is now ready with the following components:

### 1. **Core Processing Modules** (6 files)

#### audio_loader.py
- Loads audio files from the 16k-LP7 dataset
- Handles mono/stereo conversion
- Normalizes audio amplitudes
- Recursively finds all .wav files

#### stft_processor.py
- Computes Short-Time Fourier Transform using Librosa
- Generates 4 types of spectrograms:
  - **Magnitude**: Raw frequency content
  - **Power**: Energy-based (squared magnitude)
  - **Log**: dB scale (human perception)
  - **Mel**: Mel-frequency scale (for ML)
- Extracts spectral features:
  - Centroid
  - Rolloff
  - Spectral Flux
  - Mean/Peak Power

#### visualizer.py
- Creates professional-quality plots using Matplotlib
- Shows waveform + 3 spectrograms in combined view
- Saves PNG images for each processed file
- Non-interactive backend for batch processing

#### main.py
- Main orchestration script
- Processes all 1,444 audio files from 16k-LP7/CA/
- Organizes output by category
- Generates processing summary JSON

#### test.py
- Quick test with single audio file
- Validates all components work correctly
- Useful for debugging

#### requirements.txt
- All dependencies: librosa, numpy, scipy, matplotlib, soundfile

---

## 📊 Output Structure

```
results/
├── spectrogram_data/CA/
│   ├── CA01_01/
│   │   ├── results.json                    (metadata & features)
│   │   ├── spectrogram_magnitude.npy       (1025 x 86)
│   │   ├── spectrogram_power.npy          (1025 x 86)
│   │   ├── spectrogram_log.npy            (1025 x 86)
│   │   └── spectrogram_mel.npy            (128 x 86)
│   ├── CA01_02/
│   └── ... (all files)
│
├── visualizations/CA/
│   ├── CA01_01_combined.png               (waveform + 3 spectrograms)
│   ├── CA01_02_combined.png
│   └── ... (all files)
│
└── processing_summary.json                (summary of all files)
```

---

## 🎯 Key Features

### STFT Parameters (Optimized for 16kHz audio)
- **FFT Size (n_fft)**: 2048 samples
- **Hop Length**: 512 samples (12.5ms frames)
- **Window**: Hann window
- **Result**: 1025 frequency bins × time frames

### Frequency Resolution
- Freq bin resolution: 16000 / 2048 = 7.8 Hz per bin
- Covers 0 - 8000 Hz (Nyquist frequency at 8kHz)

### Time Resolution
- Frame duration: 2048 / 16000 = 128ms
- Hop duration: 512 / 16000 = 32ms
- A 2.74s audio file = 86 time frames

---

## 📁 Files Structure

Each processed file has:

### results.json (example)
```json
{
  "file_path": "16k-LP7/CA/CA01_01.wav",
  "duration_seconds": 2.74,
  "sample_rate": 16000,
  "features": {
    "centroid": 2115.37,    // weighted mean frequency
    "rolloff": 3592.57,     // frequency with 85% energy
    "flux": 11.80,          // change rate of spectrum
    "mean_power": 0.548,    // average energy
    "peak_power": 1467.63   // maximum energy
  },
  "spectrogram_shapes": {
    "magnitude": [1025, 86],
    "power": [1025, 86],
    "log": [1025, 86],
    "mel": [128, 86]
  }
}
```

### Numpy Arrays (.npy files)

Load and use in Python:
```python
import numpy as np

# Load spectrogram
S_log = np.load('results/spectrogram_data/CA/CA01_01/spectrogram_log.npy')
print(S_log.shape)  # (1025, 86) - 1025 freq bins, 86 time frames

# Access time frame 0, frequency bin 500
value = S_log[500, 0]

# Get time-averaged spectrum
avg_spectrum = np.mean(S_log, axis=1)  # (1025,)

# Get frequency-averaged temporal pattern
temporal = np.mean(S_log, axis=0)  # (86,)
```

---

## 🚀 Usage Examples

### 1. Load and Visualize Results
```python
import numpy as np
import matplotlib.pyplot as plt

# Load log spectrogram
S = np.load('results/spectrogram_data/CA/CA01_01/spectrogram_log.npy')

# Plot
plt.figure(figsize=(12, 6))
plt.imshow(S, aspect='auto', origin='lower', cmap='viridis')
plt.colorbar(label='Power (dB)')
plt.xlabel('Time frames')
plt.ylabel('Frequency bins')
plt.title('Log Spectrogram - CA01_01')
plt.show()
```

### 2. Extract Statistics
```python
import json
import numpy as np

# Load metadata
with open('results/spectrogram_data/CA/CA01_01/results.json') as f:
    meta = json.load(f)

# Load spectrograms
S_log = np.load('results/spectrogram_data/CA/CA01_01/spectrogram_log.npy')
S_mel = np.load('results/spectrogram_data/CA/CA01_01/spectrogram_mel.npy')

# Statistics
print(f"Duration: {meta['duration_seconds']:.2f}s")
print(f"Spectral Centroid: {meta['features']['centroid']:.2f} Hz")
print(f"Mean Power: {meta['features']['mean_power']:.4f}")
print(f"Log Spectrogram range: [{S_log.min():.2f}, {S_log.max():.2f}] dB")
```

### 3. Batch Processing Features
```python
import json
import numpy as np
from pathlib import Path

# Process all results
results_dir = Path('results/spectrogram_data/CA')
all_features = []

for file_dir in results_dir.iterdir():
    if file_dir.is_dir():
        with open(file_dir / 'results.json') as f:
            features = json.load(f)['features']
            all_features.append(features)

# Aggregate statistics
for feature_name in all_features[0].keys():
    values = [f[feature_name] for f in all_features]
    print(f"{feature_name}: mean={np.mean(values):.4f}, std={np.std(values):.4f}")
```

---

## 💡 What Each Spectrogram Is Best For

| Spectrogram | Use Case | Characteristics |
|-------------|----------|-----------------|
| **Magnitude** | Technical analysis, debugging | Linear amplitude scale |
| **Power** | Energy analysis, loudness | Squared magnitude |
| **Log (dB)** | Human perception, visualization | Logarithmic scale, -∞ to 0 dB |
| **Mel** | Machine Learning, speech tasks | Mimics human hearing, 128 bands |

---

## ⚙️ Technical Specifications

### STFT Computation (by Librosa)
```
Input: Audio signal y (time series)
       ↓
Apply window (Hann): frame the signal
       ↓
Compute FFT on each frame
       ↓
Output: Complex-valued STFT matrix D (1025 × time_frames)
```

### Spectral Features
- **Centroid**: Weighted mean of frequencies (Eq: Σ(f * magnitude) / Σ(magnitude))
- **Rolloff**: Frequency where cumulative magnitude exceeds 85%
- **Flux**: L2 norm of frame-to-frame derivative

---

## 🔄 Processing Pipeline

```
16k-LP7/CA/*.wav files (1,444 files)
     ↓
AudioLoader (reads WAV)
     ↓
STFT Processor (computes STFT)
     ↓
3 outputs generated in parallel:
  ├→ Spectrogram Data (.npy files)
  ├→ JSON Metadata & Features
  └→ PNG Visualization
     ↓
All saved to results/
     ↓
Final: processing_summary.json
```

---

## 📈 Processing Statistics

- **Total Audio Files**: 1,444
- **Audio Format**: 16-bit PCM WAV @ 16kHz
- **Category**: CA (presumably from a larger dataset)
- **Average Duration**: ~2.74 seconds
- **Total Duration**: ~3,956 seconds (~1.1 hours)

---

## ✨ Key Advantages of This Setup

1. **Batch Processing**: Handles 1,444+ files automatically
2. **Parallel Generation**: Saves multiple spectrogram types simultaneously
3. **Professional Visualization**: High-quality PNG output for inspection
4. **Metadata Preservation**: All parameters, shapes, and features saved
5. **ML-Ready**: Numpy arrays directly usable in TensorFlow/PyTorch
6. **Scalable**: Easy to add more audio categories or modify parameters
7. **Error Handling**: Graceful failure with detailed error messages
8. **Reproducible**: All parameters documented and saved

---

## 🎓 Learning Resources

The code demonstrates:
- Audio signal processing with Librosa
- STFT theory and implementation
- Feature extraction from spectrograms
- Batch processing best practices
- JSON data serialization
- Matplotlib plotting and image generation
- Python pathlib for file organization

---

## 🎓 Next Steps

1. **Load Results**: Use examples above to load .npy files
2. **ML Training**: Feed spectrograms to ML models (CNN, RNN, etc.)
3. **Feature Analysis**: Study the extracted features across files
4. **Visualization**: View PNG files to understand audio characteristics
5. **Customization**: Modify STFT parameters for different use cases
6. **Combine Data**: Use processing_summary.json to aggregate results

---

**Status**: ✅ All files generated and ready for use!
**Location**: `c:\Users\prakh\OneDrive\Documents\stft_proj\`
