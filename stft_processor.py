"""
STFT (Short-Time Fourier Transform) processing module
"""
import numpy as np
import librosa
import librosa.display
from scipy import signal
import json
from pathlib import Path


class STFTProcessor:
    """Process audio using STFT"""

    def __init__(self, n_fft=2048, hop_length=512, win_length=2048, window='hann'):
        """
        Initialize STFT processor

        Args:
            n_fft: FFT size
            hop_length: Number of samples between successive frames
            win_length: Window size
            window: Window function type
        """
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.win_length = win_length
        self.window = window

    def compute_stft(self, y, sr):
        """
        Compute STFT of audio

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            D: STFT matrix (complex)
            freq: Frequency values
            time: Time values
        """
        try:
            # Compute STFT
            D = librosa.stft(
                y,
                n_fft=self.n_fft,
                hop_length=self.hop_length,
                win_length=self.win_length,
                window=self.window,
                center=True
            )

            # Get frequency and time values
            freq = librosa.fft_frequencies(sr=sr, n_fft=self.n_fft)
            time = librosa.frames_to_time(np.arange(D.shape[1]), sr=sr, hop_length=self.hop_length)

            print(f"  [OK] STFT computed: Shape {D.shape} | Time: {time[-1]:.2f}s")
            return D, freq, time
        except Exception as e:
            print(f"  [ERROR] Error computing STFT: {e}")
            return None, None, None

    def get_magnitude_spectrogram(self, D):
        """
        Get magnitude spectrogram from STFT

        Args:
            D: STFT matrix

        Returns:
            S: Magnitude spectrogram
        """
        S = np.abs(D)
        return S

    def get_power_spectrogram(self, D):
        """
        Get power spectrogram from STFT

        Args:
            D: STFT matrix

        Returns:
            S_power: Power spectrogram (magnitude squared)
        """
        S = np.abs(D) ** 2
        return S

    def get_log_spectrogram(self, D, ref=np.max, amin=1e-5):
        """
        Get log-scaled spectrogram

        Args:
            D: STFT matrix or magnitude spectrogram
            ref: Reference power
            amin: Minimum amplitude

        Returns:
            S_log: Log-scaled spectrogram in dB
        """
        S = np.abs(D) if isinstance(D, np.complexfloating) else D
        S_log = librosa.power_to_db(S ** 2, ref=ref, amin=amin)
        return S_log

    def get_mel_spectrogram(self, y, sr, n_mels=128):
        """
        Get mel spectrogram

        Args:
            y: Audio time series
            sr: Sample rate
            n_mels: Number of mel bands

        Returns:
            S_mel: Mel spectrogram
            mel_freq: Mel frequency bins
        """
        S = librosa.feature.melspectrogram(
            y=y,
            sr=sr,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            n_mels=n_mels
        )
        S_db = librosa.power_to_db(S, ref=np.max)
        mel_freq = librosa.mel_frequencies(n_mels=n_mels, fmin=0, fmax=sr/2)

        return S_db, mel_freq

    def extract_features(self, D, sr):
        """
        Extract spectral features from STFT

        Args:
            D: STFT matrix
            sr: Sample rate

        Returns:
            dict: Dictionary of features
        """
        S = np.abs(D)
        S_power = S ** 2

        features = {
            'centroid': librosa.feature.spectral_centroid(S=S, sr=sr)[0],
            'rolloff': librosa.feature.spectral_rolloff(S=S, sr=sr)[0],
            'flux': self._spectral_flux(S),
            'mean_power': np.mean(S_power),
            'peak_power': np.max(S_power),
        }

        return features

    @staticmethod
    def _spectral_flux(S):
        """
        Calculate spectral flux (rate of change of spectrogram)

        Args:
            S: Magnitude spectrogram

        Returns:
            flux: Spectral flux values
        """
        diff = np.sqrt(np.sum(np.diff(S, axis=1) ** 2, axis=0))
        return diff

    def save_results(self, results, output_file):
        """
        Save STFT results to JSON

        Args:
            results: Dictionary with results
            output_file: Output file path
        """
        try:
            # Convert numpy arrays to lists for JSON serialization
            results_serializable = {}
            for key, value in results.items():
                if isinstance(value, np.ndarray):
                    results_serializable[key] = value.tolist()
                elif isinstance(value, dict):
                    results_serializable[key] = {
                        k: v.tolist() if isinstance(v, np.ndarray) else v
                        for k, v in value.items()
                    }
                else:
                    results_serializable[key] = value

            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(results_serializable, f, indent=2)
            print(f"  [OK] Saved: {output_file}")
        except Exception as e:
            print(f"  [ERROR] Error saving results: {e}")
