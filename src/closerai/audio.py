import queue, json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from .suggestion_engine import SuggestionEngine
from .chatgpt_engine import ChatGPTEngine
from dotenv import load_dotenv
load_dotenv()                # ← loads C:\AI\CloserAI\.env
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("Missing OPENAI_API_KEY in environment")

# ChatGPT Stuff
static_engine = SuggestionEngine()
gpt_engine    = ChatGPTEngine()

# Replace these with the indices you found:
MIC_INDEX   = 1   # your physical mic
LOOP_INDEX  = 9   # VB-Cable in Recording devices

engine = SuggestionEngine()

# Queues for the two streams
mic_q  = queue.Queue()
cust_q = queue.Queue()

def mic_callback(indata, frames, time, status):
    if status: print(f"[Mic status] {status}")
    mono = indata[:, 0].copy().tobytes()
    mic_q.put(mono)

def cust_callback(indata, frames, time, status):
    if status: print(f"[Cust status] {status}")
    mono = indata[:, 0].copy().tobytes()
    cust_q.put(mono)

def listen(keywords=None, disable_gpt=False):
    """
    Listen on both mic (you) and loopback (customer), printing
    static suggestions and—unless disable_gpt=True—dynamic GPT suggestions.
    """
    # Load Vosk model once
    model = Model("models/vosk-model-small-en-us-0.15")
    mic_rec  = KaldiRecognizer(model, 16000)
    cust_rec = KaldiRecognizer(model, 16000)

    print("🎙 Listening (Mic + Customer)… Ctrl+C to stop")

    # Handlers
    def mic_callback(indata, frames, time, status):
        if status:
            print(f"[Mic status] {status}")
        mono = indata[:, 0].copy().tobytes()
        mic_q.put(mono)

    def cust_callback(indata, frames, time, status):
        if status:
            print(f"[Cust status] {status}")
        mono = indata[:, 0].copy().tobytes()
        cust_q.put(mono)

    # Open both streams
    with sd.InputStream(samplerate=16000, blocksize=8000,
                        dtype="int16", channels=4,
                        device=MIC_INDEX, callback=mic_callback), \
         sd.InputStream(samplerate=16000, blocksize=8000,
                        dtype="int16", channels=2,
                        device=LOOP_INDEX, callback=cust_callback):

        try:
            while True:
                # Process customer audio first
                while not cust_q.empty():
                    data = cust_q.get()
                    if cust_rec.AcceptWaveform(data):
                        txt = json.loads(cust_rec.Result()).get("text", "")
                        if txt:
                            print(f"[Customer said] {txt}")

                            # 1) static JSON suggestion
                            if suggestion := static_engine.get(txt):
                                print(f"[Suggestion] {suggestion}")

                            # 2) dynamic GPT suggestion (unless disabled)
                            if not disable_gpt:
                                if gpt_sugg := gpt_engine.get(txt, timeout=3.0):
                                    print(f"💡 GPT Suggestion: {gpt_sugg}")

                # (Optional) process your own mic if desired
                while not mic_q.empty():
                    data = mic_q.get()
                    if mic_rec.AcceptWaveform(data):
                        txt = json.loads(mic_rec.Result()).get("text", "")
                        if txt:
                            print(f"[You said] {txt}")

                sd.sleep(100)  # small sleep to yield control

        except KeyboardInterrupt:
            print("\nStopped.")
