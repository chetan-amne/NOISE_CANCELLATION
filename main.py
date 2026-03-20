"""
Main STFT processing script
Processes audio files from 16k-LP7 dataset
"""
import os
import sys
from pathlib import Path
from audio_loader import AudioLoader
from stft_processor import STFTProcessor
from visualizer import STFTVisualizer
import json
import numpy as np


def create_output_dirs():
    """Create output directories for results"""
    dirs = [
        'results/spectrogram_data',
        'results/visualizations',
        'results/features',
    ]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("[OK] Output directories created\n")


def process_single_audio(file_path, audio_loader, stft_processor, visualizer, output_base):
    """
    Process a single audio file

    Args:
        file_path: Path to audio file
        audio_loader: AudioLoader instance
        stft_processor: STFTProcessor instance
        visualizer: STFTVisualizer instance
        output_base: Base output directory
    """
    print(f"\nProcessing: {file_path}")
    print("=" * 60)

    # Load audio
    y, sr = audio_loader.load_audio(file_path)
    if y is None:
        return None

    # Compute STFT
    D, freq, time = stft_processor.compute_stft(y, sr)
    if D is None:
        return None

    # Get relative path for organizing output
    relative_path = Path(file_path).relative_to('16k-LP7')
    stem = relative_path.stem
    category = relative_path.parent.name

    # Create output paths
    output_dir = Path(output_base) / category / stem
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process spectrograms
    print("  Generating spectrograms...")
    S_magnitude = stft_processor.get_magnitude_spectrogram(D)
    S_power = stft_processor.get_power_spectrogram(D)
    S_log = stft_processor.get_log_spectrogram(D)
    S_mel, mel_freq = stft_processor.get_mel_spectrogram(y, sr, n_mels=128)

    # Extract features
    print("  Extracting features...")
    features = stft_processor.extract_features(D, sr)

    # Prepare results
    results = {
        'file_path': file_path,
        'duration_seconds': float(len(y) / sr),
        'sample_rate': sr,
        'stft_params': {
            'n_fft': stft_processor.n_fft,
            'hop_length': stft_processor.hop_length,
            'win_length': stft_processor.win_length,
            'window': stft_processor.window,
        },
        'spectrogram_shapes': {
            'magnitude': S_magnitude.shape,
            'power': S_power.shape,
            'log': S_log.shape,
            'mel': S_mel.shape,
        },
        'features': {k: float(np.mean(v)) if isinstance(v, np.ndarray) else float(v)
                     for k, v in features.items()},
        'frequency_range': {
            'min_hz': float(freq[0]),
            'max_hz': float(freq[-1]),
            'n_freq_bins': len(freq),
        },
        'time_range': {
            'duration_s': float(time[-1]),
            'n_frames': len(time),
        }
    }

    # Save results
    print("  Saving results...")
    stft_processor.save_results(results, str(output_dir / 'results.json'))

    # Save spectrograms as numpy
    np.save(str(output_dir / 'spectrogram_magnitude.npy'), S_magnitude)
    np.save(str(output_dir / 'spectrogram_power.npy'), S_power)
    np.save(str(output_dir / 'spectrogram_log.npy'), S_log)
    np.save(str(output_dir / 'spectrogram_mel.npy'), S_mel)
    print(f"  [OK] Saved spectrogram data")

    # Create visualizations
    print("  Creating visualizations...")
    viz_file = str(output_dir.parent / f"{stem}_combined.png")
    visualizer.plot_combined(y, D, sr, stft_processor.hop_length, viz_file)
    visualizer.close_all()

    print(f"  [OK] All results saved to: {output_dir}")
    return results


def process_all_audio(input_dir="16k-LP7", output_dir="results"):
    """
    Process all audio files in directory

    Args:
        input_dir: Input directory with audio files
        output_dir: Output directory for results
    """
    print("\n" + "=" * 60)
    print("STFT AUDIO PROCESSING")
    print("=" * 60 + "\n")

    # Initialize components
    audio_loader = AudioLoader(sr=16000)
    stft_processor = STFTProcessor(
        n_fft=2048,
        hop_length=512,
        win_length=2048,
        window='hann'
    )
    visualizer = STFTVisualizer(figsize=(14, 8), dpi=100)

    # Create output directories
    create_output_dirs()

    # Get audio files
    audio_files = audio_loader.get_audio_files(input_dir, ext='.wav')
    if not audio_files:
        print("[ERROR] No audio files found!")
        return

    print(f"Starting processing of {len(audio_files)} files...\n")

    # Process each file
    all_results = []
    for i, file_path in enumerate(audio_files, 1):
        try:
            result = process_single_audio(
                file_path,
                audio_loader,
                stft_processor,
                visualizer,
                output_dir
            )
            if result:
                all_results.append(result)
            print(f"Progress: {i}/{len(audio_files)}")
        except Exception as e:
            print(f"[ERROR] Failed to process {file_path}: {e}")
            import traceback
            traceback.print_exc()

    # Save summary
    print("\n" + "=" * 60)
    print(f"Processing complete! Processed {len(all_results)}/{len(audio_files)} files")
    print("=" * 60)

    summary = {
        'total_files': len(audio_files),
        'processed_files': len(all_results),
        'output_directory': output_dir,
        'files': all_results
    }

    with open(f'{output_dir}/processing_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\n[OK] Summary saved to: {output_dir}/processing_summary.json")


if __name__ == "__main__":
    try:
        process_all_audio()
        print("\n[OK] STFT processing completed successfully!")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
