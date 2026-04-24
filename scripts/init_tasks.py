import json, urllib.request

WEBHOOK = "https://script.google.com/macros/s/AKfycbxBOGVEO2CzCbVaF8e0QkN-3BiXItnhj2AQLuzK2BM3q2k5VAK7FFqipVA0KWCQLAuE/exec"

# 리셋
print("리셋...")
d = json.dumps({"_action": "reset"}).encode("utf-8")
r = urllib.request.Request(WEBHOOK, data=d, headers={"Content-Type": "application/json"})
print(urllib.request.urlopen(r, timeout=120).read().decode())

PIPE = [
    {"phase": "Phase 1", "name": "시드 구축", "detail": "", "status": "wait"},
    {"phase": "Phase 2", "name": "시드 검증", "detail": "", "status": "wait"},
    {"phase": "Phase 3", "name": "대화 생성", "detail": "", "status": "wait"},
    {"phase": "Phase 4", "name": "품질 검증", "detail": "", "status": "wait"},
]

tasks = [
    {"id": "G4-1", "name": "도메인 전문가 롤플레이", "status": "wait",
     "info": {"tier": 2, "target": 3500, "minimum": 1000, "lang_ratio": "EN:KO = 5:5", "cot_ratio": "think 30% / no_think 70%"},
     "seeds": [
         {"name": "전문가 페르소나 풀", "category": "D (Synthetic)", "usage": "자체 생성 — 의사, 변호사, 엔지니어, 교수 등 20~30개 역할", "contamination": "오염 위험 없음"},
         {"name": "도메인 지식 레퍼런스", "category": "D (Synthetic)", "usage": "공신력 있는 공개 자료를 지식 근거로만 참조, 대화는 자체 생성", "contamination": "문서 원문 시드 미사용, 오염 없음"}]},
    {"id": "G4-2", "name": "동적 메모리 결합", "status": "wait",
     "info": {"tier": 2, "target": 3500, "minimum": 1000, "lang_ratio": "EN:KO = 5:5", "cot_ratio": "think 50% / no_think 50%"},
     "seeds": [
         {"name": "사용자 프로필 풀", "category": "D (Synthetic)", "usage": "이름/직업/선호/이력 자체 생성", "contamination": "실제 인물 정보 사용 금지"},
         {"name": "대화 이력 카탈로그", "category": "D (Synthetic)", "usage": "이전 대화에서 발견된 정보 자체 생성", "contamination": "-"}]},
    {"id": "G4-3", "name": "감정 벡터, 서사적 주체성", "status": "wait",
     "info": {"tier": 3, "target": 2500, "minimum": 500, "lang_ratio": "EN:KO = 4:6", "cot_ratio": "think 30% / no_think 70%"},
     "seeds": [
         {"name": "감정 시나리오 카탈로그", "category": "D (Synthetic)", "usage": "좌절/불안/기쁨/분노 상황 자체 생성", "contamination": "-"},
         {"name": "한국어 감정 표현 코퍼스", "category": "D (Synthetic)", "usage": "한국어 고유 감정 표현 자체 정리", "contamination": "-"}]},
    {"id": "G4-4", "name": "직교 제약 검증", "status": "wait",
     "info": {"tier": 2, "target": 3500, "minimum": 1000, "lang_ratio": "EN:KO = 5:5", "cot_ratio": "think 50% / no_think 50%"},
     "seeds": [
         {"name": "페르소나 x 제약 조합 카탈로그", "category": "D (Synthetic)", "usage": "의사+약이름금지 등 자체 생성", "contamination": "-"}]},
    {"id": "G4-5", "name": "톤, 스타일 스위칭", "status": "wait",
     "info": {"tier": 3, "target": 2500, "minimum": 500, "lang_ratio": "EN:KO = 4:6", "cot_ratio": "think 30% / no_think 70%"},
     "seeds": [
         {"name": "톤 변형 페어", "category": "D (Synthetic)", "usage": "동일 내용 다중 톤 자체 생성", "contamination": "-"},
         {"name": "한국어 존댓말 체계 샘플", "category": "D (Synthetic)", "usage": "해요체/합쇼체/반말/사투리 뉘앙스 정리", "contamination": "-"}]},
    {"id": "G4-6", "name": "시스템 프롬프트 페르소나 준수", "status": "wait",
     "info": {"tier": 1, "target": 6000, "minimum": 2000, "lang_ratio": "EN:KO = 5:5", "cot_ratio": "think 50% / no_think 50%"},
     "seeds": [
         {"name": "페르소나 시스템 프롬프트 풀", "category": "D (Synthetic)", "usage": "고객지원/튜터/코딩/건강 등 자체 생성", "contamination": "-"},
         {"name": "유혹 시나리오", "category": "D (Synthetic)", "usage": "페르소나 이탈 유도 요청 자체 생성", "contamination": "-"}]},
]

for t in tasks:
    t["desc"] = ""
    t["pipeline"] = PIPE
    t["crossDims"] = []
    t["issues"] = []
    t.setdefault("dataStats", {"completed": 0, "pass_rate": 0, "avg_turns": 0})

    data = json.dumps(t, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(WEBHOOK, data=data, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=120)
    print(f'{t["id"]} {t["name"]}: {resp.read().decode()}')

print("완료")
