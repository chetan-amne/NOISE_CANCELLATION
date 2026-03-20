# STFT Audio Processing - Setup Guide

## ✓ Files Created

Your project now has the following structure with 6 complete modules:

### Core Modules:
1. **main.py** - Main processing script (processes all audio files)
2. **audio_loader.py** - Audio file loading and preprocessing
3. **stft_processor.py** - STFT computation and feature extraction
4. **visualizer.py** - Spectrogram visualization
5. **test.py** - Quick test with a single file
6. **requirements.txt** - Python dependencies

### Documentation:
- **README.md** - Full documentation

---

## ⚡ Quick Start

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install librosa numpy scipy matplotlib soundfile
```

**Note**: Installation may take 2-3 minutes for first-time setup (especially librosa)

### Step 2: Verify Installation
```bash
python -c "import librosa; print('✓ Ready!')"
```

### Step 3: Test with One File
```bash
python test.py
```

This will:
- Load one audio sample from 16k-LP7/CA/
- Compute STFT
- Extract features
- Create a visualization in results/test/test_output.png

### Step 4: Process All Files
```bash
python main.py
```

This will process ALL audio files and create:
- Spectrogram data (numpy arrays)
- Visualizations (PNG images)
- Feature data (JSON)
- Summary report

---

## 📊 What You'll Get

After running `python main.py`, in the `results/` folder:

```
results/
├── spectrogram_data/          # Numpy arrays
│   └── CA/
│       └── CA01_01/
│           ├── results.json           # Metadata & features
│           ├── spectrogram_magnitude.npy
│           ├── spectrogram_power.npy
│           ├── spectrogram_log.npy
│           └── spectrogram_mel.npy
│
├── visualizations/            # PNG plots
│   └── CA/
│       ├── CA01_01_combined.png
│       ├── CA01_02_combined.png
│       └── ...
│
└── processing_summary.json    # Summary of all files
```

---

## 🎯 What Each File Contains

### Spectrogram Files (.npy)

1. **spectrogram_magnitude.npy**
   - Shape: (frequency_bins, time_frames)
   - Values: |STFT|
   - Use: Raw magnitude analysis

2. **spectrogram_power.npy**
   - Shape: (frequency_bins, time_frames)
   - Values: |STFT|²
   - Use: Energy-based analysis

3. **spectrogram_log.npy**
   - Shape: (frequency_bins, time_frames)
   - Values: 20*log₁₀(|STFT|) in dB
   - Use: Human perception-aligned analysis

4. **spectrogram_mel.npy**
   - Shape: (128_mel_bands, time_frames)
   - Values: Mel-scale power in dB
   - Use: Machine learning applications

### Results JSON

Each `results.json` contains:
```json
{
  "file_path": "16k-LP7/CA/CA01_01.wav",
  "duration_seconds": 8.45,
  "sample_rate": 16000,
  "stft_params": {...},
  "features": {
    "centroid": 2150.5,
    "rolloff": 4500.2,
    "flux": 125.3,
    "mean_power": 0.045,
    "peak_power": 2.15
  },
  "spectrogram_shapes": {...},
  "frequency_range": {...}
}
```

---

## 🔧 Customization

Edit `main.py` to change STFT parameters:

```python
stft_processor = STFTProcessor(
    n_fft=2048,          # FFT size (increase for more frequency detail)
    hop_length=512,      # Frame hop (decrease for more time detail)
    win_length=2048,     # Window size
    window='hann'        # Window type
)
```

---

## 📝 Features Extracted

From each spectrogram:

| Feature | Description | Use Case |
|---------|-------------|----------|
| **Centroid** | Weighted average frequency | Determine "brightness" of sound |
| **Rolloff** | Frequency with 85% energy | Detect presence of high frequencies |
| **Flux** | Change in spectrum over time | Detect onset/transitions |
| **Mean Power** | Average energy | Overall loudness indicator |
| **Peak Power** | Maximum energy | Dynamic range indicator |

---

## ❓ Troubleshooting

### "ModuleNotFoundError: No module named 'librosa'"
```bash
pip install librosa --upgrade
```

### "No audio files found"
```bash
ls 16k-LP7/CA/
# Should show: CA01_01.wav, CA01_02.wav, etc.
```

### Memory issues with large files
- Increase `hop_length` to 1024
- Decrease `n_fft` to 1024

### Slow processing
- Reduce number of files for testing
- Edit `main.py` to process only first N files:
```python
for file_path in audio_files[:10]:  # Process only first 10
```

---

## 🚀 Next Steps

1. After files process, visualizations are in `results/visualizations/CA/`
2. Load spectrogram data in Python:
```python
import numpy as np
S = np.load('results/spectrogram_data/CA/CA01_01/spectrogram_log.npy')
print(S.shape)  # (frequency, time)
```

3. Use for machine learning:
   - Music classification
   - Speech recognition
   - Anomaly detection
   - etc.

---

## 📚 References

- [Librosa Docs](https://librosa.org/)
- [STFT Explained](https://en.wikipedia.org/wiki/Short-time_Fourier_transform)
- [Mel-scale](https://en.wikipedia.org/wiki/Mel_scale)

---

## ✅ You're All Set!

Now run:
```bash
python test.py      # Test first
python main.py      # Process all files
```
