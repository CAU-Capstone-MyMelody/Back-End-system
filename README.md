# MyMelody 백엔드 시스템


### main.py

업로드된 음원에서 다음 과정을 통해 보컬의 피치를 추출합니다:

1. 파일을 `.wav`로 변환
2. 보컬/반주 분리 (`htdemucs` 사용 예상)
3. 무음 구간 제거 및 필터링
4. CREPE를 이용한 피치 분석
5. 시간별 피치 추세, 최대/최소 피치 반환

특정 시간 구간에 대해 MIDI와 정렬된 피치를 비교 분석합니다:

- 입력: 음성 파일 + 시작 시간(`start_time`) + 종료 시간(`end_time`)
- mid을 기준으로 MIDI 피치 추출
- CREPE 결과와 MIDI 구간을 정렬하여 비교
- 반환값: 시간, 원본(MIDI) 피치, 녹음된 피치



## 참고한 프로젝트

- [CREPE: A Convolutional Representation for Pitch Estimation](https://github.com/marl/crepe.git)  
  피치 인식 모델 구현에 있어 CREPE의 코드와 구조를 참고하였습니다.

CREPE는 음악 정보 검색(MIR)을 위한 고정밀 피치 추정 딥러닝 모델입니다. 본 프로젝트에서는 CREPE의 구조 및 코드 일부를 기반으로 하여, 고유의 기능과 처리 과정을 추가하여 개발하였습니다.
