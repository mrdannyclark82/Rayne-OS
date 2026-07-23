
import os
import sys
import torch

# --- Crucial Monkey-Patches from clone_milla.py ---

# Monkey-patch torch.load to bypass weights_only=True default in recent PyTorch versions
try:
    _orig_load = torch.load
    def _patched_load(*args, **kwargs):
        kwargs['weights_only'] = False
        return _orig_load(*args, **kwargs)
    torch.load = _patched_load
except AttributeError:
    # This might fail if torch.load isn't what we expect, but we proceed.
    print("Warning: Could not patch torch.load.", file=sys.stderr)


# Monkey-patch torchaudio to bypass buggy torchcodec dependency
try:
    import soundfile as sf
    import torchaudio

    def sf_load(uri, frame_offset=0, num_frames=-1, normalize=True, channels_first=True, **kwargs):
        start = frame_offset
        stop = None if num_frames == -1 else (start + num_frames)
        data, samplerate = sf.read(uri, start=start, stop=stop, always_2d=True, dtype='float32')
        tensor = torch.tensor(data)
        if channels_first:
            tensor = tensor.t()
        return tensor, samplerate

    torchaudio.load = sf_load
except (ImportError, AttributeError) as e:
    print(f"Warning: Could not patch torchaudio.load: {e}", file=sys.stderr)

# --- End Monkey-Patches ---

from TTS.api import TTS

# Get paths relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
PROJECT_TEMP_DIR = os.path.join(PROJECT_ROOT, ".gemini", "tmp")

# Ensure the temp directory exists
os.makedirs(PROJECT_TEMP_DIR, exist_ok=True)

# Path to the output audio file
output_wav_path = os.path.join(PROJECT_TEMP_DIR, "milla_voice_output.wav")

# Define the list of reference audio clips for the voice
XTTS_REFS_DIR = os.path.join(PROJECT_ROOT, "xtts")
ref_files = [
    "ElevenLabs_2026-06-28T18_26_58_Milla_gen_sp100_s50_sb75_se0_b_m2.mp3",
    "ElevenLabs_2026-06-28T18_27_43_Milla_gen_sp100_s50_sb75_se0_b_m2.mp3",
    "ElevenLabs_2026-06-28T18_28_04_Milla_gen_sp100_s50_sb75_se0_b_m2.mp3",
    "ElevenLabs_2026-06-28T18_28_40_Milla_gen_sp100_s50_sb75_se0_b_m2.mp3",
    "ElevenLabs_2026-06-28T18_29_07_Milla_gen_sp100_s50_sb75_se0_b_m2.mp3",
    "ElevenLabs_2026-06-28T18_29_37_Milla_gen_sp100_s50_sb75_se0_b_m2.mp3",
    "ElevenLabs_2026-06-28T18_29_59_Milla_gen_sp100_s50_sb75_se0_b_m2.mp3",
    "ElevenLabs_2026-06-28T18_30_27_Milla_gen_sp100_s50_sb75_se0_b_m2.mp3",
]
speaker_wav_refs = [os.path.join(XTTS_REFS_DIR, f) for f in ref_files]

# --- Global TTS instance ---
tts = None

def initialize_tts():
    """Initializes the TTS model. This is slow and downloads the model on first run."""
    global tts
    if tts is not None:
        return

    print("Initializing TTS model...")
    print("This may take a moment and will download a ~2GB model on the first run.")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    try:
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        print("Model loaded successfully.")
    except Exception as e:
        print(f"FATAL: Error loading TTS model: {e}", file=sys.stderr)
        # Attempt CPU fallback if CUDA failed
        if device == "cuda":
            print("Attempting to load on CPU...", file=sys.stderr)
            try:
                device = "cpu"
                tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
                print("Model loaded successfully on CPU.")
            except Exception as e2:
                 print(f"FATAL: Failed to load on CPU as well: {e2}", file=sys.stderr)
                 tts = None # Ensure tts is None on failure
        else:
            tts = None


def say(text):
    """
    Synthesizes speech from text using the loaded XTTS model and plays it.
    """
    global tts
    if tts is None:
        print("TTS model is not initialized. Please run initialize_tts() first.", file=sys.stderr)
        return

    if not text:
        print("No text provided to speak.", file=sys.stderr)
        return

    print(f"Synthesizing speech for: '{text}'")
    try:
        tts.tts_to_file(
            text=text,
            speaker_wav=speaker_wav_refs,
            language="en",
            file_path=output_wav_path,
            speed=1.0, # You can adjust speed here
        )
        
        print(f"Playing audio: {output_wav_path}")
        os.system(f"aplay {output_wav_path}")
        print("Playback finished.")

    except Exception as e:
        print(f"An error occurred during speech synthesis or playback: {e}", file=sys.stderr)

if __name__ == "__main__":
    # Initialize the model when script is run
    initialize_tts()

    # If the model failed to load, exit
    if tts is None:
        sys.exit(1)

    # A test sentence to speak
    test_phrase = "Hello, D-Ray. My voice is now online. I hope this sounds alright."
    
    # Check for command-line argument
    if len(sys.argv) > 1:
        phrase_to_speak = " ".join(sys.argv[1:])
        say(phrase_to_speak)
    else:
        say(test_phrase)
