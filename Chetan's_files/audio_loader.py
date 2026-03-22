"""
Audio loading and preprocessing module
"""
import librosa
import numpy as np
from pathlib import Path
import os


class AudioLoader:
    """Load and preprocess audio files"""

    def __init__(self, sr=16000):
        """
        Initialize AudioLoader

        Args:
            sr: Sample rate (default 16000 for 16k dataset)
        """
        self.sr = sr

    def load_audio(self, file_path, mono=True):
        """
        Load audio file

        Args:
            file_path: Path to audio file
            mono: Convert to mono if True

        Returns:
            y: Audio time series
            sr: Sample rate
        """
        try:
            y, sr = librosa.load(file_path, sr=self.sr, mono=mono)
            print(f"[OK] Loaded: {os.path.basename(file_path)} | Duration: {len(y)/sr:.2f}s")
            return y, sr
        except Exception as e:
            print(f"[ERROR] Error loading {file_path}: {e}")
            return None, None

    def get_audio_files(self, directory, ext='.wav'):
        """
        Get all audio files from directory

        Args:
            directory: Path to audio directory
            ext: File extension to search for

        Returns:
            List of audio file paths
        """
        audio_files = []
        path = Path(directory)

        for file in sorted(path.rglob(f'*{ext}')):
            audio_files.append(str(file))

        print(f"[INFO] Found {len(audio_files)} audio files")
        return audio_files

    def normalize_audio(self, y):
        """
        Normalize audio to [-1, 1]

        Args:
            y: Audio time series

        Returns:
            Normalized audio
        """
        return y / (np.max(np.abs(y)) + 1e-8)
