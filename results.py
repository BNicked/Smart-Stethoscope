import numpy as np
from scipy.signal import butter, filtfilt, find_peaks
from scipy.io.wavfile import write
import matplotlib.pyplot as plt

import pyaudio
import wave


FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 1000

p = pyaudio.PyAudio()

info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
device_name = 'Stethophone'

for i in range(0, numdevices):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
    if(p.get_device_info_by_host_api_device_index(0, i).get('name') == device_name):
        device_index = i

stream = p.open(
    format = FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input = True,
    frames_per_buffer = FRAMES_PER_BUFFER,
    input_device_index= 1
)

print("Starting Recording")

seconds = 10
frames = []

for i in range(0, int(RATE/FRAMES_PER_BUFFER * seconds)):
    data = stream.read(FRAMES_PER_BUFFER)
    frames.append(data)

stream.stop_stream()
stream.close()
p.terminate()

audio_data = np.frombuffer(b''.join(frames), dtype=np.float32)

obj = wave.open("count.wav", "wb")
obj.setnchannels(CHANNELS)
obj.setsampwidth(p.get_sample_size(FORMAT))
obj.setframerate(RATE)
obj.writeframes(b"".join(frames))
obj.close()

# Bandpass filter
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data, axis=0)
    return y

lowcut = 20.0
highcut = 200.0
filtered_audio = bandpass_filter(audio_data, lowcut, highcut, RATE).flatten()

# Find peaks
max_bpm = 80
min_distance = int((RATE * 60) / max_bpm)
peaks, _ = find_peaks(filtered_audio, distance=min_distance, height=0.5) 

# Calculate BPM
num_beats = len(peaks)
duration_in_minutes1 = seconds / 60.0
bpm1 = num_beats / duration_in_minutes1

def get_wav_duration(filepath):
    with wave.open(filepath, 'r') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        duration = frames / float(rate)
    return duration

d = get_wav_duration('count.wav')
duration_in_minutes2 = d/60.0
bpm2 = num_beats/duration_in_minutes2


print(f"Beats in 10s: {num_beats}")
print(f"Duration1: {duration_in_minutes1}")
print(f"Duration2: {duration_in_minutes2}")
print(f"Estimated BPM1: {bpm1}")
print(f"Estimated BPM2: {bpm2}")

# Plot the signal
plt.plot(filtered_audio)
plt.plot(peaks, filtered_audio[peaks], "x")
plt.title("Heart Sound Signal with Detected Peaks")
plt.xlabel("Sample Number")
plt.ylabel("Amplitude")
plt.savefig('count.png')
plt.show()