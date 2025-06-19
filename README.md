# MyMelody Back-End System

### Development Features

This system extracts vocal pitch from an uploaded audio file through the following steps:

1. Convert the file to `.wav` format  
2. Separate vocals and accompaniment  
3. Remove silence and apply filtering  
4. Analyze pitch using the CREPE model  
5. Return pitch trends over time, including max/min pitch values  

It also performs pitch comparison aligned with MIDI data within a specific time range:

- Input: Audio file + start time (`start_time`) + end time (`end_time`)  
- Extract pitch information from a reference `.mid` file  
- Align the CREPE output to the MIDI time intervals  
- Return: time array, original pitch (from MIDI), recorded pitch (from audio)

MelonChart API (`melody.melon.ChartData`) is used to:
- Retrieve metadata (in JSON format) for the top 100 tracks on the real-time Melon chart.

---

## Key Files and Functional Overview

This project is based on FastAPI and provides audio pitch analysis and comparison features. Below are the roles of each major file:

---

### `main.py`  
**Entry point of the FastAPI backend server**

- Defines API endpoints (`/analyze`, `/analyze2`, `/analyze3`, `/melon-chart`, etc.)
- Configures CORS and controls file processing flow
- Temporarily saves uploaded audio and calls preprocessing and analysis logic

---

### `audio_utils.py`  
**Audio preprocessing and pitch analysis utilities**

- `convert_to_wav`: Converts uploaded files to `.wav`  
- `separate_vocals`: Separates vocals and accompaniment (likely using Demucs)  
- `remove_silence_and_filter`: Removes silent segments and filters noise  
- `run_crepe`: Runs the CREPE model to extract pitch  
- `extract_midi_json`: Extracts time and pitch data from MIDI files  
- `align_crepe_to_midi_times`: Aligns CREPE output with MIDI timing

---

### `audio.py`  
**Post-processing CREPE analysis data**

- `process_audio_pitches`: Calculates time series, pitch, and max/min values from CREPE CSV output

---

### `melon_chat.py`  
**Melon chart data collection module**

- `ChartData` class: Fetches metadata for the top 100 real-time songs from Melon and converts it to JSON

---

### `.mid` files  
**Reference MIDI files used for pitch comparison**

- `벚꽃엔딩.mid`, `헤어지자말해요수정BPM68.mid`, `아무노래_수정2.mid`, etc.  
- Used as reference pitch data for comparison with user audio

---

## Environment Setup (Development Environment)

- Python 3.10.13 is recommended  
- Use of virtual environments is highly recommended (venv, conda, etc.)  
- GPU usage is strongly recommended (CREPE and Demucs are PyTorch-based)  


Install dependencies via:

```bash
pip install -r requirements.txt ```


---

## 🔧 How to Run Locally

To run the FastAPI server locally with auto-reloading:

```bash
uvicorn main:app --reload ```


---

## Referenced Project

- [CREPE: A Convolutional Representation for Pitch Estimation](https://github.com/marl/crepe.git)  
  We referred to the code and structure of CREPE for implementing the pitch detection functionality.

CREPE is a high-accuracy deep learning model for pitch estimation in music information retrieval (MIR).  
In this project, we used parts of CREPE’s architecture and code as a foundation, and extended it with our own features and processing steps.

After placing the `crepe/` and `model/` folders into the project directory, you must install CREPE locally using the `setup.py` inside the folder.
