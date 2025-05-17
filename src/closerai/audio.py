import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# ← your Realtek mic index
DEVICE_INDEX = 19  

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(f"[Audio status] {status}")
    # indata is shape (frames, 2) for stereo; take channel 0 only
    mono = indata[:, 0].copy().tobytes()
    q.put(mono)

def listen(keywords=None):
    """
    Open mic stream, run Vosk recognizer, and detect keywords.
    keywords: list of lower-cased strings to trigger suggestions.
    """
    if keywords is None:
        keywords = ["pricing", "budget", "next steps"]

    # Load your model
    model = Model("models/vosk-model-small-en-us-0.15")
    rec = KaldiRecognizer(model, 16000)

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=2,            # record stereo
        device=DEVICE_INDEX,   # select your mic
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
                        for kw in keywords:
                            if kw in text.lower():
                                print(f"[Suggestion] Mention {kw!r} to guide the conversation.")
                else:
                    partial = json.loads(rec.PartialResult()).get("partial", "")
                    if partial:
                        # print partial results inline
                        print(f"[…] {partial}", end="\r")
        except KeyboardInterrupt:
            print("\nStopped listening.")
