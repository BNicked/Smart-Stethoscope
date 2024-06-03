import pyaudio
import wave

def record(outputFile):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 6

    p = pyaudio.PyAudio()

    stream = p.open(format = FORMAT, 
                    channels = CHANNELS, 
                    rate = RATE, 
                    input = True, 
                    frames_per_buffer = CHUNK)
    
    print("* Recording")

    frames = []

    for i in range(0, int (RATE/CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* Done Recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(outputFile, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

record('PyAudio_Practice/output1.wav')