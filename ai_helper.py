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
        # 1번 모델이 실패하면 2번, 2번이 실패하면 3번, 3번이 실패하면 4번 모델을 자동으로 시도합니다.
        self.models = [
            "google/gemini-pro-latest",
            "openai/gpt-5.2-pro",
            "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
            "deepseek/deepseek-chat-v3-0324:free",
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

    def print_ai_failure_message(self):
        """
        사용자에게 보여줄 AI 실패 메시지는 이 한 줄로 통일한다.
        HTTP 응답 원문, API 오류 JSON, 예외 내용은 출력하지 않는다.
        """

        print("AI 호출에 실패했습니다. Python 기본 기능만 사용합니다.")

    def check_ai_ready(self, show_message=True):
        if requests is None:
            if show_message:
                self.print_ai_failure_message()
            return False

        if self.api_key is None or self.api_key == "":
            if show_message:
                self.print_ai_failure_message()
            return False

        if not self.api_key.startswith("sk-or-"):
            if show_message:
                self.print_ai_failure_message()
            return False

        try:
            self.api_key.encode("latin-1")
        except Exception:
            if show_message:
                self.print_ai_failure_message()
            return False

        return True

    def ask_ai(self, prompt):
        """
        일반 AI 요청 함수입니다.

        작동 순서:
        1. google/gemini-pro-latest 시도
        2. 실패하면 openai/gpt-5.2-pro 시도
        3. 실패하면 nvidia/llama-3.1-nemotron-ultra-253b-v1:free 시도
        4. 실패하면 deepseek/deepseek-chat-v3-0324:free 시도

        성공하면 AI 응답 문자열을 반환하고,
        모든 모델이 실패하면 None을 반환합니다.
        """

        if self.check_ai_ready(show_message=True) == False:
            return None

        for model in self.models:
            answer = self.ask_ai_with_model(prompt, model)

            if answer is not None:
                self.model = model
                return answer

        self.print_ai_failure_message()
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

            if response.status_code != 200:
                return None

            result = response.json()

            if "choices" not in result or len(result["choices"]) == 0:
                return None

            try:
                content = result["choices"][0]["message"]["content"]

                if content is None or str(content).strip() == "":
                    return None

                return content

            except Exception:
                return None

        except Exception:
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

    def convert_ingredient_unit(self, name, quantity, unit, expire_days, recipe_unit_context=""):
        """
        재료명과 단위를 AI에게 표준 형태로 정규화하게 합니다.

        중요한 원칙:
        - AI가 모르는 재료를 억지로 다른 음식으로 바꾸면 안 됩니다.
        - 식재료가 아니거나 recipes.json 후보와 관계가 없으면 success=false를 반환하게 합니다.

        반환값:
        [재료명, 수량, 단위, 유통기한]

        실패 시:
        None
        """

        if self.check_ai_ready(show_message=True) == False:
            return None

        prompt = """
냉장고 재료 입력을 recipes.json에서 실제로 사용할 수 있는 표준 형태로 정규화해줘.
반드시 JSON 하나만 출력해.

입력:
재료명: """ + str(name) + """
수량: """ + str(quantity) + """
단위: """ + str(unit) + """
유통기한까지 남은 날짜: """ + str(expire_days) + """

recipes.json에서 실제로 쓰이는 재료명과 단위 후보:
""" + str(recipe_unit_context) + """

가장 중요한 규칙:
- 입력 재료가 식재료가 아니면 절대 다른 재료로 바꾸지 말고 success=false를 출력해.
- 입력 재료가 후보 목록의 재료와 의미상 명확히 같거나, 아주 가까운 오타/영어명/동의어일 때만 success=true를 출력해.
- ekfrif, 피카츄, 젠슨황처럼 식재료가 아니거나 의미를 알 수 없는 입력은 success=false로 처리해.
- 후보 목록에 없는 재료를 억지로 후보 목록의 다른 재료로 바꾸지 말고 success=false로 처리해.
- 모르는 재료를 억지로 가장 비슷한 음식으로 추정하지 마.
- 반드시 위 recipes.json 후보에 있는 재료명과 단위 조합에 맞춰서 변환해.
- 사용자가 입력한 단위가 틀린 표기는 아니더라도 recipes.json에서 쓰이지 않는 단위면 recipes.json 단위로 바꿔.
- 영어, 대문자, 명확한 오타, 동의어는 한국어 표준 재료명으로 바꿔.
- 예: EGG, egg, eggs, 달걀, 삶은계란 -> 계란
- 예: 파, green onion, scallion -> 대파
- 예: milk -> 우유
- 예: tofu -> 두부
- 예: asparagus -> 아스파라거스, broccoli -> 브로콜리
- 출력 단위는 recipes.json 후보에 맞춰 g, ml, 개, 장, 토막 중 하나로 바꿔.
- 설명 문장 없이 JSON만 출력해.

성공 예시:
{"success":true,"name":"계란","quantity":2,"unit":"개","expire_days":5}
{"success":true,"name":"대파","quantity":300,"unit":"g","expire_days":5}
{"success":true,"name":"우유","quantity":1000,"unit":"ml","expire_days":5}
{"success":true,"name":"라면","quantity":1,"unit":"개","expire_days":5}

실패 예시:
{"success":false,"reason":"식재료가 아니거나 recipes.json 후보와 관련 없는 입력"}

출력 형식:
성공하면 {"success":true,"name":"재료명","quantity":숫자,"unit":"단위","expire_days":숫자}
실패하면 {"success":false,"reason":"간단한 이유"}
"""

        for model in self.models:
            answer = self.ask_ai_with_model(prompt, model)
            data = self.extract_json_object(answer)

            if data is None:
                continue

            try:
                if "success" in data and data["success"] == False:
                    continue

                converted_name = str(data["name"]).strip()
                converted_quantity = float(data["quantity"])
                converted_unit = str(data["unit"]).strip().lower()
                converted_expire_days = int(data["expire_days"])
            except Exception:
                continue

            if converted_name == "":
                continue

            if converted_unit == "":
                continue

            if converted_quantity <= 0:
                continue

            if converted_expire_days < 0:
                continue

            self.model = model

            return [
                converted_name,
                converted_quantity,
                converted_unit,
                converted_expire_days,
            ]

        self.print_ai_failure_message()
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
