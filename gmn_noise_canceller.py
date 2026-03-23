"""
Noise Canceller based on Generalized-Mean Neural Networks (GMN)
================================================================
Implementation of the paper:
    "Noise-Canceller based on Generalized-Mean Neural Networks"
    Agya Mishra, R.N. Yadav, D.K. Trivedi
    Indian Journal of Computer Science and Engineering, Vol 1 No 2, 125-135

Core equations implemented:
    Eq(1) - Generalized Mean:     GM  = (1/N * Σ x_j^r)^(1/r)
    Eq(2) - Aggregation function: y   = (Σ w_j * x_j^r + w_o)^(1/r)
    Eq(3) - Hidden net input:     neti = (Σ w_ij * x_j^r + w_oi)^(1/r)
    Eq(4) - Hidden output:        yj  = sigmoid(neti)
    Eq(5) - Output activation:    yk  = sigmoid(netk)
    Eq(6) - Output net input:     netk = (Σ w_ki * yi^r + w_ok)^(1/r)

Requirements:
    torch>=2.0.0
    numpy>=1.24.0
    scipy>=1.10.0
    matplotlib>=3.7.0
    soundfile>=0.12.0
    librosa>=0.10.0
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────────────────────────────────────
# 1. GMN LAYER — implements Eq(2) / Eq(3) / Eq(6)
#    net = ( Σ_{j=1}^{N}  w_ij * x_j^r  +  w_oi )^(1/r)
# ─────────────────────────────────────────────────────────────────────────────

class GMNLayer(nn.Module):
    """
    Generalized-Mean Neuron layer.

    Each neuron computes (paper Eq. 2 & 3):
        net_i = ( Σ_{j=1}^{N}  w_ij * x_j^r  +  w_oi )^(1/r)

    r is a *learnable* generalisation parameter (shared across the layer).
    When r→1  it approaches the standard weighted sum (MLP).
    When r→2  it gives a quadratic (power-2) aggregation.
    The paper fixes r=0.9 in simulations; you can freeze it via:
        layer.r.requires_grad_(False)

    Parameters
    ----------
    in_features  : N — number of inputs  (= delay_taps in the canceller)
    out_features : M or K — number of neurons in this layer
    r            : initial generalisation parameter (default 0.9, per paper)
    eps          : numerical guard inside the r-th root
    """

    def __init__(self, in_features: int, out_features: int,
                 r: float = 0.9, eps: float = 1e-8):
        super().__init__()
        self.in_features  = in_features
        self.out_features = out_features
        self.eps          = eps

        # r is a scalar learnable parameter (same for every neuron — paper §4)
        self.r = nn.Parameter(torch.tensor(float(r), dtype=torch.float32))

        # w_ij  weight matrix   shape: (out_features × in_features)
        self.weight = nn.Parameter(torch.empty(out_features, in_features))
        # w_oi  bias vector     shape: (out_features,)
        self.bias   = nn.Parameter(torch.zeros(out_features))

        nn.init.xavier_uniform_(self.weight)

    # ── Aggregation function  (paper Eq. 2 / 3 / 6) ─────────────────
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x   : (batch_size, in_features)
        out : (batch_size, out_features)

        Steps:
            1. x_r  = sign(x) * |x + eps|^r        ← raise to r-th power
            2. inner = x_r @ W^T + b                ← weighted sum  (Eq. 3)
            3. out   = sign(inner) * |inner|^(1/r)  ← r-th root     (Eq. 3)
        """
        r = self.r

        # Step 1 — element-wise x^r with sign preservation
        #   Using sign(x)*|x|^r allows negative inputs & arbitrary real r
        x_r = torch.sign(x) * (x.abs() + self.eps).pow(r)        # (B, N)

        # Step 2 — Σ w_ij * x_j^r  +  w_oi
        inner = x_r @ self.weight.t() + self.bias                 # (B, M)

        # Step 3 — (·)^(1/r)  with sign preservation
        out = torch.sign(inner) * (inner.abs() + self.eps).pow(1.0 / r)
        return out                                                 # (B, M)


# ─────────────────────────────────────────────────────────────────────────────
# 2. GMN NETWORK — multilayer feed-forward  (paper Fig. 3, Section 4)
#    Architecture: N  →  h1 × … × hk  →  K
# ─────────────────────────────────────────────────────────────────────────────

class GMNNetwork(nn.Module):
    """
    Multilayer feed-forward network built entirely from GMNLayer neurons.

    Topology  (paper Section 4):
        Input (N)  →  [GMNLayer + Sigmoid] × num_hidden  →  [GMNLayer + Sigmoid]

    The sigmoid after each GMNLayer corresponds to f(·) in Eq(4) and Eq(5).
    r is shared across all layers (per paper: "same for every neuron").

    Parameters
    ----------
    layer_sizes : list of ints  e.g. [3, 10, 1]
                  [input_dim, hidden1, ..., output_dim]
    r           : generalisation parameter
    """

    def __init__(self, layer_sizes: list, r: float = 0.9):
        super().__init__()
        self.gmn_layers = nn.ModuleList([
            GMNLayer(layer_sizes[i], layer_sizes[i + 1], r=r)
            for i in range(len(layer_sizes) - 1)
        ])
        self.act = nn.Sigmoid()    # f(·) — Eq(4) & Eq(5)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for layer in self.gmn_layers:
            x = self.act(layer(x))
        return x


# ─────────────────────────────────────────────────────────────────────────────
# 3. NOISE CANCELLER  (paper Fig. 1 architecture)
# ─────────────────────────────────────────────────────────────────────────────

class NoiseCanceller:
    """
    Adaptive noise canceller using the GMN network.

    Architecture (paper Fig. 1):

        noisy ──┬─────────────────────────────────────► (+) ──► output ≈ clean
                │                                         ▲
                ├─► delay t-1 ─┐                          │
                ├─► delay t-2  ├──► GMN ──► noise_est ──►(−)
                └─► delay t-k ─┘

    The GMN learns to estimate the noise component.  The clean signal is
    recovered as:  e(t) = noisy(t) − GMN_output(t)

    MSE criterion  (paper §5): minimise E[e²] → e → 0 (paper condition)

    Parameters
    ----------
    delay_taps  : k  (number of delayed copies, default 3)
    hidden_size : M  (hidden layer neurons)
    r           : generalisation parameter (paper uses 0.9)
    lr          : gradient-descent learning rate
    device      : 'cpu' or 'cuda'
    """

    def __init__(self, delay_taps: int = 3, hidden_size: int = 10,
                 r: float = 0.9, lr: float = 0.01, device: str = "cpu"):
        self.delay_taps = delay_taps
        self.device     = torch.device(device)

        # Architecture: [k  →  hidden  →  1]
        self.model = GMNNetwork(
            layer_sizes=[delay_taps, hidden_size, 1], r=r
        ).to(self.device)

        self.optimizer    = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion    = nn.MSELoss()
        self.loss_history = []

    # ── Build delay-tap input matrix  (Fig. 1: t-1, t-2, …, t-k) ────
    def _delay_matrix(self, signal: np.ndarray) -> torch.Tensor:
        """Returns (T-k, k) tensor; row t = [x(t-1), x(t-2), …, x(t-k)]."""
        k, T = self.delay_taps, len(signal)
        rows = [signal[t - k: t][::-1].copy() for t in range(k, T)]
        return torch.tensor(np.array(rows), dtype=torch.float32).to(self.device)

    # ── Training ──────────────────────────────────────────────────────
    def train(self, noisy_signal: np.ndarray,
              n_epochs: int = 500, verbose: bool = True):
        """
        Train on the noisy signal.

        The network is trained so that its output estimates the noisy signal
        itself; the error residual then converges to the clean signal
        (standard ANC formulation, §2 of the paper).
        """
        X = self._delay_matrix(noisy_signal)                       # (T-k, k)
        y = torch.tensor(
            noisy_signal[self.delay_taps:], dtype=torch.float32
        ).unsqueeze(1).to(self.device)                             # (T-k, 1)

        self.model.train()
        self.loss_history = []

        for epoch in range(1, n_epochs + 1):
            self.optimizer.zero_grad()
            pred = self.model(X)
            loss = self.criterion(pred, y)
            loss.backward()
            self.optimizer.step()
            self.loss_history.append(loss.item())
            if verbose and epoch % 50 == 0:
                print(f"  Epoch {epoch:5d}/{n_epochs}  |  MSE = {loss.item():.6e}")

        return self.loss_history

    # ── Inference ─────────────────────────────────────────────────────
    @torch.no_grad()
    def cancel_noise(self, noisy_signal: np.ndarray):
        """
        Returns
        -------
        detected  : recovered clean signal   e = noisy − GMN_output
        noise_est : noise estimate from the GMN
        """
        self.model.eval()
        X         = self._delay_matrix(noisy_signal)
        noise_est = self.model(X).squeeze().cpu().numpy()
        detected  = noisy_signal[self.delay_taps:] - noise_est
        return detected, noise_est


# ─────────────────────────────────────────────────────────────────────────────
# 4. MLP BASELINE  (standard network for GMN vs MLP comparison, §6)
# ─────────────────────────────────────────────────────────────────────────────

class MLPNoiseCanceller:
    """Standard MLP noise canceller for comparison with GMN (paper §6)."""

    def __init__(self, delay_taps: int = 3, hidden_size: int = 10,
                 lr: float = 0.01, device: str = "cpu"):
        self.delay_taps   = delay_taps
        self.device       = torch.device(device)
        self.model        = nn.Sequential(
            nn.Linear(delay_taps, hidden_size), nn.Sigmoid(),
            nn.Linear(hidden_size, 1),          nn.Sigmoid()
        ).to(self.device)
        self.optimizer    = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion    = nn.MSELoss()
        self.loss_history = []

    def _delay_matrix(self, signal):
        k, T = self.delay_taps, len(signal)
        rows = [signal[t - k: t][::-1].copy() for t in range(k, T)]
        return torch.tensor(np.array(rows), dtype=torch.float32).to(self.device)

    def train(self, noisy_signal, n_epochs=500, verbose=True):
        X = self._delay_matrix(noisy_signal)
        y = torch.tensor(
            noisy_signal[self.delay_taps:], dtype=torch.float32
        ).unsqueeze(1).to(self.device)
        self.model.train()
        self.loss_history = []
        for epoch in range(1, n_epochs + 1):
            self.optimizer.zero_grad()
            loss = self.criterion(self.model(X), y)
            loss.backward()
            self.optimizer.step()
            self.loss_history.append(loss.item())
            if verbose and epoch % 50 == 0:
                print(f"  Epoch {epoch:5d}/{n_epochs}  |  MSE = {loss.item():.6e}")
        return self.loss_history

    @torch.no_grad()
    def cancel_noise(self, noisy_signal):
        self.model.eval()
        noise_est = self.model(self._delay_matrix(noisy_signal)).squeeze().cpu().numpy()
        return noisy_signal[self.delay_taps:] - noise_est, noise_est


# ─────────────────────────────────────────────────────────────────────────────
# 5. SIGNAL GENERATORS  (matching paper examples §5)
# ─────────────────────────────────────────────────────────────────────────────

def add_white_gaussian_noise(signal: np.ndarray, snr_db: float) -> np.ndarray:
    """Add White Gaussian Noise at a given SNR in dB."""
    sig_power   = np.mean(signal ** 2)
    noise_power = sig_power / (10 ** (snr_db / 10.0))
    noise       = np.random.normal(0.0, np.sqrt(noise_power), signal.shape)
    return signal + noise


def generate_s1(N: int = 600) -> np.ndarray:
    """Example-1  S1(t) = 40/t  (paper §5, normalised)."""
    t = np.linspace(0.1, 6.0, N)
    s = 40.0 / t
    return (s - s.mean()) / (s.std() + 1e-8)


def generate_s2(N: int = 500) -> np.ndarray:
    """Example-2  S2(t) = sin(2π·0.015·(N-1)) * 0.5·cos(2π·0.008·(N-1))."""
    t = np.arange(N)
    return np.sin(2 * np.pi * 0.015 * t) * 0.5 * np.cos(2 * np.pi * 0.008 * t)


def generate_s3(N: int = 600) -> np.ndarray:
    """
    Example-3  Synthetic ECG-like signal (paper §5, S3(t) = ECG signal).
    Approximates a multi-frequency cardiac waveform with varying amplitude.
    """
    t        = np.linspace(0.0, 6.0, N)
    ecg      = (0.6 * np.sin(2 * np.pi * 1.2 * t)
                + 0.3 * np.sin(2 * np.pi * 2.4 * t)
                + 0.1 * np.sin(2 * np.pi * 4.8 * t))
    envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 0.1 * t)
    ecg     *= envelope
    return ecg / (np.std(ecg) + 1e-8)


# ─────────────────────────────────────────────────────────────────────────────
# 6. VISUALISATION  (matching paper Fig-4 … Fig-12)
# ─────────────────────────────────────────────────────────────────────────────

def plot_performance(original, noisy, detected, title="Noise-canceller performance",
                     save_path=None):
    """Three-panel plot: original / noisy / original-vs-detected  (Fig-4,5,6)."""
    fig, axes = plt.subplots(3, 1, figsize=(10, 9))
    fig.suptitle(title, fontsize=12, fontweight='bold')

    t_full   = np.linspace(0, 6, len(original))
    t_detect = np.arange(len(detected))

    axes[0].plot(t_full, original, 'b', lw=1.2)
    axes[0].set_title("Original signal"); axes[0].grid(alpha=.3)

    axes[1].plot(t_full, noisy, 'b', lw=0.8)
    axes[1].set_title("Noisy signal"); axes[1].grid(alpha=.3)

    orig_trim = original[-len(detected):]
    norm = lambda v: (v - v.min()) / (v.ptp() + 1e-8)
    axes[2].plot(t_detect, norm(orig_trim), 'r--', lw=1.2, label='original')
    axes[2].plot(t_detect, norm(detected),  'k:',  lw=1.2, label='detected')
    axes[2].set_title("Performance of Noise-canceller")
    axes[2].set_xlabel("Samples"); axes[2].legend(); axes[2].grid(alpha=.3)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  Saved → {save_path}")
    plt.show()


def plot_learning_curves(gmn_loss, mlp_loss, title="Learning curve GMN vs MLP",
                          save_path=None):
    """Fig-7 / Fig-9 / Fig-11."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(gmn_loss, label='GMN', lw=1.5)
    ax.plot(mlp_loss, label='MLP', lw=1.5, ls='--')
    ax.set(title=title, xlabel="Iterations", ylabel="MSE")
    ax.legend(); ax.grid(alpha=.3)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight'); print(f"  Saved → {save_path}")
    plt.show()


def plot_mse_vs_snr(snr_vals, gmn_mse, mlp_mse, title="MSE vs SNR", save_path=None):
    """Fig-8 / Fig-10 / Fig-12."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(snr_vals, gmn_mse, 'b-o', label='GMN', lw=1.5, ms=5)
    ax.plot(snr_vals, mlp_mse, 'r--s', label='MLP', lw=1.5, ms=5)
    ax.set(title=title, xlabel="SNR (dB)", ylabel="MSE")
    ax.legend(); ax.grid(alpha=.3)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight'); print(f"  Saved → {save_path}")
    plt.show()


# ─────────────────────────────────────────────────────────────────────────────
# 7. AUDIO FILE SUPPORT  (librosa / soundfile)
# ─────────────────────────────────────────────────────────────────────────────

def cancel_noise_from_audio(audio_path: str,
                             output_path: str = "denoised.wav",
                             snr_db_added: float = None,
                             delay_taps: int = 5,
                             hidden_size: int = 20,
                             r: float = 0.9,
                             n_epochs: int = 300,
                             lr: float = 0.005,
                             train_samples: int = 2048):
    """
    Apply the GMN noise canceller to a real audio file via librosa/soundfile.

    Parameters
    ----------
    audio_path    : path to .wav / .mp3 / .flac
    output_path   : output denoised .wav
    snr_db_added  : if set, artificially adds WGN at this SNR (for testing)
    train_samples : how many samples to use for training
    """
    try:
        import librosa
        import soundfile as sf
    except ImportError:
        raise ImportError("Run:  pip install librosa soundfile")

    print(f"\n[Audio] Loading: {audio_path}")
    signal, sr = librosa.load(audio_path, sr=None, mono=True)
    print(f"  SR={sr} Hz | Duration={len(signal)/sr:.2f}s")

    if snr_db_added is not None:
        signal = add_white_gaussian_noise(signal, snr_db_added)
        print(f"  Added WGN at {snr_db_added} dB")

    canceller = NoiseCanceller(delay_taps=delay_taps, hidden_size=hidden_size,
                                r=r, lr=lr)
    print(f"[Audio] Training on first {train_samples} samples …")
    canceller.train(signal[:train_samples], n_epochs=n_epochs, verbose=False)
    print(f"  Final MSE: {canceller.loss_history[-1]:.6e}")

    denoised, _ = canceller.cancel_noise(signal)
    denoised   /= np.max(np.abs(denoised)) + 1e-8

    import soundfile as sf
    sf.write(output_path, denoised, sr)
    print(f"[Audio] Saved → {output_path}")
    return denoised, sr


# ─────────────────────────────────────────────────────────────────────────────
# 8. FULL EXPERIMENT RUNNER
# ─────────────────────────────────────────────────────────────────────────────

def run_experiment(signal_fn, label: str,
                   N: int = 600, snr_db: float = 16.0,
                   n_epochs: int = 500, delay_taps: int = 3,
                   hidden_size: int = 10, r: float = 0.9, lr: float = 0.01,
                   snr_range=None, out_dir: str = "."):
    """
    Full experiment matching paper §5–§6:
      1. Generate signal, add WGN
      2. Train GMN + MLP cancellers
      3. Plot performance, learning curves, MSE-vs-SNR
      4. Print parameter table (MSE / Mean / Variance at each SNR)
    """
    if snr_range is None:
        snr_range = [0, 4, 8, 12, 16, 20]

    print("\n" + "=" * 65)
    print(f"  EXPERIMENT: {label}")
    print("=" * 65)

    np.random.seed(42)
    original = signal_fn(N)
    noisy    = add_white_gaussian_noise(original, snr_db)

    print("\n[GMN] Training …")
    gmn      = NoiseCanceller(delay_taps=delay_taps, hidden_size=hidden_size,
                               r=r, lr=lr)
    gmn_loss = gmn.train(noisy, n_epochs=n_epochs, verbose=True)
    gmn_det, _ = gmn.cancel_noise(noisy)

    print("\n[MLP] Training …")
    mlp      = MLPNoiseCanceller(delay_taps=delay_taps, hidden_size=hidden_size,
                                  lr=lr)
    mlp_loss = mlp.train(noisy, n_epochs=n_epochs, verbose=True)

    plot_performance(original, noisy, gmn_det,
                     title=f"Noise-canceller using GMN — {label}",
                     save_path=f"{out_dir}/perf_{label}.png")
    plot_learning_curves(gmn_loss, mlp_loss,
                          title=f"Learning Curve GMN vs MLP — {label}",
                          save_path=f"{out_dir}/lcurve_{label}.png")

    # MSE-vs-SNR table
    gmn_mse_list, mlp_mse_list = [], []
    header = (f"\n{'SNR':>6} | {'GMN MSE':>12} {'GMN Mean':>10} {'GMN Var':>10}"
              f" | {'MLP MSE':>12} {'MLP Mean':>10} {'MLP Var':>10}")
    print(header)
    print("-" * len(header))

    for snr in snr_range:
        np.random.seed(42)
        nsy = add_white_gaussian_noise(original, snr)

        g = NoiseCanceller(delay_taps=delay_taps, hidden_size=hidden_size, r=r, lr=lr)
        g.train(nsy, n_epochs=n_epochs, verbose=False)
        gd, _ = g.cancel_noise(nsy)
        ot    = original[-len(gd):]
        gm    = float(np.mean((gd - ot) ** 2))
        gmn_mse_list.append(gm)

        m = MLPNoiseCanceller(delay_taps=delay_taps, hidden_size=hidden_size, lr=lr)
        m.train(nsy, n_epochs=n_epochs, verbose=False)
        md, _ = m.cancel_noise(nsy)
        mm    = float(np.mean((md - ot) ** 2))
        mlp_mse_list.append(mm)

        print(f"{snr:>6} | {gm:>12.4e} {float(np.mean(gd)):>10.4f} {float(np.var(gd)):>10.4f}"
              f" | {mm:>12.4e} {float(np.mean(md)):>10.4f} {float(np.var(md)):>10.4f}")

    plot_mse_vs_snr(snr_range, gmn_mse_list, mlp_mse_list,
                    title=f"MSE vs SNR — {label}",
                    save_path=f"{out_dir}/mse_snr_{label}.png")

    return gmn, mlp, gmn_loss, mlp_loss


# ─────────────────────────────────────────────────────────────────────────────
# 9. ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os, time

    OUT = "gmn_results"
    os.makedirs(OUT, exist_ok=True)

    COMMON = dict(delay_taps=3, hidden_size=10, r=0.9, lr=0.01, out_dir=OUT)

    t0 = time.time()

    # Example-1 : S1(t) = 40/t
    run_experiment(generate_s1, "S1_40_over_t", N=600, snr_db=16,
                   n_epochs=500, **COMMON)

    # Example-2 : sine × cosine  (comm. signal)
    run_experiment(generate_s2, "S2_sin_cos", N=500, snr_db=16,
                   n_epochs=500, **COMMON)

    # Example-3 : ECG-like (1000 iterations as in the paper)
    run_experiment(generate_s3, "S3_ECG", N=600, snr_db=16,
                   n_epochs=1000, **COMMON)

    print(f"\n✓  All done in {time.time()-t0:.1f}s — results in ./{OUT}/")
