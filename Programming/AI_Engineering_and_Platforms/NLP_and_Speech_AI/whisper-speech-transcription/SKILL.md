---
name: whisper-speech-transcription
metadata:
  category: NLP Audio and Speech AI
description: >-
  Deploy OpenAI Whisper and Faster-Whisper for high-throughput batch and streaming speech-to-text (STT) transcription.
  Triggers when implementing CTranslate2 GPU acceleration, Voice Activity Detection (Silero VAD), word-level timestamps,
  speaker diarization (PyAnnote), FFmpeg audio pre-processing, dynamic language detection, or WebSocket streaming transcription APIs.
compatibility: Python (>= 3.9), faster-whisper (>= 1.0.0), PyTorch, Silero VAD, FFmpeg, CUDA (>= 11.8)
---

# Whisper Speech Transcription & Diarization

Production patterns for deploying high-performance Speech-to-Text (STT) pipelines using Faster-Whisper, Silero VAD, PyAnnote Speaker Diarization, and WebSockets.

---

## 1. System Architecture

```text
+----------------------+      +---------------------------------+      +---------------------------------+
| Input Audio Stream   | ---> | FFmpeg Audio Pre-processing     | ---> | Silero VAD                      |
| (Microphone/WAV/MP3) |      | (Resample to 16kHz Mono PCM)    |      | (Voice Activity Chunk Filter)   |
+----------------------+      +---------------------------------+      +---------------------------------+
                                                                                       |
                                                                                       v
+----------------------+      +---------------------------------+      +---------------------------------+
| Output JSON Transcript| <--- | PyAnnote Speaker Diarization    | <--- | Faster-Whisper Engine           |
| (Words, Timestamps)  |      | (Assign Speaker IDs)            |      | (CTranslate2 FP16/INT8 GPU)     |
+----------------------+      +---------------------------------+      +---------------------------------+
```

---

## 2. High-Performance Batch Transcription Engine (`transcribe_engine.py`)

Using `faster-whisper` (CTranslate2) for 4x faster execution and 50% lower VRAM usage compared to standard PyTorch implementations.

```python
import os
import logging
from faster_whisper import WhisperModel
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HighPerformanceWhisperEngine:
    def __init__(self, model_size: str = "large-v3", device: str = "cuda", compute_type: str = "float16"):
        logger.info(f"Loading Faster-Whisper model '{model_size}' on {device} ({compute_type})...")
        
        # Fallback to float32 on CPU
        if not torch.cuda.is_available():
            device = "cpu"
            compute_type = "int8"

        self.model = WhisperModel(
            model_size_or_path=model_size,
            device=device,
            compute_type=compute_type,
            cpu_threads=4,
            num_workers=2
        )

    def transcribe_file(self, audio_filepath: str, language: str = None) -> dict:
        """
        Transcribes an audio file with Voice Activity Detection (VAD) and word timestamps.
        """
        segments, info = self.model.transcribe(
            audio_filepath,
            language=language,
            beam_size=5,
            best_of=5,
            vad_filter=True,  # Built-in Silero VAD
            vad_parameters=dict(
                min_speech_duration_ms=250,
                max_speech_duration_s=30,
                min_silence_duration_ms=500,
                speech_pad_ms=400
            ),
            word_timestamps=True
        )

        logger.info(f"Detected language: '{info.language}' with probability {info.language_probability:.2f}")

        formatted_segments = []
        full_text = []

        for segment in segments:
            full_text.append(segment.text)
            
            words_list = []
            if segment.words:
                for w in segment.words:
                    words_list.append({
                        "word": w.word,
                        "start": round(w.start, 2),
                        "end": round(w.end, 2),
                        "probability": round(w.probability, 2)
                    })

            formatted_segments.append({
                "id": segment.id,
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip(),
                "words": words_list
            })

        return {
            "language": info.language,
            "duration": round(info.duration, 2),
            "text": " ".join(full_text).strip(),
            "segments": formatted_segments
        }

if __name__ == "__main__":
    engine = HighPerformanceWhisperEngine(model_size="medium", compute_type="float16")
    result = engine.transcribe_file("sample_meeting.wav")
    print(result["text"])
```

---

## 3. Combining Whisper with PyAnnote Speaker Diarization (`diarized_transcribe.py`)

Assign precise speaker labels ("Speaker A", "Speaker B") to Whisper segment timestamps.

```python
import torch
from pyannote.audio import Pipeline
from transcribe_engine import HighPerformanceWhisperEngine
import numpy as np

def transcribe_with_diarization(audio_filepath: str, hf_token: str):
    # 1. Initialize Whisper STT Engine
    whisper_engine = HighPerformanceWhisperEngine(model_size="large-v3")
    stt_result = whisper_engine.transcribe_file(audio_filepath)

    # 2. Initialize PyAnnote Speaker Diarization Pipeline
    diarization_pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=hf_token
    )
    if torch.cuda.is_available():
        diarization_pipeline.to(torch.device("cuda"))

    # 3. Execute Diarization
    diarization = diarization_pipeline(audio_filepath)

    # 4. Merge Diarization Speakers with Whisper Segments
    final_transcript = []
    
    for segment in stt_result["segments"]:
        seg_start = segment["start"]
        seg_end = segment["end"]

        # Find speaker with maximum overlap during segment timeframe
        speaker_overlaps = {}
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            overlap_start = max(seg_start, turn.start)
            overlap_end = min(seg_end, turn.end)
            
            if overlap_end > overlap_start:
                duration = overlap_end - overlap_start
                speaker_overlaps[speaker] = speaker_overlaps.get(speaker, 0.0) + duration

        assigned_speaker = max(speaker_overlaps, key=speaker_overlaps.get) if speaker_overlaps else "UNKNOWN"

        final_transcript.append({
            "speaker": assigned_speaker,
            "start": seg_start,
            "end": seg_end,
            "text": segment["text"]
        })

    return final_transcript
```

---

## 4. Real-Time Streaming Audio Server via WebSockets (`websocket_server.py`)

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from faster_whisper import WhisperModel
import numpy as np
import asyncio

app = FastAPI(title="Whisper Live Streaming Audio API")

# Load small/fast model for low-latency streaming
MODEL = WhisperModel("tiny.en", device="cuda", compute_type="float16")

@app.websocket("/ws/transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    audio_buffer = bytearray()
    SAMPLE_RATE = 16000
    BYTES_PER_SAMPLE = 2  # 16-bit PCM
    CHUNK_DURATION_SEC = 2
    REQUIRED_BYTES = SAMPLE_RATE * BYTES_PER_SAMPLE * CHUNK_DURATION_SEC

    try:
        while True:
            data = await websocket.receive_bytes()
            audio_buffer.extend(data)

            if len(audio_buffer) >= REQUIRED_BYTES:
                # Convert raw PCM int16 bytes to float32 NumPy array
                pcm_data = np.frombuffer(audio_buffer[:REQUIRED_BYTES], dtype=np.int16).astype(np.float32) / 32768.0
                audio_buffer = audio_buffer[REQUIRED_BYTES:]

                # Run Whisper inference on chunk
                segments, _ = MODEL.transcribe(pcm_data, language="en", beam_size=1)
                
                text_chunk = " ".join([s.text for s in segments]).strip()
                if text_chunk:
                    await websocket.send_json({"transcript": text_chunk})

    except WebSocketDisconnect:
        print("WebSocket client disconnected.")
```

---

## 5. Production Optimization Guidelines

1. **Audio Pre-processing**: Convert input streams using FFmpeg to 16kHz single-channel mono PCM (`ffmpeg -i input.mp3 -ar 16000 -ac 1 -f s16le output.raw`) prior to passing to model buffers.
2. **Batching**: Use `vad_filter=True` to strip silence chunks before invoking CTranslate2 matrix computations; this increases throughput by up to 300% on dialogue files.
3. **Quantization Selection**: Use `compute_type="float16"` on NVIDIA GPUs (Ampere/Ada architectures) and `compute_type="int8"` for CPU deployments.
