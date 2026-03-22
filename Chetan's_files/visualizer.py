"""
Visualization module for STFT results
"""
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import librosa
import librosa.display
import numpy as np
from pathlib import Path


class STFTVisualizer:
    """Visualize STFT results"""

    def __init__(self, figsize=(14, 8), dpi=100):
        """
        Initialize visualizer

        Args:
            figsize: Figure size (width, height)
            dpi: DPI for saved figures
        """
        self.figsize = figsize
        self.dpi = dpi

    def plot_waveform(self, y, sr, title="Waveform"):
        """
        Plot audio waveform

        Args:
            y: Audio time series
            sr: Sample rate
            title: Plot title

        Returns:
            fig, ax
        """
        fig, ax = plt.subplots(figsize=(14, 4))
        time = np.arange(len(y)) / sr
        ax.plot(time, y, linewidth=0.5)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig, ax

    def plot_magnitude_spectrogram(self, D, sr, hop_length, title="Magnitude Spectrogram"):
        """
        Plot magnitude spectrogram

        Args:
            D: STFT matrix
            sr: Sample rate
            hop_length: Hop length
            title: Plot title

        Returns:
            fig, ax
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        S = np.abs(D)
        img = librosa.display.specshow(
            S,
            sr=sr,
            hop_length=hop_length,
            x_axis='time',
            y_axis='hz',
            ax=ax
        )
        ax.set_title(title)
        fig.colorbar(img, ax=ax, format='%+2.0f')
        plt.tight_layout()
        return fig, ax

    def plot_log_spectrogram(self, D, sr, hop_length, title="Log Spectrogram (dB)"):
        """
        Plot log-scaled spectrogram

        Args:
            D: STFT matrix
            sr: Sample rate
            hop_length: Hop length
            title: Plot title

        Returns:
            fig, ax
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        S_db = librosa.power_to_db(np.abs(D) ** 2, ref=np.max)
        img = librosa.display.specshow(
            S_db,
            sr=sr,
            hop_length=hop_length,
            x_axis='time',
            y_axis='hz',
            ax=ax,
            cmap='magma'
        )
        ax.set_title(title)
        fig.colorbar(img, ax=ax, format='%+2.0f dB')
        plt.tight_layout()
        return fig, ax

    def plot_mel_spectrogram(self, y, sr, hop_length, n_mels=128, title="Mel Spectrogram"):
        """
        Plot mel spectrogram

        Args:
            y: Audio time series
            sr: Sample rate
            hop_length: Hop length
            n_mels: Number of mel bands
            title: Plot title

        Returns:
            fig, ax
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        S = librosa.feature.melspectrogram(
            y=y,
            sr=sr,
            n_fft=2048,
            hop_length=hop_length,
            n_mels=n_mels
        )
        S_db = librosa.power_to_db(S, ref=np.max)
        img = librosa.display.specshow(
            S_db,
            sr=sr,
            hop_length=hop_length,
            x_axis='time',
            y_axis='mel',
            ax=ax,
            cmap='viridis'
        )
        ax.set_title(title)
        fig.colorbar(img, ax=ax, format='%+2.0f dB')
        plt.tight_layout()
        return fig, ax

    def plot_combined(self, y, D, sr, hop_length, filename=None):
        """
        Plot waveform + spectrograms in one figure

        Args:
            y: Audio time series
            D: STFT matrix
            sr: Sample rate
            hop_length: Hop length
            filename: Save to file if provided

        Returns:
            fig
        """
        fig = plt.figure(figsize=(15, 10))

        # Waveform
        ax1 = plt.subplot(3, 1, 1)
        time = np.arange(len(y)) / sr
        ax1.plot(time, y, linewidth=0.5, color='steelblue')
        ax1.set_ylabel('Amplitude')
        ax1.set_title('Waveform')
        ax1.grid(True, alpha=0.3)

        # Magnitude spectrogram
        ax2 = plt.subplot(3, 1, 2)
        S = np.abs(D)
        img2 = librosa.display.specshow(
            S,
            sr=sr,
            hop_length=hop_length,
            x_axis='time',
            y_axis='hz',
            ax=ax2,
            cmap='magma'
        )
        ax2.set_title('Magnitude Spectrogram')
        fig.colorbar(img2, ax=ax2, format='%+2.0f')

        # Log spectrogram
        ax3 = plt.subplot(3, 1, 3)
        S_db = librosa.power_to_db(np.abs(D) ** 2, ref=np.max)
        img3 = librosa.display.specshow(
            S_db,
            sr=sr,
            hop_length=hop_length,
            x_axis='time',
            y_axis='hz',
            ax=ax3,
            cmap='viridis'
        )
        ax3.set_title('Log Spectrogram (dB)')
        fig.colorbar(img3, ax=ax3, format='%+2.0f dB')

        plt.tight_layout()

        if filename:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(filename, dpi=self.dpi, bbox_inches='tight')
            print(f"  [OK] Saved visualization: {filename}")

        return fig

    @staticmethod
    def close_all():
        """Close all matplotlib figures"""
        plt.close('all')
