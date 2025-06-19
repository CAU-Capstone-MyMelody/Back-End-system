from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import tempfile
from melon import ChartData
import shutil


from audio_utils import (
    separate_vocals,
    remove_silence_and_filter,
    run_crepe,
    extract_midi_json,
    align_crepe_to_midi_times,
    convert_to_wav
)

from audio import process_audio_pitches


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze0")
async def analyze(
    file: UploadFile = File(...)
):
    tmp_dir = tempfile.mkdtemp()
    try:
        audio_path = os.path.join(tmp_dir, file.filename)
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        wav_path = os.path.join(tmp_dir, "converted.wav")
        convert_to_wav(audio_path, wav_path)

        vocals_path = separate_vocals(wav_path, tmp_dir)

        cleaned_wav = os.path.join(tmp_dir, "cleaned.wav")
        remove_silence_and_filter(vocals_path, cleaned_wav)

        crepe_csv = run_crepe(cleaned_wav, tmp_dir)

        times, audio_pitches, max_pitch, min_pitch = process_audio_pitches(crepe_csv)

        return JSONResponse(content={
            "time": [round(t, 2) for t in times],
            "recordedPitch": audio_pitches,
            "max_pitch": max_pitch,
            "min_pitch": min_pitch
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        shutil.rmtree(tmp_dir)

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...), 
    start_time: float = Form(...),
    end_time: float = Form(...)
):
    tmp_dir = tempfile.mkdtemp()
    try:
        audio_path = os.path.join(tmp_dir, file.filename)
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        wav_path = os.path.join(tmp_dir, "converted.wav")
        convert_to_wav(audio_path, wav_path)

        vocals_path = separate_vocals(wav_path, tmp_dir)

        cleaned_wav = os.path.join(tmp_dir, "cleaned.wav")
        remove_silence_and_filter(vocals_path, cleaned_wav)
        


        crepe_csv = run_crepe(cleaned_wav, tmp_dir)


        midi_path = "벚꽃엔딩.mid"
        midi_times, midi_pitches = extract_midi_json(midi_path, start_time, end_time)

        
        audio_pitches = align_crepe_to_midi_times(crepe_csv, midi_times, start_time, end_time)

        return JSONResponse(content={
            "time": midi_times,
            "originalPitch": midi_pitches,
            "recordedPitch": audio_pitches
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        shutil.rmtree(tmp_dir)
        
@app.post("/analyze2")
async def analyze2(
    file: UploadFile = File(...), 
    start_time: float = Form(...),
    end_time: float = Form(...)
):
    tmp_dir = tempfile.mkdtemp()
    try:
        audio_path = os.path.join(tmp_dir, file.filename)
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        wav_path = os.path.join(tmp_dir, "converted.wav")
        convert_to_wav(audio_path, wav_path)

        vocals_path = separate_vocals(wav_path, tmp_dir)

        cleaned_wav = os.path.join(tmp_dir, "cleaned.wav")
        remove_silence_and_filter(vocals_path, cleaned_wav)


        crepe_csv = run_crepe(cleaned_wav, tmp_dir)


        midi_path = "헤어지자말해요수정BPM68.mid"
        midi_times, midi_pitches = extract_midi_json(midi_path, start_time, end_time)

        
        audio_pitches = align_crepe_to_midi_times(crepe_csv, midi_times, start_time, end_time)

        return JSONResponse(content={
            "time": midi_times,
            "originalPitch": midi_pitches,
            "recordedPitch": audio_pitches
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        shutil.rmtree(tmp_dir)
        
        
@app.post("/analyze3")
async def analyze3(
    file: UploadFile = File(...), 
    start_time: float = Form(...),
    end_time: float = Form(...)
):
    tmp_dir = tempfile.mkdtemp()
    try:
        audio_path = os.path.join(tmp_dir, file.filename)
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        wav_path = os.path.join(tmp_dir, "converted.wav")
        convert_to_wav(audio_path, wav_path)

        vocals_path = separate_vocals(wav_path, tmp_dir)

        cleaned_wav = os.path.join(tmp_dir, "cleaned.wav")
        remove_silence_and_filter(vocals_path, cleaned_wav)


        crepe_csv = run_crepe(cleaned_wav, tmp_dir)


        midi_path = "아무노래_수정2.mid"
        midi_times, midi_pitches = extract_midi_json(midi_path, start_time, end_time)

        
        audio_pitches = align_crepe_to_midi_times(crepe_csv, midi_times, start_time, end_time)

        return JSONResponse(content={
            "time": midi_times,
            "originalPitch": midi_pitches,
            "recordedPitch": audio_pitches
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        shutil.rmtree(tmp_dir)
        
@app.get("/melon-chart")
def get_melon_chart():
    chart = ChartData()
    chart_data = [json.loads(song.json()) for song in chart[:100]]
    return chart_data  # FastAPI가 자동으로 JSON 응답 처리