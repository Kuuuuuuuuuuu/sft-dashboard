import json, urllib.request

WEBHOOK = "https://script.google.com/macros/s/AKfycbxBOGVEO2CzCbVaF8e0QkN-3BiXItnhj2AQLuzK2BM3q2k5VAK7FFqipVA0KWCQLAuE/exec"

tasks = [
    {"id": "G4-1", "seeds": [
        {"name": "전문가 페르소나 풀", "category": "D (Synthetic)", "usage": "자체 생성 — 의사, 변호사, 엔지니어 등", "contamination": "오염 위험 없음", "count": 30},
        {"name": "도메인 지식 레퍼런스", "category": "D (Synthetic)", "usage": "공신력 있는 공개 자료를 지식 근거로만 참조", "contamination": "오염 없음", "count": 260}]},
    {"id": "G4-2", "seeds": [
        {"name": "사용자 프로필 풀", "category": "D (Synthetic)", "usage": "이름/직업/선호/이력 자체 생성", "contamination": "실제 인물 정보 사용 금지", "count": 500},
        {"name": "대화 이력 카탈로그", "category": "D (Synthetic)", "usage": "이전 대화에서 발견된 정보 자체 생성", "contamination": "-", "count": 1200}]},
    {"id": "G4-3", "seeds": [
        {"name": "감정 시나리오 카탈로그", "category": "D (Synthetic)", "usage": "좌절/불안/기쁨/분노 상황 자체 생성", "contamination": "-", "count": 100},
        {"name": "한국어 감정 표현 코퍼스", "category": "D (Synthetic)", "usage": "한국어 고유 감정 표현 자체 정리", "contamination": "-", "count": 100}]},
    {"id": "G4-4", "seeds": [
        {"name": "페르소나 x 제약 조합 카탈로그", "category": "D (Synthetic)", "usage": "의사+약이름금지 등 자체 생성", "contamination": "-", "count": 350}]},
    {"id": "G4-5", "seeds": [
        {"name": "톤 변형 페어", "category": "D (Synthetic)", "usage": "동일 내용 다중 톤 자체 생성", "contamination": "-", "count": 600},
        {"name": "한국어 존댓말 체계 샘플", "category": "D (Synthetic)", "usage": "해요체/합쇼체/반말/사투리 뉘앙스 정리", "contamination": "-", "count": 9}]},
    {"id": "G4-6", "seeds": [
        {"name": "페르소나 시스템 프롬프트 풀", "category": "D (Synthetic)", "usage": "고객지원/튜터/코딩/건강 등 자체 생성", "contamination": "-", "count": 20000},
        {"name": "유혹 시나리오", "category": "D (Synthetic)", "usage": "페르소나 이탈 유도 요청 자체 생성", "contamination": "-", "count": 5000}]},
]

for t in tasks:
    data = json.dumps(t, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(WEBHOOK, data=data, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=120)
    print(f'{t["id"]}: {resp.read().decode()}')
print("완료")
