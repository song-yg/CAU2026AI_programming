import os
import json
import re

try:
    import requests
except Exception:
    requests = None


class AIHelper:
    def __init__(self):
        self.url = "https://openrouter.ai/api/v1/chat/completions"

        # AI 모델 우선순위
        # 1번 모델이 실패하면 2번, 2번이 실패하면 3번 모델을 자동으로 시도합니다.
        self.models = [
            "nvidia/nemotron-3-super-120b-a12b:free",
            "deepseek/deepseek-v4-flash:free",
            "google/gemma-4-31b-it:free",
        ]

        # 기존 코드에서 self.model을 참조해도 깨지지 않게 첫 번째 모델을 넣어둡니다.
        self.model = self.models[0]

        # API 키 읽기
        self.api_key = self.load_api_key()

    def load_api_key(self):
        # 1. 환경변수에서 먼저 읽기
        key = os.getenv("OPENROUTER_API_KEY")

        # 2. 환경변수에 없으면 openrouter_key.txt에서 읽기
        # 현재 실행 위치와 ai_helper.py가 있는 위치를 둘 다 확인합니다.
        if key is None or key.strip() == "":
            possible_paths = [
                "openrouter_key.txt",
                os.path.join(os.path.dirname(__file__), "openrouter_key.txt"),
            ]

            for path in possible_paths:
                try:
                    if os.path.exists(path):
                        with open(path, "r", encoding="utf-8-sig") as file:
                            key = file.read()
                        break
                except Exception:
                    key = None

        if key is None:
            return None

        # 3. 혹시 파일 안에 OPENROUTER_API_KEY=... 형식으로 넣었을 때 처리
        key = key.strip()

        if key.startswith("OPENROUTER_API_KEY="):
            key = key.replace("OPENROUTER_API_KEY=", "", 1).strip()

        # 4. 따옴표 제거
        if key.startswith('"') and key.endswith('"'):
            key = key[1:-1].strip()

        if key.startswith("'") and key.endswith("'"):
            key = key[1:-1].strip()

        # 5. 눈에 안 보이는 특수 공백 제거
        key = key.replace("\ufeff", "")
        key = key.replace("\u200b", "")
        key = key.replace("\u200c", "")
        key = key.replace("\u200d", "")
        key = key.replace("\n", "")
        key = key.replace("\r", "")
        key = key.strip()

        return key

    def check_ai_ready(self):
        if requests is None:
            print("[AI 오류] requests가 설치되어 있지 않습니다.")
            print("PowerShell에서 실행:")
            print("python -m pip install requests")
            return False

        if self.api_key is None or self.api_key == "":
            print("[AI 오류] API 키를 찾지 못했습니다.")
            print("openrouter_key.txt 파일에 API 키만 한 줄로 넣어주세요.")
            return False

        if not self.api_key.startswith("sk-or-"):
            print("[AI 경고] OpenRouter API 키는 보통 sk-or- 로 시작합니다.")
            print("[AI 경고] 현재 키가 OpenRouter 키가 아닐 가능성이 있습니다.")

        try:
            self.api_key.encode("latin-1")
        except Exception:
            print("[AI 오류] API 키에 한글 또는 특수문자가 들어가 있습니다.")
            print("openrouter_key.txt에는 실제 sk-or-... 키만 넣어야 합니다.")
            return False

        return True

    def ask_ai(self, prompt):
        """
        일반 AI 요청 함수입니다.

        작동 순서:
        1. nvidia/nemotron-3-super-120b-a12b:free 시도
        2. 실패하면 deepseek/deepseek-v4-flash:free 시도
        3. 실패하면 google/gemma-4-31b-it:free 시도

        성공하면 AI 응답 문자열을 반환하고,
        모든 모델이 실패하면 None을 반환합니다.
        """

        print("[AI 확인] ask_ai 함수 실행됨")

        if self.check_ai_ready() == False:
            return None

        print("[AI 확인] requests 있음")
        print("[AI 확인] API KEY 있음")
        print("[AI 확인] API KEY 앞부분:", self.api_key[:8])
        print("[AI 확인] API KEY 길이:", len(self.api_key))

        for model in self.models:
            print("[AI 시도] 사용 모델:", model)

            answer = self.ask_ai_with_model(prompt, model)

            if answer is not None:
                print("[AI 성공] 사용 모델:", model)
                self.model = model
                return answer

            print("[AI 실패] 다음 모델을 시도합니다.")

        print("[AI 최종 실패] 모든 예비 AI 모델이 실패했습니다.")
        return None

    def ask_ai_with_model(self, prompt, model):
        headers = {
            "Authorization": "Bearer " + self.api_key,
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "FridgeMate",
        }

        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "너는 냉장고 재료와 한국 요리 레시피를 도와주는 AI야.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.2,
        }

        try:
            response = requests.post(
                self.url,
                headers=headers,
                json=data,
                timeout=30,
            )

            print("[AI 응답 코드]", response.status_code)

            if response.status_code != 200:
                print("[AI 오류 내용]")
                print(response.text)
                return None

            result = response.json()

            if "choices" not in result or len(result["choices"]) == 0:
                print("[AI 오류] 응답에 choices가 없습니다.")
                print(result)
                return None

            try:
                content = result["choices"][0]["message"]["content"]

                if content is None or str(content).strip() == "":
                    print("[AI 오류] 응답 내용이 비어 있습니다.")
                    return None

                return content

            except Exception:
                print("[AI 오류] 응답에서 content를 읽지 못했습니다.")
                print(result)
                return None

        except Exception as e:
            print("[AI 예외 발생]")
            print(e)
            return None

    def extract_json_object(self, text):
        """
        AI가 ```json ... ``` 또는 설명을 같이 보내도 JSON 부분만 최대한 뽑습니다.
        """

        if text is None:
            return None

        text = str(text).strip()
        text = text.replace("```json", "")
        text = text.replace("```JSON", "")
        text = text.replace("```", "")
        text = text.strip()

        try:
            return json.loads(text)
        except Exception:
            pass

        match = re.search(r"\{.*\}", text, re.DOTALL)

        if match is None:
            return None

        try:
            return json.loads(match.group())
        except Exception:
            return None

    def convert_ingredient_unit(self, name, quantity, unit, expire_days):
        """
        재료명과 단위를 AI에게 표준 형태로 정규화하게 합니다.

        예:
        EGG 2 pcs -> 계란 2 개
        달걀 한 판 -> 계란 30 개
        파 1단 -> 대파 300 g
        milk 1 pack -> 우유 1000 ml

        반환값:
        [재료명, 수량, 단위, 유통기한]

        실패 시:
        None
        """

        print("[AI 정규화] 재료명/단위 AI 변환을 시도합니다.")

        if self.check_ai_ready() == False:
            return None

        prompt = """
냉장고 재료 입력을 레시피 계산용 표준 형태로 정규화해줘.
반드시 JSON 하나만 출력해.

입력:
재료명: """ + str(name) + """
수량: """ + str(quantity) + """
단위: """ + str(unit) + """
유통기한까지 남은 날짜: """ + str(expire_days) + """

규칙:
- 재료명은 한국어 레시피에서 쓰기 좋은 표준 이름으로 바꿔.
- 영어, 대문자, 오타, 동의어도 가능하면 한국어 표준 재료명으로 바꿔.
- 예: EGG, egg, eggs, 달걀, 삶은계란 -> 계란
- 예: 파, green onion, scallion -> 대파
- 예: milk -> 우유
- 예: tofu -> 두부
- 예: onion -> 양파
- 출력 단위는 가능하면 g, ml, 개, 장, 토막 중 하나로 바꿔.
- 한국 요리에서 흔히 쓰는 평균값으로 환산해.
- 확실히 모르는 경우에도 가장 흔한 조리 기준으로 추정해.
- 설명 문장 없이 JSON만 출력해.

예시:
{"name":"계란","quantity":2,"unit":"개","expire_days":5}
{"name":"계란","quantity":30,"unit":"개","expire_days":5}
{"name":"대파","quantity":300,"unit":"g","expire_days":5}
{"name":"식빵","quantity":20,"unit":"장","expire_days":7}
{"name":"우유","quantity":1000,"unit":"ml","expire_days":5}
{"name":"두부","quantity":300,"unit":"g","expire_days":3}

출력 형식:
{"name":"재료명","quantity":숫자,"unit":"단위","expire_days":숫자}
"""

        for model in self.models:
            print("[AI 정규화 시도] 사용 모델:", model)

            answer = self.ask_ai_with_model(prompt, model)
            data = self.extract_json_object(answer)

            if data is None:
                print("[AI 정규화 실패] JSON을 읽지 못했습니다.")
                print("[AI 정규화 실패] 다음 모델을 시도합니다.")
                continue

            try:
                converted_name = str(data["name"]).strip()
                converted_quantity = float(data["quantity"])
                converted_unit = str(data["unit"]).strip().lower()
                converted_expire_days = int(data["expire_days"])
            except Exception:
                print("[AI 정규화 실패] JSON 형식이 올바르지 않습니다.")
                print(data)
                print("[AI 정규화 실패] 다음 모델을 시도합니다.")
                continue

            if converted_name == "":
                print("[AI 정규화 실패] 변환된 재료명이 비어 있습니다.")
                print(data)
                print("[AI 정규화 실패] 다음 모델을 시도합니다.")
                continue

            if converted_unit == "":
                print("[AI 정규화 실패] 변환된 단위가 비어 있습니다.")
                print(data)
                print("[AI 정규화 실패] 다음 모델을 시도합니다.")
                continue

            if converted_quantity <= 0:
                print("[AI 정규화 실패] 변환된 수량이 0 이하입니다.")
                print(data)
                print("[AI 정규화 실패] 다음 모델을 시도합니다.")
                continue

            if converted_expire_days < 0:
                print("[AI 정규화 실패] 변환된 유통기한이 음수입니다.")
                print(data)
                print("[AI 정규화 실패] 다음 모델을 시도합니다.")
                continue

            print("[AI 정규화 성공] 사용 모델:", model)
            self.model = model

            return [
                converted_name,
                converted_quantity,
                converted_unit,
                converted_expire_days,
            ]

        print("[AI 정규화 최종 실패] 모든 예비 AI 모델이 실패했습니다.")
        return None

    def rerank_recipes(self, candidates, user_condition):
        recipe_text = ""

        for i in range(len(candidates)):
            result = candidates[i]

            recipe_text = recipe_text + str(i + 1) + ". " + result.recipe.name + "\n"
            recipe_text = recipe_text + "점수: " + str(round(result.score, 2)) + "\n"
            recipe_text = recipe_text + "조리시간: " + str(result.recipe.minutes) + "분\n"
            recipe_text = recipe_text + "부족한 재료: " + str(result.missing_ingredients) + "\n"
            recipe_text = recipe_text + "매운 정도: " + str(result.recipe.spicy_level) + "\n\n"

        prompt = """
사용자 조건을 보고 아래 추천 후보 중 TOP 5를 골라 순서대로 추천해줘.

사용자 조건:
""" + user_condition + """

추천 후보:
""" + recipe_text + """

조건:
- 후보 목록 안에서만 고르기
- 번호와 요리 이름을 함께 출력
- 간단한 추천 이유도 작성
"""

        return self.ask_ai(prompt)

    def suggest_substitutes(self, missing_ingredients):
        prompt = """
다음 부족한 재료를 대체할 수 있는 재료를 추천해줘.

부족한 재료:
""" + str(missing_ingredients) + """

조건:
- 한국 요리 기준
- 각 재료마다 대체재 2개 정도 추천
- 너무 길지 않게 설명
"""

        return self.ask_ai(prompt)

    def rewrite_instructions(self, recipe, fridge_names):
        prompt = """
다음 레시피를 사용자가 가진 재료 기준으로 다시 설명해줘.

요리 이름:
""" + recipe.name + """

원래 조리법:
""" + recipe.instructions + """

사용자가 가진 재료:
""" + str(fridge_names) + """

조건:
- 없는 재료는 대체 가능하면 대체해서 설명
- 초보자도 따라할 수 있게 단계별로 설명
- 너무 길지 않게 작성
"""

        return self.ask_ai(prompt)
