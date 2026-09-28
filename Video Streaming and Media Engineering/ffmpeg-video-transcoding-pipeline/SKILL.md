---
name: ffmpeg-video-transcoding-pipeline
metadata:
  category: Video Streaming and Media Engineering
description: Build automated, production-grade video transcoding pipelines using FFmpeg. Generate multi-bitrate Adaptive Bitrate (ABR) ladders for HLS and MPEG-DASH, optimize two-pass VBR encoding with H.264, HEVC, and AV1, fragment MP4 (fMP4), and normalize audio loudness according to EBU R128 standards. Trigger when processing video uploads, preparing video for streaming, or automating media conversions.
compatibility: FFmpeg 6.0+, HLS v7+, MPEG-DASH ISO/IEC 23009-1
---

# FFmpeg Video Transcoding Pipeline Skill Guide

This skill standardizes automated multi-bitrate transcoding pipelines for video-on-demand (VOD) streaming infrastructure.

---

## 1. Adaptive Bitrate (ABR) Transcoding Ladder

```text
[ Raw Master Video ] (ProRes / High-Bitrate MP4)
         |
         +---> FFmpeg Multi-Output Transcoder
                 |
                 |-- 1080p @ 4500 kbps (fMP4 / H.264)
                 |-- 720p  @ 2500 kbps (fMP4 / H.264)
                 |-- 480p  @ 1200 kbps (fMP4 / H.264)
                 |-- 360p  @ 600 kbps  (fMP4 / H.264)
                 |-- Audio: AAC 128 kbps (EBU R128 Normalized)
                 |
                 v
[ Master Playlist: master.m3u8 / manifest.mpd ]
```

---

## 2. Production FFmpeg Commands & Scripts

### A. Production Multi-Bitrate HLS Generation Script

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT_FILE="${1:?Usage: $0 <input_video.mp4> <output_dir>}"
OUT_DIR="${2:?Usage: $0 <input_video.mp4> <output_dir>}"

mkdir -p "${OUT_DIR}"

ffmpeg -hide_banner -y -i "${INPUT_FILE}" \
  # Video filter: scale and keyframe alignment (2-second GOP at 30fps = 60 frames)
  -filter_complex \
  "[0:v]split=3[v1080][v720][v480]; \
   [v1080]scale=w=1920:h=1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[v1080out]; \
   [v720]scale=w=1280:h=720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2[v720out]; \
   [v480]scale=w=854:h=480:force_original_aspect_ratio=decrease,pad=854:480:(ow-iw)/2:(oh-ih)/2[v480out]" \
  \
  # 1080p Stream
  -map "[v1080out]" -c:v:0 libx264 -preset slow -b:v:0 4500k -maxrate:v:0 4800k -bufsize:v:0 9000k \
  -g 60 -keyint_min 60 -sc_threshold 0 \
  \
  # 720p Stream
  -map "[v720out]" -c:v:1 libx264 -preset slow -b:v:1 2500k -maxrate:v:1 2700k -bufsize:v:1 5000k \
  -g 60 -keyint_min 60 -sc_threshold 0 \
  \
  # 480p Stream
  -map "[v480out]" -c:v:2 libx264 -preset slow -b:v:2 1200k -maxrate:v:2 1350k -bufsize:v:2 2400k \
  -g 60 -keyint_min 60 -sc_threshold 0 \
  \
  # Audio Stream (Normalized)
  -map a:0 -c:a aac -b:a 128k -ar 48000 -ac 2 \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
  \
  # HLS Output Packaging
  -f hls \
  -hls_time 4 \
  -hls_playlist_type vod \
  -hls_flags independent_segments \
  -hls_segment_type fmp4 \
  -hls_segment_filename "${OUT_DIR}/stream_%v_data%03d.m4s" \
  -master_pl_name master.m3u8 \
  -var_stream_map "v:0,a:0 v:1,a:0 v:2,a:0" \
  "${OUT_DIR}/stream_%v.m3u8"

echo "Transcoding completed. Manifest at: ${OUT_DIR}/master.m3u8"
```

### B. Python Automated Transcoder Worker

```python
import subprocess
import json
from pathlib import Path


def probe_video(file_path: str) -> dict:
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        file_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def transcode_to_web_optimized_mp4(input_path: str, output_path: str):
    # Encodes a single web-compatible MP4 with faststart for instant streaming.
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",  # Moves moov atom to beginning of file
        output_path,
    ]
    subprocess.run(cmd, check=True)
```

---

## 3. Best Practices Checklist

- [ ] **Aligned Keyframes (GOP):** Set strict GOP size (`-g <frames> -keyint_min <frames> -sc_threshold 0`) to ensure seamless stream switching in HLS/DASH.
- [ ] **Faststart for MP4:** Always add `-movflags +faststart` when generating standalone MP4 files so browsers start playback before full download.
- [ ] **Loudness Normalization:** Apply `-af loudnorm=I=-16:TP=-1.5` to meet standard broadcast/web loudness targets (EBU R128 / ITU-R BS.1770).
