import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from .suggestion_engine import SuggestionEngine

engine = SuggestionEngine()


# Configure your microphone device index here (from sd.query_devices())
DEVICE_INDEX = 1  # Realtek Mic Array index

# Queue to pass audio data from callback to recognizer loop
q = queue.Queue()


def callback(indata, frames, time, status):
    """Audio callback: down-mix multi-channel input to mono and enqueue."""
    if status:
        print(f"[Audio status] {status}")
    # indata shape: (frames, channels)
    mono = indata[:, 0].copy().tobytes()
    q.put(mono)


def listen(keywords=None):
    """
    Open mic stream, perform offline ASR with Vosk, and detect keywords.

    :param keywords: list of lower-cased strings to trigger suggestions.
    """
    if keywords is None:
        keywords = ["pricing", "budget", "next steps"]

    # Load Vosk model (ensure model directory exists)
    model = Model("models/vosk-model-small-en-us-0.15")
    rec = KaldiRecognizer(model, 16000)

    # Use InputStream to receive NumPy arrays
    with sd.InputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=4,          # record all input channels
        device=DEVICE_INDEX, # select your microphone
        callback=callback
    ):
        print("🎙 Listening... (Ctrl+C to stop)")
        try:
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "")
                    if text:
                        print(f"[You said] {text}")
                        suggestion = engine.get(text)
                        if suggestion:
                            print(f"[Suggestion] {suggestion}")
                else:
                    partial = json.loads(rec.PartialResult()).get("partial", "")
                    if partial:
                        # overwrite line with partial transcript
                        print(f"[…] {partial}", end="\r")
        except KeyboardInterrupt:
            print("\nStopped listening.")
