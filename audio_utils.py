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

def extract_midi_json(midi_path, start_time, end_time):
    pm = pretty_midi.PrettyMIDI(midi_path)
    instrument = pm.instruments[0]
    midi_times = []
    midi_pitches = []
    for note in instrument.notes:
        if note.end < start_time or note.start > end_time:
            continue
        clipped_start = max(note.start, start_time)
        clipped_end = min(note.end, end_time)
        hz = pretty_midi.note_number_to_hz(note.pitch)
        midi_times.extend([round(clipped_start, 3), round(clipped_end, 3)])
        midi_pitches.extend([round(hz, 2), round(hz, 2)])
    return midi_times, midi_pitches

#def align_crepe_to_midi_times(crepe_csv_path, midi_times, user_start, user_end):
    df = pd.read_csv(crepe_csv_path)
    df = df[df['confidence'] > 0.5]
    df['time'] += user_start
    df = df[(df['time'] >= user_start) & (df['time'] <= user_end)]
    df['frequency'] = correct_crepe_octave(df['frequency'].values)
    crepe_times = df['time'].values
    crepe_pitches = df['frequency'].values
    aligned_pitches = []
    for t in midi_times:
        if len(crepe_times) == 0:
            aligned_pitches.append(None)
            continue
        else:
            idx = np.argmin(np.abs(crepe_times - t))
            aligned_pitches.append(round(crepe_pitches[idx], 2))
    return aligned_pitches

def align_crepe_to_midi_times(crepe_csv_path, midi_times, start_time, end_time):
    df = pd.read_csv(crepe_csv_path)
    df = df[df['confidence'] > 0.5]
    df['time'] += start_time
    df = df[(df['time'] >= start_time) & (df['time'] <= end_time)]
    df['frequency'] = correct_crepe_octave(df['frequency'].values)

    aligned_pitches = []
    crepe_times = df['time'].values
    crepe_pitches = df['frequency'].values

    for t in midi_times:
        if len(crepe_times) == 0:
            aligned_pitches.append(None)
            continue
        idx = np.argmin(np.abs(crepe_times - t))
        aligned_pitches.append(round(crepe_pitches[idx], 2))

    return aligned_pitches