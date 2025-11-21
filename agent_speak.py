import pyaudio

pya = pyaudio.PyAudio()

def play_audio_file(wav_path: str, pa, device_substr="Voicemeeter Input"):
    """
    Inject WAV audio playback into an ongoing Gemini Live session using the same PyAudio instance.
    - `pa` MUST be the existing PyAudio instance already used by the session!
    - Does NOT close or terminate `pa`
    - Keeps static device logic
    """
    import wave
    import numpy as np

    FRAMES_PER_BUFFER = 480

    def find_output_device(substr: str) -> int:
        s = substr.lower()
        for i in range(pa.get_device_count()):
            d = pa.get_device_info_by_index(i)
            if d.get('maxOutputChannels', 0) > 0 and s in d['name'].lower():
                return i
        raise RuntimeError(f"Output device '{substr}' not found. Check audio routing.")

    # Open WAV
    wf = wave.open(wav_path, 'rb')
    sr = wf.getframerate()
    ch = wf.getnchannels()
    sw = wf.getsampwidth()

    dev_index = find_output_device(device_substr)
    print(f"🎧 Injecting audio via '{device_substr}' | SR={sr}, CH={ch}, WIDTH={sw*8} bits")

    # Create new stream using existing pa instance
    stream = pa.open(
        format=pa.get_format_from_width(sw),
        channels=ch,
        rate=sr,
        output=True,
        output_device_index=dev_index,
        frames_per_buffer=FRAMES_PER_BUFFER
    )

    data = wf.readframes(1024)
    while data:
        stream.write(data)
        data = wf.readframes(1024)

    # 🔹 Only stop, do NOT close or terminate pa
    stream.stop_stream()
    wf.close()  # safe

    print("✓ Injection completed (stream stopped, device still active).")


# play_audio_file("audio/let_me_think.wav", pya)