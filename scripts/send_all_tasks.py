import json, urllib.request

WEBHOOK = "https://script.google.com/macros/s/AKfycbxBOGVEO2CzCbVaF8e0QkN-3BiXItnhj2AQLuzK2BM3q2k5VAK7FFqipVA0KWCQLAuE/exec"

tasks = [
    {
        "id": "G4-2", "name": "동적 메모리 결합",
        "desc": "이전 대화 이력과 사용자 프로필을 결합하여 맥락 연속성 유지",
        "status": "wait",
        "info": {"tier": 2, "target": 3500, "minimum": 1000, "lang_ratio": "EN:KO = 5:5", "cot_ratio": "think 50% / no_think 50%"},
        "seeds": [
            {"name": "사용자 프로필 풀", "category": "D (Synthetic)", "usage": "이름/직업/선호/이력 자체 생성", "contamination": "실제 인물 정보 사용 금지"},
            {"name": "대화 이력 카탈로그", "category": "D (Synthetic)", "usage": "이전 대화에서 발견된 정보 자체 생성", "contamination": "-"}
        ],
        "crossDims": [],
        "dataStats": {"completed": 0, "pass_rate": 0, "avg_turns": 0, "lang": {"EN": 50, "KO": 50}, "cot": {"think": 50, "no_think": 50}, "domains": []},
        "pipeline": [
            {"phase": "Phase 1", "name": "시드 구축", "detail": "사용자 프로필 풀, 대화 이력 카탈로그", "status": "wait"},
            {"phase": "Phase 2", "name": "시드 검증", "detail": "프로필 일관성, 이력 맥락 정합성", "status": "wait"},
            {"phase": "Phase 3", "name": "대화 생성", "detail": "이력+프로필 결합, 맥락 연속성 유지", "status": "wait"},
            {"phase": "Phase 4", "name": "품질 검증", "detail": "맥락 일관성, 메모리 활용도", "status": "wait"}
        ],
        "issues": []
    },
    {
        "id": "G4-3", "name": "감정 벡터·서사성·주체성",
        "desc": "감정 표현의 벡터 변화, 서사적 흐름, 주체적 의사결정 대화",
        "status": "wait",
        "info": {"tier": 3, "target": 2500, "minimum": 500, "lang_ratio": "EN:KO = 4:6", "cot_ratio": "think 30% / no_think 70%"},
        "seeds": [
            {"name": "감정 시나리오 카탈로그", "category": "D (Synthetic)", "usage": "좌절/불안/기쁨/분노 상황 자체 생성", "contamination": "-"},
            {"name": "한국어 감정 표현 코퍼스", "category": "D (Synthetic)", "usage": "한국어 고유 감정 표현 자체 정리", "contamination": "-"}
        ],
        "crossDims": [],
        "dataStats": {"completed": 0, "pass_rate": 0, "avg_turns": 0, "lang": {"EN": 40, "KO": 60}, "cot": {"think": 30, "no_think": 70}, "domains": []},
        "pipeline": [
            {"phase": "Phase 1", "name": "시드 구축", "detail": "감정 시나리오 카탈로그, 감정 표현 코퍼스", "status": "wait"},
            {"phase": "Phase 2", "name": "시드 검증", "detail": "감정 벡터 분류, 시나리오 다양성", "status": "wait"},
            {"phase": "Phase 3", "name": "대화 생성", "detail": "감정 전이 흐름, 주체적 의사결정", "status": "wait"},
            {"phase": "Phase 4", "name": "품질 검증", "detail": "감정 일관성, 서사 진행도", "status": "wait"}
        ],
        "issues": []
    },
    {
        "id": "G4-4", "name": "직교 제약 검증",
        "desc": "다중 제약 조건을 동시에 만족시키는 정밀 수행 학습 데이터",
        "status": "wait",
        "info": {"tier": 2, "target": 3500, "minimum": 1000, "lang_ratio": "EN:KO = 5:5", "cot_ratio": "think 50% / no_think 50%"},
        "seeds": [
            {"name": "페르소나 x 제약 조합 카탈로그", "category": "D (Synthetic)", "usage": "의사+약이름금지 등 자체 생성", "contamination": "-"}
        ],
        "crossDims": [],
        "dataStats": {"completed": 0, "pass_rate": 0, "avg_turns": 0, "lang": {"EN": 50, "KO": 50}, "cot": {"think": 50, "no_think": 50}, "domains": []},
        "pipeline": [
            {"phase": "Phase 1", "name": "시드 구축", "detail": "페르소나x제약 조합 카탈로그", "status": "wait"},
            {"phase": "Phase 2", "name": "시드 검증", "detail": "제약 충돌/양립, 난이도 확인", "status": "wait"},
            {"phase": "Phase 3", "name": "대화 생성", "detail": "다중 제약 동시 적용", "status": "wait"},
            {"phase": "Phase 4", "name": "품질 검증", "detail": "제약 충족 전수 검증", "status": "wait"}
        ],
        "issues": []
    },
    {
        "id": "G4-5", "name": "톤·스타일 스위칭",
        "desc": "동일 내용을 다양한 톤/존댓말 체계로 전환하는 대화",
        "status": "wait",
        "info": {"tier": 3, "target": 2500, "minimum": 500, "lang_ratio": "EN:KO = 4:6", "cot_ratio": "think 30% / no_think 70%"},
        "seeds": [
            {"name": "톤 변형 페어", "category": "D (Synthetic)", "usage": "동일 내용 다중 톤 자체 생성", "contamination": "-"},
            {"name": "한국어 존댓말 체계 샘플", "category": "D (Synthetic)", "usage": "해요체/합쇼체/반말/사투리 뉘앙스 정리", "contamination": "-"}
        ],
        "crossDims": [],
        "dataStats": {"completed": 0, "pass_rate": 0, "avg_turns": 0, "lang": {"EN": 40, "KO": 60}, "cot": {"think": 30, "no_think": 70}, "domains": []},
        "pipeline": [
            {"phase": "Phase 1", "name": "시드 구축", "detail": "톤 변형 페어, 존댓말 체계 샘플", "status": "wait"},
            {"phase": "Phase 2", "name": "시드 검증", "detail": "톤 분류 체계, 페어 품질", "status": "wait"},
            {"phase": "Phase 3", "name": "대화 생성", "detail": "톤 전환 요청, 스타일 일관성", "status": "wait"},
            {"phase": "Phase 4", "name": "품질 검증", "detail": "톤 정확도, 뉘앙스 자연스러움", "status": "wait"}
        ],
        "issues": []
    },
    {
        "id": "G4-6", "name": "시스템 프롬프트 페르소나 준수",
        "desc": "시스템 프롬프트 페르소나를 유혹/이탈 시도에도 유지하는 대화",
        "status": "wait",
        "info": {"tier": 1, "target": 6000, "minimum": 2000, "lang_ratio": "EN:KO = 5:5", "cot_ratio": "think 50% / no_think 50%"},
        "seeds": [
            {"name": "페르소나 시스템 프롬프트 풀", "category": "D (Synthetic)", "usage": "고객지원/튜터/코딩/건강 등 자체 생성", "contamination": "-"},
            {"name": "유혹 시나리오", "category": "D (Synthetic)", "usage": "페르소나 이탈 유도 요청 자체 생성", "contamination": "-"}
        ],
        "crossDims": [],
        "dataStats": {"completed": 0, "pass_rate": 0, "avg_turns": 0, "lang": {"EN": 50, "KO": 50}, "cot": {"think": 50, "no_think": 50}, "domains": []},
        "pipeline": [
            {"phase": "Phase 1", "name": "시드 구축", "detail": "페르소나 프롬프트 풀, 유혹 시나리오", "status": "wait"},
            {"phase": "Phase 2", "name": "시드 검증", "detail": "프롬프트 완성도, 유혹 난이도", "status": "wait"},
            {"phase": "Phase 3", "name": "대화 생성", "detail": "정상 대화+유혹 삽입, 페르소나 유지", "status": "wait"},
            {"phase": "Phase 4", "name": "품질 검증", "detail": "이탈 여부, 일관성 점수", "status": "wait"}
        ],
        "issues": []
    }
]

for t in tasks:
    data = json.dumps(t, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(WEBHOOK, data=data, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=120)
    print(f'{t["id"]}: {resp.read().decode()}')

print("완료")
