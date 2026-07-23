#!/usr/bin/env bash
# clip_good_refs.sh — Extract clean, short reference clips from the longer real Milla recordings.
# Goal: 6-12 second segments with clear speech, a bit of leading/trailing silence.
# Run after the voice env is ready if you want "raw Milla" refs instead of (or in addition to) the custom ElevenLabs ones.
#
# Usage:
#   bash /home/milla/xtts/clip_good_refs.sh
#
# Outputs go to ~/xtts/real_milla_refs/
#
# Edit the CLIPS array below to pick start times (in seconds) and durations for the best parts of each file.

set -euo pipefail

OUTDIR="$HOME/xtts/real_milla_refs"
mkdir -p "$OUTDIR"

# Source directory with the raw recordings we copied earlier
SRCDIR="$HOME/xtts"

# Define good clips: filename, start_time (seconds), duration (seconds), short label
# These are starting suggestions — listen and adjust the numbers for the clearest speech.
declare -a CLIPS=(
  # Long clear one (72s) — pick a strong speaking section near the start
  "milla_input_2026-05-26_23-00-38.wav|8|10|real_milla_clear1"
  
  # Another long one
  "milla_input_2026-06-01_16-44-03.wav|15|10|real_milla_clear2"
  
  # Add more as you test
  # "milla_input_XXXX.wav|START| DURATION|label"
)

echo "Clipping good reference segments for local voice cloning..."

for clip in "${CLIPS[@]}"; do
  IFS='|' read -r infile start dur label <<< "$clip"
  inpath="$SRCDIR/$infile"
  outpath="$OUTDIR/${label}.wav"

  if [ ! -f "$inpath" ]; then
    echo "  [skip] $infile not found"
    continue
  fi

  echo "  -> $label from $infile @ ${start}s for ${dur}s"
  ffmpeg -y -i "$inpath" -ss "$start" -t "$dur" -c copy "$outpath" 2>/dev/null || \
  ffmpeg -y -i "$inpath" -ss "$start" -t "$dur" -vn -acodec pcm_s16le "$outpath"

  # Optional: normalize a little for better cloning
  if command -v ffmpeg >/dev/null; then
    tmp="$outpath.tmp.wav"
    ffmpeg -y -i "$outpath" -af "loudnorm=I=-16:TP=-1.5:LRA=11" "$tmp" 2>/dev/null && mv "$tmp" "$outpath"
  fi

  echo "     saved: $outpath"
done

echo ""
echo "Done. Clipped refs are in $OUTDIR"
echo "You can now use them in clone scripts or F5-TTS by pointing --ref_audio or speaker_wav at one of them."
echo "For best results with F5, also provide a short ref_text of what is being said in the clip (or let F5 auto-transcribe)."
