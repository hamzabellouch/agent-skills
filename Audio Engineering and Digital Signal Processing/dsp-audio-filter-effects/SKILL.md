---
name: dsp-audio-filter-effects
metadata:
  category: Audio Engineering and Digital Signal Processing
description: Apply digital signal processing (DSP) algorithms in Python and C++ for audio filtering (IIR, FIR, Butterworth, Chebyshev), spectral analysis via Fast Fourier Transform (FFT), dynamic range compression, and modulation effects. Trigger when developing audio DSP algorithms, sound effects, or analyzing audio signals.
compatibility: Python 3.10+, NumPy, SciPy (scipy.signal), C++17
---

# Digital Signal Processing (DSP) Audio Filter & Effects Skill Guide

This skill covers the design, mathematical formulation, and software implementation of digital audio filters, dynamic range compressors, and spectral transforms.

---

## 1. Filter Classifications: IIR vs FIR

```text
+-----------------------------------+-----------------------------------+
| Infinite Impulse Response (IIR)   | Finite Impulse Response (FIR)     |
+-----------------------------------+-----------------------------------+
| - Feedback (Recursive)            | - Feedforward only (Non-recursive)|
| - Low computational cost (CPU)    | - Linear phase response available |
| - Examples: Butterworth, Biquad   | - Inherently stable               |
| - Ideal for real-time live audio  | - Ideal for mastering & phase-    |
|   filters & equalizers            |   critical crossover filters      |
+-----------------------------------+-----------------------------------+
```

---

## 2. Production Code Implementations

### A. Butterworth Bandpass & Highpass Filters (Python / SciPy)

```python
import numpy as np
from scipy import signal


class AudioFilterEngine:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def butter_bandpass(self, lowcut: float, highcut: float, order: int = 4):
        nyquist = 0.5 * self.sample_rate
        low = lowcut / nyquist
        high = highcut / nyquist
        # Return second-order sections (SOS) for numerical stability
        sos = signal.butter(order, [low, high], btype="bandpass", output="sos")
        return sos

    def apply_filter(self, data: np.ndarray, sos: np.ndarray) -> np.ndarray:
        # Applies filter forward and backward (zero-phase) or single-pass.
        return signal.sosfilt(sos, data)


def compute_spectral_centroid(audio_data: np.ndarray, sample_rate: int) -> float:
    # Calculates the spectral centroid (brightness) of an audio frame.
    spectrum = np.abs(np.fft.rfft(audio_data))
    frequencies = np.fft.rfftfreq(len(audio_data), d=1.0 / sample_rate)

    magnitude_sum = np.sum(spectrum)
    if magnitude_sum == 0:
        return 0.0
    return float(np.sum(frequencies * spectrum) / magnitude_sum)
```

### B. Dynamic Range Compressor Algorithm (C++17)

```cpp
#include <vector>
#include <cmath>
#include <algorithm>

class DynamicsCompressor {
private:
    float sampleRate;
    float thresholdDb; // e.g. -20 dB
    float ratio;       // e.g. 4.0 (4:1)
    float attackTime;  // in seconds (e.g. 0.01)
    float releaseTime; // in seconds (e.g. 0.1)
    float envelope = 0.0f;

public:
    DynamicsCompressor(float sr, float threshold, float rat, float attack, float release)
        : sampleRate(sr), thresholdDb(threshold), ratio(rat), attackTime(attack), releaseTime(release) {}

    void process(float* buffer, size_t numSamples) {
        float attackCoeff = std::exp(-1.0f / (sampleRate * attackTime));
        float releaseCoeff = std::exp(-1.0f / (sampleRate * releaseTime));

        for (size_t i = 0; i < numSamples; ++i) {
            float input = buffer[i];
            float absInput = std::abs(input);

            // Envelope detection
            if (absInput > envelope) {
                envelope = attackCoeff * envelope + (1.0f - attackCoeff) * absInput;
            } else {
                envelope = releaseCoeff * envelope + (1.0f - releaseCoeff) * absInput;
            }

            // Convert to dB
            float envDb = 20.0f * std::log10(std::max(envelope, 1e-6f));
            float gainReductionDb = 0.0f;

            if (envDb > thresholdDb) {
                gainReductionDb = (thresholdDb - envDb) * (1.0f - 1.0f / ratio);
            }

            // Convert dB reduction back to linear multiplier
            float gainLinear = std::pow(10.0f, gainReductionDb / 20.0f);
            buffer[i] = input * gainLinear;
        }
    }
};
```

---

## 3. Best Practices Checklist

- [ ] **Second-Order Sections (SOS):** When designing higher-order IIR filters (>2nd order), always use `output='sos'` instead of transfer function `b, a` coefficients to avoid float quantization instability.
- [ ] **Nyquist Criterion:** Never place filter cutoffs above `0.5 * sampleRate` (Nyquist limit) to avoid severe aliasing distortion.
- [ ] **Denormal Protection:** In real-time audio loops (especially C++), add anti-denormal noise (e.g. `1e-18f`) to prevent CPU spikes when signals decay close to zero.
