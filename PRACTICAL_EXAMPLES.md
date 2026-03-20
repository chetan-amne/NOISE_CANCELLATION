# PRACTICAL EXAMPLES - STFT DATA KAI USE KAISE KARTE HO?

## 🔥 Example 1: Ek File ka Data Load Karna

```python
import numpy as np
import json
import matplotlib.pyplot as plt

# Path
file_path = 'results/CA/CA01_01'

# 1. JSON metadata load karo
with open(f'{file_path}/results.json') as f:
    metadata = json.load(f)

print("=== FILE INFO ===")
print(f"Duration: {metadata['duration_seconds']:.2f} seconds")
print(f"Sample Rate: {metadata['sample_rate']} Hz")
print(f"Total Frequency Bins: {metadata['frequency_range']['n_freq_bins']}")
print(f"Total Time Frames: {metadata['time_range']['n_frames']}")

# 2. Log spectrogram load karo
S_log = np.load(f'{file_path}/spectrogram_log.npy')
print(f"\n=== SPECTROGRAM ===")
print(f"Shape: {S_log.shape}")  # (1025, 86)
print(f"Min value: {S_log.min():.2f} dB")
print(f"Max value: {S_log.max():.2f} dB")
print(f"Mean value: {S_log.mean():.2f} dB")

# 3. Features dekho
features = metadata['features']
print(f"\n=== EXTRACTED FEATURES ===")
print(f"Spectral Centroid: {features['centroid']:.2f} Hz")
print(f"Spectral Rolloff: {features['rolloff']:.2f} Hz")
print(f"Mean Power: {features['mean_power']:.4f}")
print(f"Peak Power: {features['peak_power']:.2f}")
```

**Output aayega:**
```
=== FILE INFO ===
Duration: 2.74 seconds
Sample Rate: 16000 Hz
Total Frequency Bins: 1025
Total Time Frames: 86

=== SPECTROGRAM ===
Shape: (1025, 86)
Min value: -77.35 dB
Max value: -18.42 dB
Mean value: -65.23 dB

=== EXTRACTED FEATURES ===
Spectral Centroid: 2115.37 Hz
Spectral Rolloff: 3592.57 Hz
Mean Power: 0.5484
Peak Power: 1467.6326
```

---

## 🎨 Example 2: Spectrogram Plot Banao

```python
import numpy as np
import matplotlib.pyplot as plt
import librosa.display

# Load karo
S_log = np.load('results/CA/CA01_01/spectrogram_log.npy')

# Plot karo (simple)
fig, ax = plt.subplots(figsize=(12, 6))

# Display spectrogram
img = librosa.display.specshow(
    S_log,
    sr=16000,
    hop_length=512,
    x_axis='time',
    y_axis='hz',
    ax=ax,
    cmap='viridis'  # Color map
)

ax.set_title('Log Spectrogram - CA01_01', fontsize=14)
fig.colorbar(img, ax=ax, format='%+2.0f dB')
plt.tight_layout()
plt.savefig('my_spectrogram.png', dpi=150)
plt.show()
```

**Ye banane se:**
- X-axis: Time (0 to 2.74 seconds)
- Y-axis: Frequency (0 to 8000 Hz)
- Color: Power in dB (-80 to -18)

---

## 📊 Example 3: Sabhi Files ka Average Features

```python
import json
import numpy as np
from pathlib import Path
import pandas as pd

# Results ka path
results_dir = Path('results')

# Data collect karna
all_data = []

for category_dir in results_dir.iterdir():
    if not category_dir.is_dir():
        continue

    category = category_dir.name

    for file_dir in category_dir.iterdir():
        if not file_dir.is_dir():
            continue

        json_file = file_dir / 'results.json'
        if json_file.exists():
            with open(json_file) as f:
                data = json.load(f)

            # Extract important info
            all_data.append({
                'category': category,
                'file': file_dir.name,
                'duration': data['duration_seconds'],
                'centroid': data['features']['centroid'],
                'rolloff': data['features']['rolloff'],
                'flux': data['features']['flux'],
                'mean_power': data['features']['mean_power'],
                'peak_power': data['features']['peak_power'],
            })

# DataFrame banao
df = pd.DataFrame(all_data)

# Analysis
print("=== STATISTICS BY CATEGORY ===")
print(df.groupby('category')[['centroid', 'rolloff', 'mean_power']].describe())

print("\n=== OVERALL STATISTICS ===")
print(f"Total Files: {len(df)}")
print(f"Avg Duration: {df['duration'].mean():.2f} seconds")
print(f"Avg Centroid: {df['centroid'].mean():.2f} Hz")
print(f"Avg Rolloff: {df['rolloff'].mean():.2f} Hz")
print(f"Avg Mean Power: {df['mean_power'].mean():.4f}")

# CSV mein save karo
df.to_csv('audio_features_summary.csv', index=False)
print("\nSaved to: audio_features_summary.csv")
```

---

## 🤖 Example 4: Simple ML Model - Classification

```python
import numpy as np
import json
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Data collect karna
X = []  # Features
y = []  # Labels (category)

results_dir = Path('results')

for category_dir in results_dir.iterdir():
    if not category_dir.is_dir():
        continue

    category = category_dir.name

    for file_dir in category_dir.iterdir():
        if not file_dir.is_dir():
            continue

        json_file = file_dir / 'results.json'
        if json_file.exists():
            with open(json_file) as f:
                data = json.load(f)

            # Features nikalo
            features = [
                data['features']['centroid'],
                data['features']['rolloff'],
                data['features']['flux'],
                data['features']['mean_power'],
                data['features']['peak_power'],
            ]

            X.append(features)
            y.append(category)

# Convert to numpy
X = np.array(X)
y = np.array(y)

print(f"Total samples: {len(X)}")
print(f"Features per sample: {X.shape[1]}")
print(f"Categories: {np.unique(y)}")

# Split karo
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Normalize karo
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Model train karo
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Predictions
y_pred = clf.predict(X_test)

# Results
accuracy = accuracy_score(y_test, y_pred)
print(f"\nAccuracy: {accuracy:.2%}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Feature importance
print("\nFeature Importance:")
feature_names = ['Centroid', 'Rolloff', 'Flux', 'Mean Power', 'Peak Power']
for name, importance in zip(feature_names, clf.feature_importances_):
    print(f"  {name}: {importance:.4f}")
```

---

## 🎵 Example 5: Mel Spectrogram Load Karna

```python
import numpy as np
import matplotlib.pyplot as plt
import librosa.display

# Load mel spectrogram
S_mel = np.load('results/CA/CA01_01/spectrogram_mel.npy')

print(f"Shape: {S_mel.shape}")  # (128, 86)
# 128 mel frequency bands
# 86 time frames

# Plot karo
fig, ax = plt.subplots(figsize=(12, 6))

img = librosa.display.specshow(
    S_mel,
    sr=16000,
    hop_length=512,
    x_axis='time',
    y_axis='mel',  # Mel scale!
    ax=ax,
    cmap='magma'
)

ax.set_title('Mel Spectrogram - CA01_01', fontsize=14)
fig.colorbar(img, ax=ax, format='%+2.0f dB')
plt.tight_layout()
plt.savefig('mel_spectrogram.png', dpi=150)
plt.show()
```

---

## 🔍 Example 6: Ek Specific Frequency Band Analyze Karna

```python
import numpy as np
import matplotlib.pyplot as plt

# Load log spectrogram
S_log = np.load('results/CA/CA01_01/spectrogram_log.npy')

# Total frequencies: 1025
# Each bin: 7.8 Hz

# Speech frequencies usually: 300-3000 Hz
# 300 Hz = bin 300/7.8 ≈ 38
# 3000 Hz = bin 3000/7.8 ≈ 385

speech_freq_start = int(300 / 7.8)  # bin 38
speech_freq_end = int(3000 / 7.8)    # bin 385

# Speech band nikalo
S_speech = S_log[speech_freq_start:speech_freq_end, :]

print(f"Original shape: {S_log.shape}")
print(f"Speech band shape: {S_speech.shape}")
print(f"Speech band mean power: {S_speech.mean():.2f} dB")

# Plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# Full spectrogram
ax1.imshow(S_log, aspect='auto', origin='lower', cmap='viridis')
ax1.set_title('Full Spectrogram')
ax1.axhline(y=speech_freq_start, color='r', linestyle='--', label='Speech band')
ax1.axhline(y=speech_freq_end, color='r', linestyle='--')
ax1.legend()

# Speech band only
ax2.imshow(S_speech, aspect='auto', origin='lower', cmap='viridis')
ax2.set_title('Speech Frequency Band Only (300-3000 Hz)')

plt.tight_layout()
plt.savefig('speech_band_analysis.png', dpi=150)
plt.show()
```

---

## 📈 Example 7: Temporal Pattern Analyze Karna

```python
import numpy as np
import matplotlib.pyplot as plt

# Load spectrogram
S_log = np.load('results/CA/CA01_01/spectrogram_log.npy')

# Time ke saath kya badal raha hai ye dekho
time_averaged = S_log.mean(axis=0)  # Sabhi frequencies ka average
print(f"Time pattern shape: {time_averaged.shape}")  # (86,)
print(f"Pattern: {time_averaged}")

# Plot karo
fig, ax = plt.subplots(figsize=(12, 4))

time_frames = np.arange(len(time_averaged))
seconds = time_frames * (512 / 16000)  # Convert frames to seconds

ax.plot(seconds, time_averaged, linewidth=2, color='steelblue')
ax.fill_between(seconds, time_averaged, alpha=0.3)
ax.set_xlabel('Time (seconds)')
ax.set_ylabel('Average Power (dB)')
ax.set_title('Sound Energy Over Time')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('temporal_pattern.png', dpi=150)
plt.show()

# Peak time nikalo
max_idx = np.argmax(time_averaged)
max_second = seconds[max_idx]
print(f"\nLoudest moment at: {max_second:.2f} seconds")
print(f"Power: {time_averaged[max_idx]:.2f} dB")
```

---

## 🏆 Example 8: Sabhi Categories Compare Karna

```python
import numpy as np
import json
from pathlib import Path
import matplotlib.pyplot as plt

# Data collect
categories_stats = {}

results_dir = Path('results')

for category_dir in results_dir.iterdir():
    if not category_dir.is_dir():
        continue

    category = category_dir.name
    centroids = []

    for file_dir in category_dir.iterdir():
        if not file_dir.is_dir():
            continue

        json_file = file_dir / 'results.json'
        if json_file.exists():
            with open(json_file) as f:
                data = json.load(f)
                centroids.append(data['features']['centroid'])

    if centroids:
        categories_stats[category] = {
            'mean': np.mean(centroids),
            'std': np.std(centroids),
            'count': len(centroids),
        }

# Plot
categories = list(categories_stats.keys())
means = [categories_stats[c]['mean'] for c in categories]
stds = [categories_stats[c]['std'] for c in categories]

fig, ax = plt.subplots(figsize=(14, 6))

bars = ax.bar(categories, means, yerr=stds, capsize=10, alpha=0.7, color='steelblue')
ax.set_ylabel('Average Spectral Centroid (Hz)')
ax.set_title('Spectral Centroid Comparison Across Categories')
ax.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar, mean in zip(bars, means):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{mean:.0f}',
            ha='center', va='bottom')

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('categories_comparison.png', dpi=150)
plt.show()

print("Category Comparison:")
for cat, stats in sorted(categories_stats.items()):
    print(f"{cat}: mean={stats['mean']:.2f} Hz, std={stats['std']:.2f}, n={stats['count']}")
```

---

## ✅ QUICK REFERENCE - Commands

```bash
# Python script run karna
python load_and_analyze.py

# Numpy array inspect using Python
python -c "import numpy as np; S = np.load('results/CA/CA01_01/spectrogram_log.npy'); print(S.shape)"

# JSON pretty print
python -c "import json; f=open('results/CA/CA01_01/results.json'); print(json.dumps(json.load(f), indent=2))"

# Count total files generated
find results -name "*.npy" | wc -l
```

---

## 🎓 TIPS & TRICKS

### Tip 1: Numpy Broadcasting
```python
# Sabhi frames ko normalize karna
S_normalized = (S_log - S_log.min()) / (S_log.max() - S_log.min())
# Result: 0 to 1 range
```

### Tip 2: Downsampling spectrogram
```python
# Time dimension ko compress karna (faster processing)
S_compressed = S_log[:, ::4]  # Har 4th frame lo
# Original: (1025, 86)
# Compressed: (1025, 22)
```

### Tip 3: Frequency bands
```python
# Bass (0-250 Hz)
bass = S_log[:int(250/7.8), :]

# Mid (250-2000 Hz)
mid = S_log[int(250/7.8):int(2000/7.8), :]

# Treble (2000-8000 Hz)
treble = S_log[int(2000/7.8):, :]

# Alag alag analyze kar sakta ho
```

### Tip 4: Smooth spectrogram (denoise)
```python
from scipy.ndimage import gaussian_filter

S_smooth = gaussian_filter(S_log, sigma=1.0)
# Result: Noisy parts reduce ho jayenge
```

---

Ab ye sab examples run kar ke dekh! 😎
