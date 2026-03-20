# 🎯 QUICK REFERENCE CARD - STFT PROJECT

## 30-Second Summary

```
Maine 1,444 audio files par STFT lagaya:
├─ Audio load
├─ STFT compute
├─ 4 spectrograms generate (magnitude, power, log, mel)
├─ 5 features extract (centroid, rolloff, flux, mean/peak power)
├─ Results save (numpy, JSON, PNG)
└─ Output: 150+ MB organized data
```

---

## What is STFT?

| Concept | Meaning |
|---------|---------|
| **STFT** | Short-Time Fourier Transform |
| **Matlab** | Time domain ko frequency domain mein convert karna |
| **Result** | 2D grid: Time vs Frequency |
| **Use** | Audio analysis, ML, signal processing |

---

## 4 Spectrograms Generated

| Type | Shape | Use | Format |
|------|-------|-----|--------|
| **Magnitude** | (1025, 86) | |STFT| raw values | Direct |
| **Power** | (1025, 86) | Energy-based \|STFT\|² | Energy |
| **Log (dB)** | (1025, 86) | Human perception 20*log10 | Best for viewing |
| **Mel** | (128, 86) | ML, speech proc. | ML-optimized |

---

## 5 Features Extracted

| Feature | Meaning | Example Value | Interpretation |
|---------|---------|----------------|-----------------|
| **Centroid** | Center freq | 2115 Hz | Mid-high sounds |
| **Rolloff** | 85% energy freq | 3592 Hz | High freq presence |
| **Flux** | Change rate | 11.8 | Moderate variation |
| **Mean Power** | Avg loudness | 0.548 | Normal level |
| **Peak Power** | Max intensity | 1467 | Max point |

---

## File Structure

```
results/
├── [CATEGORY]/ (CA, CB, FA, FB, etc.)
│   ├── [FILE_ID]/ (CA01_01, CA01_02, etc.)
│   │   ├── results.json
│   │   ├── spectrogram_magnitude.npy
│   │   ├── spectrogram_power.npy
│   │   ├── spectrogram_log.npy
│   │   └── spectrogram_mel.npy
│   │
│   ├── [FILE_ID]_combined.png
│   └── ... (repeat for all)
└── processing_summary.json

TOTAL: 1,444 × 4 .npy files + 1,444 PNG + 1,444 JSON
```

---

## Load Data in Python

```python
# Quick load
import numpy as np
import json

# Numpy array
S = np.load('results/CA/CA01_01/spectrogram_log.npy')
print(S.shape)  # (1025, 86)

# JSON metadata
with open('results/CA/CA01_01/results.json') as f:
    data = json.load(f)
print(data['features']['centroid'])  # 2115.37
```

---

## Key Stats

| Metric | Value |
|--------|-------|
| Total Files | 1,444 |
| Categories | 18+ |
| Frequency Bins | 1025 |
| Sample Rate | 16,000 Hz |
| Frequency Range | 0-8000 Hz |
| Avg Duration | 2.7 seconds |
| Avg Centroid | ~2000 Hz |
| Output Size | 150+ MB |
| Processing Time | ~45 min |

---

## Frequency Reference

```
Human hearing range: 20 Hz - 20,000 Hz
Your sample rate: 16,000 Hz
Your Nyquist freq: 8,000 Hz
Your freq resolution: 7.8 Hz/bin

Practical bands:
├─ Bass: 0-250 Hz
├─ Low-mid: 250-1000 Hz
├─ Mid: 1000-2000 Hz
├─ High-mid: 2000-4000 Hz
└─ Treble: 4000-8000 Hz
```

---

## Time Reference

```
Frame details:
├─ Hop length: 512 samples
├─ Sample rate: 16,000 Hz
├─ Frame duration: 32 ms (512/16000)

For 2.74 second audio:
├─ Total samples: 43,840
├─ Total frames: 86
├─ Frame 0: 0-128 ms
├─ Frame 43: ~1370 ms
├─ Frame 86: ~2750 ms
```

---

## Use Cases

### Speech Recognition
```
Audio → STFT → Mel spectrogram → Neural Net → Text
```

### Music Classification
```
Audio → Features → Classifier → Genre
```

### Emotion Detection
```
Voice → STFT → Centroid/Rolloff → Emotion
```

### Anomaly Detection
```
Signals → STFT → Features → Outlier detection
```

---

## Common Questions

**Q: Kaunsa spectrogram use karu?**
- Visualization ke liye: Log spectrogram
- ML training ke liye: Mel spectrogram
- Technical analysis: Magnitude spectrogram

**Q: Frequency bin convert kaise karu?**
- Frequency (Hz) = bin_number × (sample_rate / n_fft)
- Frequency (Hz) = bin_number × (16000 / 2048)
- Frequency (Hz) = bin_number × 7.8

**Q: Time frame convert kaise karu?**
- Second = frame_number × (hop_length / sample_rate)
- Second = frame_number × (512 / 16000)
- Second = frame_number × 0.032

**Q: Sabhi 1,444 files ka average kaise nikalu?**
```python
import json, numpy as np
from pathlib import Path

all_centroids = []
for json_file in Path('results').rglob('results.json'):
    with open(json_file) as f:
        all_centroids.append(json.load(f)['features']['centroid'])

print(f"Average centroid: {np.mean(all_centroids):.2f} Hz")
```

---

## Parameters Used

| Parameter | Value | Note |
|-----------|-------|------|
| n_fft | 2048 | FFT size |
| hop_length | 512 | Frame shift |
| window | hann | Window function |
| sr | 16000 | Sample rate |
| n_mels | 128 | Mel bands |

---

## Output Checklist

- ✅ 1,444 × magnitude spectrograms
- ✅ 1,444 × power spectrograms
- ✅ 1,444 × log spectrograms
- ✅ 1,444 × mel spectrograms
- ✅ 1,444 × results.json files
- ✅ 1,444 × PNG visualizations
- ✅ 1 × processing_summary.json

Total: ~7,664 files generated!

---

## Key Takeaways

1. **STFT Transform** = Audio को time-frequency domain में बदलना
2. **4 Spectrograms** = अलग-अलग perspectives से देखना
3. **5 Features** = Sound की important properties
4. **1,444 Files** = Complete dataset processed
5. **ML Ready** = Data directly ML models में use हो सकता है

---

**Ab samajh gaye? 😊**

Agar kisi ko samjhana hai:
- "Mene audio STFT से analyze किया"
- "हर file से 4 spectrograms बनाए"
- "128 frequency bands × time frames की grid बनी"
- "5 important features extract किए"
- "सब कुछ numpy arrays में save है ML के लिए"
