# Threat Model

## System Model

The system contains multiple federated clients, one coordination server, and two non-colluding aggregation
parties. Clients hold private local data and submit model updates. The server coordinates training and receives
only filtering decisions and masked aggregate updates.

## Adversary Model

The prototype assumes semi-honest aggregation parties that follow the protocol but may try to infer client
information from received messages. They do not collude. A subset of clients can be Byzantine and may perform
label flipping, sign flipping, or Gaussian-noise update attacks.

## Security Goals

1. Hide individual low-dimensional sketches from any single aggregation party by additive secret sharing.
2. Avoid exposing full plaintext model updates during robust filtering.
3. Detect and remove abnormal clients before secure aggregation.
4. Reveal only aggregate information needed for model update and evaluation.

## Simplifications

The secure distance implementation reconstructs pairwise sketch-distance values as a runnable course prototype,
not the original high-dimensional model updates. Full malicious-secure MPC, dropout-resilient SecAgg, formal
game-based security proof, and encrypted geometric median are left as extensions.

## Claims That Should Not Be Overstated

This prototype should not be described as a production-ready malicious-secure MPC system. It does not prove
security against aggregators that arbitrarily deviate from the protocol, does not implement zero-knowledge
proofs for client update well-formedness, and does not solve majority-malicious Byzantine robustness in the
fully encrypted geometric-median sense. The defensible claim is narrower: under two non-colluding semi-honest
aggregators, PP-SRSF hides individual sketches from any single aggregation party and avoids plaintext
high-dimensional update inspection during robust filtering.
