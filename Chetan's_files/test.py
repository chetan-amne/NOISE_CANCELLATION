"""
Quick test script - Process one audio file
"""
import sys
from pathlib import Path
from audio_loader import AudioLoader
from stft_processor import STFTProcessor
from visualizer import STFTVisualizer
import json
import numpy as np


def test_single_file():
    """Test processing with a single audio file"""
    print("\n" + "=" * 60)
    print("STFT TEST - Single File Processing")
    print("=" * 60 + "\n")

    # Find first audio file
    audio_files = list(Path('16k-LP7').rglob('*.wav'))
    if not audio_files:
        print("[ERROR] No audio files found!")
        return False

    test_file = str(audio_files[0])
    print(f"Testing with: {test_file}\n")

    try:
        # Initialize components
        audio_loader = AudioLoader(sr=16000)
        stft_processor = STFTProcessor(
            n_fft=2048,
            hop_length=512,
            win_length=2048,
            window='hann'
        )
        visualizer = STFTVisualizer()

        # Load audio
        print("Step 1: Loading audio...")
        y, sr = audio_loader.load_audio(test_file)
        if y is None:
            print("[ERROR] Failed to load audio")
            return False

        # Compute STFT
        print("\nStep 2: Computing STFT...")
        D, freq, time = stft_processor.compute_stft(y, sr)
        if D is None:
            print("[ERROR] Failed to compute STFT")
            return False

        # Get spectrograms
        print("\nStep 3: Generating spectrograms...")
        S_magnitude = stft_processor.get_magnitude_spectrogram(D)
        S_log = stft_processor.get_log_spectrogram(D)
        S_mel, _ = stft_processor.get_mel_spectrogram(y, sr, n_mels=128)
        print(f"  [OK] Magnitude shape: {S_magnitude.shape}")
        print(f"  [OK] Log shape: {S_log.shape}")
        print(f"  [OK] Mel shape: {S_mel.shape}")

        # Extract features
        print("\nStep 4: Extracting features...")
        features = stft_processor.extract_features(D, sr)
        for name, value in features.items():
            if isinstance(value, np.ndarray):
                print(f"  [OK] {name}: mean={np.mean(value):.4f}")
            else:
                print(f"  [OK] {name}: {value:.4f}")

        # Create visualization
        print("\nStep 5: Creating visualization...")
        Path('results/test').mkdir(parents=True, exist_ok=True)
        fig = visualizer.plot_combined(
            y, D, sr, stft_processor.hop_length,
            'results/test/test_output.png'
        )
        visualizer.close_all()

        # Print summary
        print("\n" + "=" * 60)
        print("[OK] TEST PASSED - All components working!")
        print("=" * 60)
        print("\nNext step: Run 'python main.py' to process all files")
        return True

    except Exception as e:
        print(f"\n[ERROR] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_single_file()
    sys.exit(0 if success else 1)
