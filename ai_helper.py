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

        # AI 모델 호출 순서
        # 앞 모델이 실패하면 다음 모델을 자동으로 시도합니다.
        # 마지막 openrouter/free는 OpenRouter가 사용 가능한 무료 모델로 자동 연결해주는 예비 모델입니다.
        self.models = [
            "deepseek/deepseek-chat-v3-0324",
            "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
            "deepseek/deepseek-r1:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "openrouter/free",
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

    def get_ai_ready_problem(self):
        """
        AI를 사용할 수 없는 이유를 사용자 친화적인 문장으로 반환합니다.
        문제가 없으면 None을 반환합니다.
        """

        if requests is None:
            return "AI 기능 사용에 필요한 프로그램 구성 요소가 없어 기본 기능으로 진행합니다."

        if self.api_key is None or self.api_key == "":
            return "AI 키가 없어 AI 기능 없이 기본 기능으로 진행합니다."

        if not self.api_key.startswith("sk-or-"):
            return "AI 키 형식이 올바르지 않아 AI 기능 없이 기본 기능으로 진행합니다."

        try:
            self.api_key.encode("latin-1")
        except Exception:
            return "AI 키에 인식할 수 없는 문자가 포함되어 있어 기본 기능으로 진행합니다."

        return None

    def check_ai_ready(self):
        problem = self.get_ai_ready_problem()

        if problem is None:
            return True

        return False

    def print_ai_failure_message(self):
        """
        AI 호출이 실패했을 때 사용자에게 보여줄 메시지입니다.
        API 오류 코드, 모델명, 긴 에러 원문은 보여주지 않습니다.
        """

        print("AI 추천 기능을 잠시 사용할 수 없어 기본 추천 방식으로 진행합니다.")

    def print_ai_ready_problem(self):
        problem = self.get_ai_ready_problem()

        if problem is not None:
            print(problem)

    def ask_ai(self, prompt):
        """
        일반 AI 요청 함수입니다.

        작동 방식:
        1. self.models에 있는 모델을 순서대로 시도합니다.
        2. 한 모델이 실패하면 다음 모델로 넘어갑니다.
        3. 모든 모델이 실패하면 None을 반환합니다.
        4. 실패 이유 JSON이나 긴 에러 로그는 출력하지 않습니다.
        """

        if self.check_ai_ready() == False:
            self.print_ai_ready_problem()
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

            if "choices" not in result:
                return None

            if len(result["choices"]) == 0:
                return None

            message = result["choices"][0].get("message", {})
            content = message.get("content", None)

            if content is None:
                return None

            content = str(content).strip()

            if content == "":
                return None

            return content

        except Exception:
            return None

    def extract_json_object(self, text):
        """
        AI가 ```json ... ``` 또는 설명 문장을 같이 보내도
        JSON 부분만 최대한 뽑아냅니다.
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

    def make_recipe_context_text(self, recipe_context=None, allowed_names=None, allowed_units=None):
        """
        fridge_manager.py 쪽에서 recipes.json 기준 재료명/단위 정보를 넘겨주는 경우,
        AI 프롬프트에 참고 정보로 넣기 위한 문자열을 만듭니다.
        """

        context_text = ""

        if recipe_context is not None:
            context_text = context_text + "\n[레시피 기준 참고 정보]\n"
            context_text = context_text + str(recipe_context) + "\n"

        if allowed_names is not None:
            try:
                names = list(allowed_names)
                names = names[:200]
                context_text = context_text + "\n[허용 가능한 재료명 일부]\n"
                context_text = context_text + ", ".join(map(str, names)) + "\n"
            except Exception:
                pass

        if allowed_units is not None:
            try:
                units = list(allowed_units)
                context_text = context_text + "\n[허용 가능한 단위]\n"
                context_text = context_text + ", ".join(map(str, units)) + "\n"
            except Exception:
                pass

        return context_text

    def convert_ingredient_unit(
        self,
        name,
        quantity,
        unit,
        expire_days,
        recipe_context=None,
        allowed_names=None,
        allowed_units=None,
    ):
        """
        재료명과 단위를 AI에게 표준 형태로 정규화하게 합니다.

        예:
        EGG 2 pcs -> 계란 2 개
        달걀 한 판 -> 계란 30 개
        파 1단 -> 대파 300 g
        milk 1 pack -> 우유 1000 ml

        실패 시 None을 반환합니다.
        """

        if self.check_ai_ready() == False:
            return None

        context_text = self.make_recipe_context_text(
            recipe_context=recipe_context,
            allowed_names=allowed_names,
            allowed_units=allowed_units,
        )

        prompt = """
냉장고 재료 입력을 레시피 계산용 표준 형태로 정규화해줘.
반드시 JSON 하나만 출력해.

입력:
재료명: """ + str(name) + """
수량: """ + str(quantity) + """
단위: """ + str(unit) + """
유통기한까지 남은 날짜: """ + str(expire_days) + """

중요 규칙:
- 입력이 실제 식재료라고 판단될 때만 success를 true로 해.
- 식재료가 아닌 단어, 사람 이름, 캐릭터 이름, 의미 없는 문자열은 절대 억지로 식재료로 바꾸지 마.
- 모르면 추측해서 다른 재료로 바꾸지 말고 success=false를 반환해.
- 예: 피카츄, 젠슨황, ekfrif처럼 식재료로 확정할 수 없는 입력은 success=false.
- 단, 한/영키 오입력이나 아주 가까운 오타는 보정 가능해.
- 예: EGG, egg, eggs, 달걀, 걔란, eggg -> 계란
- 예: 파, green onion, scallion -> 대파
- 예: milk -> 우유
- 예: tofu -> 두부
- 예: onion -> 양파
- 출력 단위는 가능하면 g, ml, 개, 장, 토막 중 하나로 바꿔.
- 레시피 기준 단위와 맞출 수 있으면 그 단위로 바꿔.
- 설명 문장 없이 JSON만 출력해.

성공 예시:
{"success":true,"name":"계란","quantity":2,"unit":"개","expire_days":5}
{"success":true,"name":"대파","quantity":300,"unit":"g","expire_days":5}
{"success":true,"name":"우유","quantity":1000,"unit":"ml","expire_days":5}

실패 예시:
{"success":false,"reason":"식재료로 판단할 수 없음"}
{"success":false,"reason":"단위를 안전하게 변환할 수 없음"}

""" + context_text + """

출력 형식:
{"success":true,"name":"재료명","quantity":숫자,"unit":"단위","expire_days":숫자}
또는
{"success":false,"reason":"실패 이유"}
"""

        for model in self.models:
            answer = self.ask_ai_with_model(prompt, model)
            data = self.extract_json_object(answer)

            if data is None:
                continue

            try:
                success = data.get("success", True)
            except Exception:
                success = True

            if success == False:
                continue

            try:
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

            default_allowed_units = [
                "g",
                "kg",
                "ml",
                "l",
                "개",
                "장",
                "토막",
                "큰술",
                "작은술",
            ]

            if allowed_units is not None:
                try:
                    allowed_unit_list = list(allowed_units)
                except Exception:
                    allowed_unit_list = default_allowed_units
            else:
                allowed_unit_list = default_allowed_units

            if converted_unit not in allowed_unit_list:
                continue

            if allowed_names is not None:
                try:
                    allowed_name_list = list(allowed_names)

                    if converted_name not in allowed_name_list:
                        continue

                except Exception:
                    pass

            self.model = model

            return [
                converted_name,
                converted_quantity,
                converted_unit,
                converted_expire_days,
            ]

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
        recipe_name = getattr(recipe, "name", "레시피")
        recipe_instructions = getattr(recipe, "instructions", None)

        if recipe_instructions is None:
            recipe_instructions = getattr(recipe, "instructions_ko", "")

        prompt = """
다음 레시피를 사용자가 가진 재료 기준으로 다시 설명해줘.

요리 이름:
""" + str(recipe_name) + """

원래 조리법:
""" + str(recipe_instructions) + """

사용자가 가진 재료:
""" + str(fridge_names) + """

조건:
- 없는 재료는 대체 가능하면 대체해서 설명
- 초보자도 따라할 수 있게 단계별로 설명
- 너무 길지 않게 작성
"""

        return self.ask_ai(prompt)
