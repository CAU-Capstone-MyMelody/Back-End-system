import os
import librosa
import soundfile as sf
import numpy as np
import pretty_midi
import pandas as pd
import torch
import subprocess
from crepe import cli
import noisereduce as nr
from scipy.signal import butter, lfilter

device = torch.device("mps" if torch.backends.mps.is_built() else "cpu")


def convert_to_wav(input_path, output_path):
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-ar", "16000",
        output_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def separate_vocals(audio_path, output_base):
    subprocess.run([
        "demucs", audio_path,
        "--two-stems", "vocals",
        "-n", "htdemucs",
        "-d", "cuda" if torch.cuda.is_available() else "mps",
        "-o", output_base
    ], stdout=subprocess.DEVNULL)
    basename = os.path.splitext(os.path.basename(audio_path))[0]
    return os.path.join(output_base, "htdemucs", basename, "vocals.wav")

def highpass_filter(y, sr, cutoff=100, order=5):
    nyq = 0.5 * sr
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return lfilter(b, a, y)

def remove_silence_and_filter(input_wav, output_wav, threshold_db=-60.0):
    y, sr = librosa.load(input_wav, sr=None)
    energy = librosa.feature.rms(y=y)[0]
    frames = np.where(librosa.amplitude_to_db(energy) > threshold_db)[0]
    if len(frames) == 0:
        y_clean = np.zeros_like(y)
    else:
        non_silent_intervals = librosa.frames_to_samples([frames[0], frames[-1]])
        y_clean = y[non_silent_intervals[0]:non_silent_intervals[1]]
    y_filtered = highpass_filter(y_clean, sr)
    sf.write(output_wav, y_filtered, sr)
    return output_wav

def run_crepe(cleaned_wav, output_dir):
    cli.run(
        filename=[cleaned_wav],
        output=output_dir,
        model_capacity='full',
        viterbi=True,
        save_activation=False,
        save_plot=False,
        plot_voicing=False,
        no_centering=False,
        step_size=10,
        verbose=False
    )
    return os.path.join(output_dir, os.path.basename(cleaned_wav).replace('.wav', '.f0.csv'))

def correct_crepe_octave(crepe_freqs):
    return crepe_freqs * 2

def process_audio_pitches(crepe_csv_path):
    df = pd.read_csv(crepe_csv_path)
    df = df[df['confidence'] > 0.5]
    df['frequency'] = correct_crepe_octave(df['frequency'].values)
    df = df.sort_values('time')

    max_time = df['time'].max()
    times = np.arange(0, max_time, 0.5)
    audio_pitches = []

    for t in times:
        segment = df[(df['time'] >= t) & (df['time'] < t + 0.5)]
        if segment.empty:
            audio_pitches.append(None)
        else:
            avg_pitch = np.mean(segment['frequency'])
            audio_pitches.append(round(avg_pitch, 2))

    valid_pitches = [p for p in audio_pitches if p is not None]
    max_pitch = max(valid_pitches) if valid_pitches else None
    min_pitch = min(valid_pitches) if valid_pitches else None

    return times.tolist(), audio_pitches, max_pitch, min_pitch
