# MyMelody 백엔드 시스템


### 개발 기능

업로드된 음원에서 다음 과정을 통해 보컬의 피치를 추출합니다:

1. 파일을 `.wav`로 변환
2. 보컬/반주 분리 
3. 무음 구간 제거 및 필터링
4. CREPE를 이용한 피치 분석
5. 시간별 피치 추세, 최대/최소 피치 반환

특정 시간 구간에 대해 MIDI와 정렬된 피치를 비교 분석합니다:

- 입력: 음성 파일 + 시작 시간(`start_time`) + 종료 시간(`end_time`)
- mid을 기준으로 MIDI 피치 추출
- CREPE 결과와 MIDI 구간을 정렬하여 비교
- 반환값: 시간, 원본(MIDI) 피치, 녹음된 피치

- MelonChart API (`melody.melon.ChartData`)를 활용하여
- 최신 멜론 차트 상위 100곡의 메타데이터(JSON)를 반환합니다.

## 주요 파일 및 기능 설명

이 프로젝트는 FastAPI를 기반으로 하여, 오디오 분석 및 피치 비교 기능을 제공합니다. 주요 파일별 역할은 다음과 같습니다:

---

### `main.py`  
**FastAPI 백엔드 서버의 진입점**

- API 엔드포인트 정의 (`/analyze`, `/analyze2`, `/analyze3`, `/melon-chart` 등)
- CORS 설정 및 파일 처리 흐름 제어
- 업로드된 오디오를 임시 폴더에 저장하고, 전처리 및 분석 처리 호출

---

### `audio_utils.py`  
**오디오 전처리 및 피치 분석 관련 유틸리티**

- `convert_to_wav` : 업로드된 파일을 `.wav`로 변환  
- `separate_vocals` : 보컬/반주 분리 (예상: Demucs 기반)  
- `remove_silence_and_filter` : 무음 구간 제거 및 필터링  
- `run_crepe` : CREPE 모델을 실행하여 피치 추출  
- `extract_midi_json` : MIDI 파일로부터 시간 및 피치 정보 추출  
- `align_crepe_to_midi_times` : CREPE 결과를 MIDI 시간에 정렬

---

### `audio.py`  
**CREPE 분석 후 데이터 후처리 담당**

- `process_audio_pitches` : CREPE의 CSV 결과를 기반으로 시간, 피치, 최고/최저 피치 계산

---

### `melon.py`  
**멜론 차트 데이터 수집 모듈**

- `ChartData` 클래스: 멜론 실시간 차트(100곡)의 메타데이터 수집 및 JSON 변환

---

### `.mid` 파일들  
**기준이 되는 원본 노래의 MIDI 파일**

- `벚꽃엔딩.mid`, `헤어지자말해요수정BPM68.mid`, `아무노래_수정2.mid` 등  
- 업로드된 음원과 비교 분석할 기준 피치 정보를 제공


## 환경 세팅 (개발 환경)
- Python 3.10.13 권장
- 가상환경 사용 권장 (venv, conda 등)
- GPU 사용을 강력히 권장 (PyTorch 기반 모델 사용)
- pip install -r requirements.txt

---

## 참고한 프로젝트

- [CREPE: A Convolutional Representation for Pitch Estimation](https://github.com/marl/crepe.git)  
  피치 인식 모델 구현에 있어 CREPE의 코드와 구조를 참고하였습니다.

CREPE는 음악 정보 검색(MIR)을 위한 고정밀 피치 추정 딥러닝 모델입니다. 본 프로젝트에서는 CREPE의 구조 및 코드 일부를 기반으로 하여, 고유의 기능과 처리 과정을 추가하여 개발하였습니다.

`crepe/` 폴더를 프로젝트 내에 추가한 후, 해당 폴더 안에 있는 `setup.py`를 통해 CREPE를 로컬에 설치해야 합니다.
