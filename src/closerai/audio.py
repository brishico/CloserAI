# src/closerai/audio.py
import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer

q = queue.Queue()

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(f"[Audio status] {status}")
    # convert to raw bytes and enqueue
    q.put(bytes(indata))

def listen(keywords=None):
    """
    Open mic stream, run Vosk recognizer, and detect keywords.
    keywords: list of lower-cased strings to trigger suggestions.
    """
    if keywords is None:
        keywords = ["pricing", "budget", "next steps"]

    # Load a small Vosk model (downloaded separately)
    model = Model("models/vosk-model-small-en-us-0.15")  
    rec = KaldiRecognizer(model, 16000)

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                           channels=1, callback=callback):
        print("🎙  Listening...  (press Ctrl+C to stop)")
        try:
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "")
                    if text:
                        print(f"[You said] {text}")
                        for kw in keywords:
                            if kw in text.lower():
                                print(f"[Suggestion] Mention {kw!r} to guide the conversation.")
        except KeyboardInterrupt:
            print("\nStopped listening.")
