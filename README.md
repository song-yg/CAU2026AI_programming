# 🧊 FridgeMate

냉장고 재료를 기반으로 요리를 추천해주는 CLI 앱입니다.  
Python 순수 알고리즘 추천과 OpenRouter AI 기능을 함께 제공합니다.

---

## 📁 프로젝트 구조

```
fridgemate/
├── main.py              # 진입점 (메인 메뉴 루프)
├── fridge_manager.py    # 냉장고 재료 CRUD
├── recommender.py       # Python 알고리즘 레시피 추천 엔진
├── ai_helper.py         # OpenRouter AI API 연동 (모델 fallback 포함)
├── models.py            # 데이터 모델 (Ingredient, Recipe, UnitManager)
├── recipe_loader.py     # recipes.json 로더
├── meal_planner.py      # 3일 식단 생성
├── shopping_list.py     # 장보기 목록 생성
├── storage.py           # JSON 파일 입출력 (경로 안전 처리)
├── data/
│   ├── recipes.json     # 레시피 데이터 (300개+)
│   └── fridge.json      # 냉장고 저장 데이터 (자동 생성)
├── requirements.txt     # 의존 패키지
└── openrouter_key.txt   # (직접 생성) API 키 파일
```

---

## ⚙️ 설치 및 실행 (VS Code 기준)

### 0. 사전 확인 — Python이 설치되어 있는지 확인

VS Code 터미널을 열고(`Ctrl + `` ` ``) 아래 명령어를 입력합니다.

```bash
python --version
```

`Python 3.x.x` 같은 버전 번호가 나오면 정상입니다.  
아무것도 안 나오거나 오류가 뜨면 [python.org](https://www.python.org/downloads/)에서 Python을 먼저 설치하세요.  
설치 시 **"Add Python to PATH"** 체크박스를 반드시 체크해야 합니다.

---

### 1. 프로젝트 폴더 열기

VS Code 메뉴 → **File → Open Folder** → `fridgemat` 폴더 선택

> ⚠️ 반드시 **폴더 자체**를 열어야 합니다. 파일 하나만 열면 이후 경로 설정이 꼬입니다.

---

### 2. 터미널 열기

VS Code 상단 메뉴 → **Terminal → New Terminal**  
또는 단축키 **Ctrl + `` ` ``**

터미널 창이 아래쪽에 열리고, 프롬프트가 프로젝트 폴더 경로를 가리키고 있어야 합니다.

```
PS C:\...\fridgemate_full_menu_test_fixed>   ← 이런 형태면 정상
```

경로가 다르면 아래 명령어로 이동합니다.

```bash
cd fridgemate_full_menu_test_fixed
```

---

### 3. 가상환경 생성

```bash
python -m venv venv
```

성공하면 프로젝트 폴더 안에 `venv/` 폴더가 새로 생깁니다.  
아무 메시지 없이 프롬프트로 돌아오면 정상입니다.

> **가상환경이란?**  
> 이 프로젝트에서만 쓰는 패키지를 격리된 공간에 설치하는 방법입니다.  
> 컴퓨터 전체 Python 환경을 건드리지 않아서, 다른 프로젝트와 충돌이 생기지 않습니다.

---

### 4. 가상환경 활성화

**Windows (PowerShell) — VS Code 기본 터미널**

```powershell
.\venv\Scripts\Activate.ps1
```

활성화되면 프롬프트 앞에 `(venv)` 가 붙습니다.

```
(venv) PS C:\...\fridgemate_full_menu_test_fixed>
```

> ❗ **"이 시스템에서 스크립트를 실행할 수 없습니다"** 오류가 뜨는 경우  
> Windows 보안 정책이 스크립트 실행을 막고 있는 것입니다. 아래 명령어로 해제합니다.
>
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
>
> 이후 다시 `.\venv\Scripts\Activate.ps1` 을 실행합니다.

**macOS / Linux**

```bash
source venv/bin/activate
```

---

### 5. VS Code 인터프리터 설정

가상환경을 VS Code에도 알려줘야 자동완성, 오류 표시 등이 제대로 동작합니다.

1. **Ctrl + Shift + P** 를 눌러 명령 팔레트 열기
2. `Python: Select Interpreter` 입력 후 Enter
3. 목록에서 `.\venv\Scripts\python.exe` (Windows) 또는 `./venv/bin/python` (Mac/Linux) 선택  
   — `venv` 라고 표시된 항목을 고르면 됩니다.

이후부터 VS Code 터미널을 새로 열면 가상환경이 자동으로 활성화됩니다.

---

### 6. 패키지 설치

가상환경이 활성화된 상태(`(venv)` 가 프롬프트에 보이는 상태)에서 실행합니다.

```bash
pip install -r requirements.txt
```

설치가 끝나면 아래 명령어로 정상 설치를 확인합니다.

```bash
pip show requests
```

`Name: requests` 와 버전 정보가 출력되면 성공입니다.

---

### 7. AI 기능 사용 시 API 키 설정

VS Code 탐색기(왼쪽 파일 트리)에서 프로젝트 루트에 `openrouter_key.txt` 파일을 새로 만들고,  
키 값만 한 줄로 저장합니다.

```
sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> 따옴표, 공백, 줄바꿈 없이 키 문자열만 저장해야 합니다.

### 8. 실행

```bash
python main.py
```

터미널에 `레시피 N개를 불러왔습니다.` 메시지와 함께 메뉴가 뜨면 성공입니다.

---

## 🍳 메뉴 기능 설명

| 번호 | 메뉴 | 설명 |
|------|------|------|
| 1 | 냉장고 재료 추가 | 재료명·수량·단위·유통기한을 입력해 냉장고에 저장. AI가 활성화된 경우 오타, 영어 입력, 비표준 단위를 자동으로 정규화함 |
| 2 | 냉장고 재료 목록 보기 | 현재 냉장고에 저장된 재료 전체를 출력 |
| 3 | 유통기한 임박 재료 보기 | 3일 이내 유통기한 만료 재료를 강조 표시 |
| 4 | Python 레시피 추천 | 보유 재료 기반 점수 계산으로 Top 10 레시피 추천. AI 불필요 |
| 5 | 기본 조리법 보기 | 4번에서 추천된 요리 중 하나를 골라 조리법과 부족 재료 확인 |
| 6 | 요리 선택 후 재료 차감 | 요리를 완성했다고 표시하면 사용한 재료를 냉장고에서 자동 차감 |
| 7 | 장보기 목록 생성 | Top 5 추천 요리의 부족한 재료를 합산해 장보기 목록 출력 |
| 8 | 3일 식단 추천 | Top 6 추천 요리를 점심·저녁으로 배분한 3일 식단표 생성 |
| 9 | 재료 버리기 / 삭제 | 수량 일부 차감 또는 재료 완전 삭제 |
| 10 | AI 추천 재정렬 | Python 추천 결과를 AI에게 전달해 사용자 조건("매운 거 싫어요" 등)에 맞춰 재정렬 |
| 11 | AI 대체재 / 맞춤 조리법 | 부족한 재료의 대체재를 AI가 제안하고, 보유 재료 기준 맞춤 조리법을 다시 작성 |
| 0 | 종료 | 앱 종료 (냉장고 데이터는 자동 저장) |

---

## 🤖 AI 기능 상세
 
`ai_helper.py`는 [OpenRouter](https://openrouter.ai/) API를 통해 모델 4개를 순서대로 시도합니다.  
앞 모델이 실패(타임아웃, 오류 응답 등)하면 자동으로 다음 모델로 넘어갑니다.
 
| 우선순위 | 모델 ID | 과금 여부 |
|----------|---------|-----------|
| 1 | `google/gemini-pro-latest` | **유료** ($2/M input) |
| 2 | `openai/gpt-5.2-pro` | **유료** ($21/M input) |
| 3 | `nvidia/llama-3.1-nemotron-ultra-253b-v1:free` | 무료 |
| 4 | `deepseek/deepseek-chat-v3-0324:free` | 무료 |
 
> ⚠️ **1번, 2번 모델은 유료입니다.**  
> OpenRouter 계정에 크레딧이 없으면 순서대로 실패하고 3번(무료)으로 자동 넘어갑니다.  

**재료 입력 시 AI 정규화 (`convert_ingredient_unit`)**  
- `egg`, `달걀`, `삶은계란` → `계란 2개` 로 자동 변환  
- `봉지`, `팩` 같은 비표준 단위를 `g`, `ml`, `개` 등 recipes.json 기준 단위로 변환  

---

## 🔧 추천 점수 계산 방식

```
점수 = 재료일치율(%)
     + 20 × 유통기한임박점수
     - 5  × 부족재료수
     - 0.3 × 조리시간(분)
```

- **재료 일치율**: 보유 재료 / 레시피 필요 재료 (%)
- **유통기한 임박 점수**: 각 재료의 `1 / (남은 일수 + 1)` 합산 → 곧 버려질 재료를 먼저 쓰도록 유도
- **부족 재료 페널티**: 부족한 재료 하나당 -5점
- **조리시간 페널티**: 분당 -0.3점

---

## 📝 데이터 형식

### fridge.json (자동 저장)

```json
[
  {"name": "계란", "quantity": 6, "unit": "개", "expire_days": 14},
  {"name": "대파", "quantity": 200, "unit": "g", "expire_days": 5}
]
```

### recipes.json (재료 항목 예시)

```json
{
  "name": "계란볶음밥",
  "minutes": 15,
  "spicy_level": 0,
  "instructions": "...",
  "used_ingredients": [
    {"name": "계란", "amount": 2, "unit": "개"},
    {"name": "대파", "amount": 30, "unit": "g"}
  ]
}

---
