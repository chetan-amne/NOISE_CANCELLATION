# STFT Audio Processing Project

Short-Time Fourier Transform (STFT) processing for 16k-LP7 audio dataset.

## Project Structure

```
stft_proj/
├── main.py                 # Main processing script
├── audio_loader.py         # Audio loading module
├── stft_processor.py       # STFT computation module
├── visualizer.py           # Visualization module
├── requirements.txt        # Python dependencies
├── 16k-LP7/               # Audio dataset
│   └── CA/                # Category folders with .wav files
└── results/               # Output directory (created after processing)
    ├── spectrogram_data/  # Numpy spectrogram files
    ├── visualizations/    # PNG plots
    └── features/          # Feature JSON files
```

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install librosa numpy scipy matplotlib soundfile
```

### 2. Verify Audio Files

Check that audio files are present:
```bash
ls 16k-LP7/CA/
```

## Usage

### Run STFT Processing

```bash
python main.py
```

This will:
1. Load all audio files from `16k-LP7/`
2. Compute STFT for each file
3. Generate spectrograms (magnitude, power, log-scaled, mel)
4. Extract spectral features
5. Create visualizations
6. Save results to `results/` directory

## Output

### Spectrogram Data
Located in `results/spectrogram_data/[category]/[filename]/`:
- `spectrogram_magnitude.npy` - Magnitude spectrogram
- `spectrogram_power.npy` - Power spectrogram (squared magnitude)
- `spectrogram_log.npy` - Log-scaled spectrogram (dB)
- `spectrogram_mel.npy` - Mel-scale spectrogram
- `results.json` - Detailed metadata and features

### Visualizations
Located in `results/visualizations/[category]/`:
- `[filename]_combined.png` - Combined plot with waveform + spectrograms

### Summary
- `results/processing_summary.json` - Summary of all processed files

## STFT Parameters

Default configuration in `main.py`:
- **n_fft**: 2048 (FFT size)
- **hop_length**: 512 (samples between frames)
- **window**: hann (window function)
- **Sample rate**: 16000 Hz

## What is STFT?

Short-Time Fourier Transform decomposes audio into:
- **Time**: Audio broken into overlapping windows
- **Frequency**: Each window analyzed for frequency content
- **Magnitude**: Strength of each frequency component
- **Phase**: Not typically visualized, but computed

## Key Spectrograms

1. **Magnitude Spectrogram**: |STFT(x)|
2. **Power Spectrogram**: |STFT(x)|² (energy)
3. **Log Spectrogram**: 20*log₁₀(|STFT(x)|) in dB
4. **Mel Spectrogram**: STFT mapped to mel-frequency scale (human hearing)

## Features Extracted

For each audio file:
- **Spectral Centroid**: Weighted mean of frequencies
- **Spectral Rolloff**: Frequency below which most energy is concentrated
- **Spectral Flux**: Rate of change of spectrum over time
- **Mean Power**: Average power in spectrogram
- **Peak Power**: Maximum power in spectrogram

## Troubleshooting

### Missing Dependencies
```bash
pip install librosa --upgrade
```

### Audio Files Not Found
Ensure files are in `16k-LP7/CA/` directory with `.wav` extension

### Memory Issues
For large files, reduce `n_fft` or process files individually

### Matplotlib Backend Issues
On headless systems, backend is set to 'Agg' (non-interactive)

## Example Processing Single File

```python
from audio_loader import AudioLoader
from stft_processor import STFTProcessor
from visualizer import STFTVisualizer

# Load
loader = AudioLoader(sr=16000)
y, sr = loader.load_audio('16k-LP7/CA/CA01_01.wav')

# Process
processor = STFTProcessor()
D, freq, time = processor.compute_stft(y, sr)
S_log = processor.get_log_spectrogram(D)

# Visualize
viz = STFTVisualizer()
fig, ax = viz.plot_log_spectrogram(D, sr, processor.hop_length)
plt.savefig('spectrogram.png')
```

## References

- [Librosa Documentation](https://librosa.org/)
- [STFT Explanation](https://en.wikipedia.org/wiki/Short-time_Fourier_transform)
- [Mel Scale](https://en.wikipedia.org/wiki/Mel_scale)
