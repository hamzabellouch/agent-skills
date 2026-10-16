---
name: information-theory-and-coding
description: "Explain information theory and coding: entropy, mutual information, KL divergence, channel capacity, source coding, Huffman codes, error-correcting codes, compression, Kolmogorov complexity, cryptographic entropy. Use for bits, entropy, compression and communication limits."
---

# Information Theory & Coding

- Entropy H(X) = -sum p log2 p (bits); max log2 n for uniform; H(X,Y) = H(X) + H(Y|X); conditional entropy; chain rule.
- Mutual information I(X;Y) = H(X) - H(X|Y) >= 0; data-processing inequality; KL divergence D(p||q) = sum p log(p/q) >= 0 (Gibbs); cross-entropy loss in ML = H(p) + D(p||q).
- Source coding theorem: average code length >= H; Huffman optimal prefix code; Kraft inequality sum 2^{-l_i} <= 1; arithmetic coding; Lempel-Ziv universal compression.
- Channel capacity C = max I(X;Y); binary symmetric channel C = 1 - H(p); AWGN (Shannon-Hartley) C = B log2(1 + S/N); noisy-channel coding theorem (rates below capacity achievable with vanishing error).
- Error-correcting codes: Hamming distance, Hamming(7,4) corrects 1 error, parity checks; linear codes (generator/parity-check matrices, syndrome); Reed-Solomon (CDs, QR codes), BCH, LDPC and turbo codes (near capacity), polar codes; Singleton, Hamming, Gilbert-Varshamov bounds.
- Rate-distortion theory, lossy compression (JPEG, MP3 transforms).
- Kolmogorov complexity (uncomputable), minimum description length, maximum entropy principle; connections to statistical mechanics (Boltzmann = Shannon up to k_B ln 2) and quantum information (von Neumann entropy).
- Password strength: entropy bits = length x log2(alphabet size) if random.
