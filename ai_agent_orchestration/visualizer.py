import pygame
import numpy as np
from pydub import AudioSegment
import matplotlib.pyplot as plt

# Initialize Pygame mixer
pygame.mixer.init()

# Load audio
file_path = r"C:\Users\andre\Downloads\Suzanne Vega, DNA - Tom's Diner 4.mp3"
sound = AudioSegment.from_mp3(file_path)
samples = np.array(sound.get_array_of_samples())

# If stereo, take left channel
if sound.channels == 2:
    samples = samples[::2]

# Normalize
samples = samples / np.max(np.abs(samples))

# Create time axis
duration = len(samples) / sound.frame_rate
time = np.linspace(0, duration, num=len(samples))

# Plot waveform
plt.figure(figsize=(12, 4))
plt.plot(time, samples, color='blue')
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
plt.title("Audio Waveform")
plt.show()

# Play audio
pygame.mixer.music.load(file_path)
pygame.mixer.music.play()

# Wait until audio finishes playing
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)
