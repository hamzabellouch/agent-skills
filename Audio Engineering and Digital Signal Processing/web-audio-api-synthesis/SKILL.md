---
name: web-audio-api-synthesis
metadata:
  category: Audio Engineering and Digital Signal Processing
description: Design and implement low-latency browser audio synthesis, sound effects, audio node graphs, convolver reverbs, and custom AudioWorklet processors using the W3C Web Audio API. Trigger when building interactive web synthesizers, in-browser audio editors, sound engines for games, or real-time audio visualization.
compatibility: W3C Web Audio API Recommendation, Modern Browsers (Chrome, Firefox, Safari)
---

# Web Audio API Synthesis Skill Guide

This skill governs standard practices for building high-fidelity audio synthesis, modular audio node graphs, and real-time AudioWorklet processors in web applications.

---

## 1. Audio Node Graph Architecture

The Web Audio API connects modular `AudioNode` instances into a directed graph routing into `AudioDestinationNode` (speakers).

```text
[ OscillatorNode (VCO) ] -----> [ BiquadFilterNode (VCF) ] -----> [ GainNode (VCA) ]
                                          ^                                |
                                          |                                v
[ AudioBufferSourceNode (Noise) ] ---------+                     [ DynamicsCompressorNode ]
                                                                           |
                                                                           v
                                                            [ AudioDestinationNode ] (Speakers)
```

---

## 2. Production Code Standards

### A. Subtractive Polyphonic Synthesizer Voice (TypeScript)

```typescript
export class SynthVoice {
  private ctx: AudioContext;
  private osc: OscillatorNode;
  private filter: BiquadFilterNode;
  private ampGain: GainNode;

  constructor(ctx: AudioContext) {
    this.ctx = ctx;

    // 1. Voltage Controlled Oscillator (VCO)
    this.osc = this.ctx.createOscillator();
    this.osc.type = "sawtooth";

    // 2. Voltage Controlled Filter (VCF)
    this.filter = this.ctx.createBiquadFilter();
    this.filter.type = "lowpass";
    this.filter.frequency.value = 800; // Cutoff
    this.filter.Q.value = 6;           // Resonance

    // 3. Voltage Controlled Amplifier (VCA)
    this.ampGain = this.ctx.createGain();
    this.ampGain.gain.setValueAtTime(0.0001, this.ctx.currentTime);

    // 4. Connect Audio Graph
    this.osc.connect(this.filter);
    this.filter.connect(this.ampGain);
  }

  public connect(destination: AudioNode): void {
    this.ampGain.connect(destination);
  }

  public triggerAttack(frequency: number, velocity: number = 0.8): void {
    const now = this.ctx.currentTime;
    this.osc.frequency.setValueAtTime(frequency, now);

    // ADSR Envelope (Attack & Decay)
    this.ampGain.gain.cancelScheduledValues(now);
    this.ampGain.gain.setValueAtTime(0.0001, now);
    this.ampGain.gain.exponentialRampToValueAtTime(velocity, now + 0.02); // 20ms Attack
    this.ampGain.gain.exponentialRampToValueAtTime(velocity * 0.7, now + 0.15); // 130ms Decay

    // Filter Envelope Sweep
    this.filter.frequency.cancelScheduledValues(now);
    this.filter.frequency.setValueAtTime(300, now);
    this.filter.frequency.exponentialRampToValueAtTime(3500, now + 0.05);
    this.filter.frequency.exponentialRampToValueAtTime(800, now + 0.3);

    this.osc.start(now);
  }

  public triggerRelease(): void {
    const now = this.ctx.currentTime;
    // Release Stage
    this.ampGain.gain.cancelScheduledValues(now);
    this.ampGain.gain.setValueAtTime(this.ampGain.gain.value, now);
    this.ampGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.3); // 300ms Release

    this.osc.stop(now + 0.35);
  }
}
```

### B. Custom DSP AudioWorklet Processor (`bitcrusher-processor.js`)

```javascript
class BitcrusherProcessor extends AudioWorkletProcessor {
  static get parameterDescriptors() {
    return [
      { name: "bitDepth", defaultValue: 8, minValue: 1, maxValue: 16 },
      { name: "reduction", defaultValue: 4, minValue: 1, maxValue: 32 },
    ];
  }

  constructor() {
    super();
    this.phase = 0;
    this.lastSample = 0;
  }

  process(inputs, outputs, parameters) {
    const input = inputs[0];
    const output = outputs[0];

    if (!input || !input[0]) return true;

    const bitDepth = parameters.bitDepth[0];
    const reduction = parameters.reduction[0];
    const step = Math.pow(0.5, bitDepth);

    for (let channel = 0; channel < input.length; ++channel) {
      const inputChannel = input[channel];
      const outputChannel = output[channel];

      for (let i = 0; i < inputChannel.length; ++i) {
        this.phase += 1;
        if (this.phase >= reduction) {
          this.phase = 0;
          // Quantize amplitude to bit depth
          this.lastSample = step * Math.floor(inputChannel[i] / step + 0.5);
        }
        outputChannel[i] = this.lastSample;
      }
    }
    return true;
  }
}

registerProcessor("bitcrusher-processor", BitcrusherProcessor);
```

---

## 3. Best Practices & User Interaction

1. **User Gesture Requirement:** Modern browsers block `AudioContext` from starting until a user gesture (click/keydown). Always resume suspended context on initial interaction:
   ```typescript
   if (audioCtx.state === "suspended") {
     await audioCtx.resume();
   }
   ```
2. **Exponential Ramps:** Always use `exponentialRampToValueAtTime` for frequency and gain to match human logarithmic perception, avoiding zero as a target (`0.0001` minimum).
