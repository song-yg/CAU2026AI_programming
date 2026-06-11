# 🧊 FridgeMate

냉장고 재료를 기반으로 요리를 추천해주는 CLI 앱입니다.
Python 순수 알고리즘 추천과 OpenRouter AI 기능을 함께 제공합니다.

AI 기능을 사용할 수 없는 경우에도 프로그램은 중단되지 않으며, Python 기본 추천 기능으로 계속 사용할 수 있습니다.

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
│   ├── recipes.json     # 레시피 데이터 (300개)
│   └── fridge.json      # 냉장고 저장 데이터
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
설치 시 **"Add Python to PATH"** 체크박스를 반드시 체크하는 것을 권장합니다.

Windows 환경에서 `python` 명령어가 작동하지 않는 경우 아래 명령어를 사용할 수 있습니다.

```bash
py --version
```

---

### 1. 프로젝트 폴더 열기

VS Code 메뉴 → **File → Open Folder** → `fridgemate` 폴더 선택

> ⚠️ 반드시 **폴더 자체**를 열어야 합니다. 파일 하나만 열면 이후 경로 설정이 꼬일 수 있습니다.

---

### 2. 터미널 열기

VS Code 상단 메뉴 → **Terminal → New Terminal**
또는 단축키 **Ctrl + `` ` ``**

터미널 창이 아래쪽에 열리고, 프롬프트가 프로젝트 폴더 경로를 가리키고 있어야 합니다.

```
PS C:\...\fridgemate>   ← 이런 형태면 정상
```

경로가 다르면 아래 명령어로 이동합니다.

```bash
cd fridgemate
```

---

### 3. 가상환경 생성

```bash
python -m venv venv
```

성공하면 프로젝트 폴더 안에 `venv/` 폴더가 새로 생깁니다.
아무 메시지 없이 프롬프트로 돌아오면 정상입니다.

#### 3-1. 먹통인데요?

```bash
PS C:\...\fridgemate> python -m venv venv
Python
```

만일 위와 같이 터미널이 반응하고 `venv/` 폴더가 새로 생기지 않는다면, Windows의 Python 실행 별칭 문제일 수 있습니다. 다음 해결 방식을 따라주세요.

**1단계**

* 시작 메뉴 → "앱 실행 별칭 관리" 검색 후 열기
* Python 항목을 모두 끄기

**2단계**

* 그 다음 다시 시도

```bash
python --version
```

정상적인 버전 번호가 뜨면 다시 `python -m venv venv`를 실행합니다.

그래도 작동하지 않으면 아래 명령어를 사용할 수 있습니다.

```bash
py -m venv venv
```

---

### 4. 가상환경 활성화

**Windows (PowerShell) — VS Code 기본 터미널**

```powershell
.\venv\Scripts\Activate.ps1
```

활성화되면 프롬프트 앞에 `(venv)` 가 붙습니다.

```
(venv) PS C:\...\fridgemate>
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
pip install requests
```

설치가 끝나면 아래 명령어로 정상 설치를 확인합니다.

```bash
pip show requests
```

`Name: requests` 와 버전 정보가 출력되면 성공입니다.

만약 `pip` 명령어가 작동하지 않으면 아래 명령어를 사용할 수 있습니다.

```bash
py -m pip install requests
```

---

### 7. AI 기능 사용 시 API 키 설정

VS Code 탐색기(왼쪽 파일 트리)에서 프로젝트 루트에 `openrouter_key.txt` 파일을 새로 만들고,
키 값만 한 줄로 저장합니다.

```
sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> 따옴표, 공백, 줄바꿈 없이 키 문자열만 저장해야 합니다.

`openrouter_key.txt` 파일은 `main.py`와 같은 위치에 있어야 합니다.

```
fridgemate/
├── main.py
├── ai_helper.py
├── openrouter_key.txt
└── data/
```

API 키가 없어도 프로그램은 실행됩니다.
다만 AI 관련 기능은 사용할 수 없으며, Python 기본 추천 기능으로 진행됩니다.

### 8. 실행

```bash
python main.py
```

위를 터미널에 붙여넣거나, `main.py`에서 실행 버튼을 눌러 실행합니다.

Windows에서 `python` 명령어가 작동하지 않으면 아래 명령어를 사용할 수 있습니다.

```bash
py main.py
```

터미널에 `레시피 300개를 불러왔습니다.` 메시지와 함께 메뉴가 뜨면 성공입니다.

---

## 🍳 메뉴 기능 설명

| 번호 | 메뉴              | 설명                                                                                 |
| -- | --------------- | ---------------------------------------------------------------------------------- |
| 1  | 냉장고 재료 추가       | 재료명·수량(숫자만)·단위(개, g 등)·유통기한을 입력해 냉장고에 저장. AI가 활성화된 경우 오타, 영어 입력, 비표준 단위를 자동으로 정규화함 |
| 2  | 냉장고 재료 목록 보기    | 현재 냉장고에 저장된 재료 전체를 출력. 같은 재료라도 유통기한이 다르면 따로 관리됨                                    |
| 3  | 유통기한 임박 재료 보기   | 유통기한이 가까운 재료를 강조 표시                                                                |
| 4  | Python 레시피 추천   | 보유 재료 기반 점수 계산으로 Top 10 레시피 추천. AI 불필요                                             |
| 5  | 기본 조리법 보기       | 4번에서 추천된 요리 중 하나를 골라 조리법과 부족 재료 확인                                                 |
| 6  | 요리 선택 후 재료 차감   | 요리를 완성했다고 표시하면 사용한 재료를 냉장고에서 자동 차감. 부족한 재료가 있으면 차감하지 않음                            |
| 7  | 장보기 목록 생성       | Top 5 추천 요리의 부족한 재료를 합산해 장보기 목록 출력                                                 |
| 8  | 3일 식단 추천        | Top 6 추천 요리를 점심·저녁으로 배분한 3일 식단표 생성                                                 |
| 9  | 재료 버리기 / 삭제     | 수량 일부 차감 또는 재료 완전 삭제                                                               |
| 10 | AI 추천 재정렬       | Python 추천 결과를 AI에게 전달해 사용자 조건("매운 거 싫어요" 등)에 맞춰 재정렬                                |
| 11 | AI 대체재 / 맞춤 조리법 | 부족한 재료의 대체재를 AI가 제안하고, 보유 재료 기준 맞춤 조리법을 다시 작성                                      |
| 0  | 종료              | 앱 종료 (냉장고 데이터는 자동 저장)                                                              |

---

## 🤖 AI 기능 상세

`ai_helper.py`는 OpenRouter API를 통해 여러 모델을 순서대로 시도합니다.
앞 모델이 실패(타임아웃, 오류 응답, 사용량 제한 등)하면 자동으로 다음 모델로 넘어갑니다.

| 우선순위 | 모델 ID                                          | 과금 여부                 |
| ---- | ---------------------------------------------- | --------------------- |
| 1    | `deepseek/deepseek-chat-v3-0324`               | 유료 또는 계정 상태에 따라 제한 가능 |
| 2    | `nvidia/llama-3.1-nemotron-ultra-253b-v1:free` | 무료                    |
| 3    | `deepseek/deepseek-r1:free`                    | 무료                    |
| 4    | `meta-llama/llama-3.3-70b-instruct:free`       | 무료                    |
| 5    | `openrouter/free`                              | 무료 예비 라우터             |

> ⚠️ 모델 제공 상태와 무료 사용 가능 여부는 OpenRouter 상황에 따라 달라질 수 있습니다.
> 앞 모델이 실패하면 다음 모델로 자동 전환되며, 모든 모델이 실패하면 Python 기본 추천 방식으로 진행됩니다.

AI 호출이 실패해도 프로그램은 종료되지 않습니다.
이 경우 아래와 같은 안내 메시지가 출력됩니다.

```
AI 추천 기능을 잠시 사용할 수 없어 기본 추천 방식으로 진행합니다.
```

**재료 입력 시 AI 정규화 (`convert_ingredient_unit`)**

* `egg`, `달걀`, `eggg` → `계란` 으로 자동 변환
* `milk` → `우유` 로 자동 변환
* `tofu` → `두부` 로 자동 변환
* `파`, `green onion`, `scallion` → `대파` 로 자동 변환
* `파 1단` → `대파 300g` 처럼 비표준 단위를 표준 단위로 변환
* `계란 1판` → `계란 30개` 처럼 묶음 단위를 계산 가능한 단위로 변환
* `봉지`, `팩` 같은 비표준 단위를 `g`, `ml`, `개` 등 recipes.json 기준 단위로 변환

식재료로 판단하기 어려운 입력은 무리하게 다른 재료로 바꾸지 않고 거부하도록 설계되어 있습니다.
이를 통해 잘못된 입력이 냉장고 데이터에 저장되는 것을 방지합니다.

---

## 🔧 추천 점수 계산 방식

```
점수 = 재료일치율(%)
     + 20 × 유통기한임박점수
     - 5  × 부족재료수
     - 0.3 × 조리시간(분)
```

* **재료 일치율**: 보유 재료 / 레시피 필요 재료 (%)
* **유통기한 임박 점수**: 각 재료의 `1 / (남은 일수 + 1)` 합산 → 곧 버려질 재료를 먼저 쓰도록 유도
* **부족 재료 페널티**: 부족한 재료 하나당 -5점
* **조리시간 페널티**: 분당 -0.3점
