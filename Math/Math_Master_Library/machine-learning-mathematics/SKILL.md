---
name: machine-learning-mathematics
description: "Explain the mathematics behind machine learning and AI: linear models, gradient descent, backpropagation, neural networks, probabilistic models, kernels, PCA, SVD, optimization landscapes, generalization, attention and transformers, information theory in ML. Use for ML theory and derivations."
---

# Mathematics of Machine Learning

## Supervised learning
- Empirical risk minimization; loss functions (MSE, cross-entropy, hinge); regularization (L2 = Gaussian prior, L1 = Laplace prior / sparsity).
- Linear regression normal equations; logistic regression gradient X^T(sigma(Xw) - y); softmax cross-entropy gradient p - y.
- Bias-variance decomposition; VC dimension; PAC learning; Rademacher complexity; generalization bounds; double descent and overparameterization.
- SVM and kernels: Mercer kernels, RBF, representer theorem; Gaussian processes.

## Neural networks
- Forward pass, backpropagation = reverse-mode automatic differentiation via the chain rule; Jacobian-vector products; vanishing/exploding gradients; initialization (Xavier, He); batch/layer norm; residual connections; universal approximation theorem.
- Optimizers: SGD, momentum, Adam; learning-rate schedules; loss landscape, saddle points, flat minima.
- CNN: convolution as shared-weight linear operator; equivariance. RNN/LSTM. Transformers: attention softmax(QK^T/sqrt(d))V, positional encodings, scaling laws, complexity O(n^2 d).
- Generative models: VAE (ELBO = E log p(x|z) - KL(q||p)), GAN (minimax), diffusion (score matching, SDE), autoregressive LMs (maximum likelihood on next-token).
- Reinforcement learning: MDP, Bellman equation, policy gradient theorem, Q-learning, PPO, RLHF.

## Unsupervised & probabilistic
PCA (eigenvectors of covariance, SVD), k-means (EM special case), EM algorithm, Gaussian mixtures, HMMs, graphical models, variational inference, MCMC, t-SNE/UMAP, contrastive learning, mutual information bounds.

## Practical math checks
Gradient checking with finite differences; dimensional analysis of tensor shapes; numerical stability (log-sum-exp); calibration; data leakage; reproducibility.
