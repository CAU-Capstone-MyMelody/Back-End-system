from melon import ChartData
import json

# 차트 데이터 가져오기
chart = ChartData()

# 전체 곡 정보를 파싱해서 리스트로 저장
chart_data = [json.loads(song.json()) for song in chart[:100]]


# 하나의 JSON으로 출력
print(json.dumps(chart_data, ensure_ascii=False, indent=2))