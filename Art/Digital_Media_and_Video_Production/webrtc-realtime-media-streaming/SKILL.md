---
name: webrtc-realtime-media-streaming
metadata:
  category: Video Streaming and Media Engineering
description: Architect and deploy sub-second real-time video, audio, and data streaming using WebRTC, SFUs (Selective Forwarding Units), STUN/TURN traversal, SDP negotiation, and data channels. Trigger when implementing real-time video conferencing, live interactive streaming, or ultra-low latency peer-to-peer data synchronization.
compatibility: WebRTC 1.0 (W3C), RFC 8829 (JSEP), LiveKit / mediasoup / Pion
---

# WebRTC Real-Time Media Streaming Skill Guide

This skill governs the design and deployment of ultra-low latency (<500ms) WebRTC communication pipelines, signaling protocols, and SFU topologies.

---

## 1. WebRTC SFU Topology & Signaling Flow

```text
[ Client Peer A ]                       [ Signaling Server ]             [ SFU Media Router ]
       |                                         |                                |
       |--(1) Create Offer (SDP) --------------->|                                |
       |                                         |--(2) Relay Offer ------------->|
       |                                         |<-(3) Answer (SDP) -------------|
       |<-(4) Set Remote Description ------------|                                |
       |                                                                          |
       |========== (5) ICE Gathering & STUN/TURN Binding ========================>|
       |                                                                          |
       |>>>>>>>>>> (6) Secure SRTP Audio / Video Stream (UDP) >>>>>>>>>>>>>>>>>>>>|
```

---

## 2. Production Code Standards

### A. WebRTC Peer Connection Manager (TypeScript)

```typescript
export class WebRTCConnection {
  private pc: RTCPeerConnection;
  private localStream?: MediaStream;

  constructor(
    private readonly iceServers: RTCIceServer[],
    private readonly onTrackCallback: (track: MediaStreamTrack, streams: readonly MediaStream[]) => void,
    private readonly onIceCandidateCallback: (candidate: RTCIceCandidate) => void
  ) {
    this.pc = new RTCPeerConnection({
      iceServers: this.iceServers,
      iceTransportPolicy: "all",
      bundlePolicy: "max-bundle",
      rtcpMuxPolicy: "require",
    });

    this.registerEventHandlers();
  }

  private registerEventHandlers(): void {
    this.pc.ontrack = (event) => {
      this.onTrackCallback(event.track, event.streams);
    };

    this.pc.onicecandidate = (event) => {
      if (event.candidate) {
        this.onIceCandidateCallback(event.candidate);
      }
    };

    this.pc.onconnectionstatechange = () => {
      console.log(`[WebRTC] Connection State: ${this.pc.connectionState}`);
    };
  }

  public async startCapture(videoConstraint: boolean = true, audioConstraint: boolean = true): Promise<MediaStream> {
    this.localStream = await navigator.mediaDevices.getUserMedia({
      video: videoConstraint ? { width: { ideal: 1280 }, height: { ideal: 720 }, frameRate: { max: 30 } } : false,
      audio: audioConstraint ? { echoCancellation: true, noiseSuppression: true, autoGainControl: true } : false,
    });

    for (const track of this.localStream.getTracks()) {
      this.pc.addTrack(track, this.localStream);
    }
    return this.localStream;
  }

  public async createOffer(): Promise<RTCSessionDescriptionInit> {
    const offer = await this.pc.createOffer({
      offerToReceiveAudio: true,
      offerToReceiveVideo: true,
    });
    await this.pc.setLocalDescription(offer);
    return offer;
  }

  public async handleAnswer(answer: RTCSessionDescriptionInit): Promise<void> {
    await this.pc.setRemoteDescription(new RTCSessionDescription(answer));
  }

  public async addIceCandidate(candidateInit: RTCIceCandidateInit): Promise<void> {
    await this.pc.addIceCandidate(new RTCIceCandidate(candidateInit));
  }

  public close(): void {
    this.localStream?.getTracks().forEach((track) => track.stop());
    this.pc.close();
  }
}
```

---

## 3. Production Guidelines & Traversal

1. **Mandatory TURN Server:** 15-20% of enterprise clients are behind symmetric NATs or corporate firewalls that block direct P2P; always configure TURN over port 443 with TLS (`turns:`).
2. **Audio Processing Constraints:** Always enable `echoCancellation: true` and `noiseSuppression: true` in `getUserMedia` for conference applications.
3. **Simulcast for Multi-Party:** In SFU architectures, configure WebRTC simulcast with 3 spatial layers (low, mid, high) so the SFU can forward lower bitrates to participants with constrained bandwidth.
