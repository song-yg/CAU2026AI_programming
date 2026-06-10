class UnitManager:
    def __init__(self):
        pass

    NAME_MAPPING = {
        "달걀": "계란",
        "달걀후라이": "계란",
        "달걀프라이": "계란",
        "삶은계란": "계란",
        "삶은 달걀": "계란",
        "에그": "계란",
        "egg": "계란",
        "eggs": "계란",
        "파": "대파",
        "쪽파": "대파",
        "green onion": "대파",
        "scallion": "대파",
        "scallions": "대파",
        "milk": "우유",
        "tofu": "두부",
        "onion": "양파",
        "ramen": "라면",
        "instant ramen": "라면",
        "oreo": "오레오",
        "ekfrif": "계란",
        "rpfks": "계란",
        "dndb": "우유",
        "fk면": "라면",
        "asparagus": "아스파라거스",
        "broccoli": "브로콜리",
        "tomato": "토마토",
        "potato": "감자",
        "sweet potato": "고구마",
        "eggplant": "가지",
        "zucchini": "애호박",
        "cabbage": "양배추",
        "mushroom": "버섯",
        "bell pepper": "파프리카",
        "carrot": "당근",
        "cucumber": "오이",
        "spinach": "시금치",
        "lettuce": "상추",
        "perilla leaf": "깻잎",
        "chicken": "닭고기",
        "pork": "돼지고기",
        "beef": "소고기",
        "lamb": "양고기",
        "shrimp": "새우",
        "squid": "오징어",
        "salmon": "연어",
        "tuna": "참치",
        "cheese": "치즈",
        "bread": "식빵",
        "pasta": "파스타면",
        "spaghetti": "스파게티면",
        "rice noodle": "쌀국수면",
        "quinoa": "퀴노아",
        "chickpea": "병아리콩",
        "lentil": "렌틸콩",
        "avocado": "아보카도",
        "basil": "바질",
        "cilantro": "고수",
    }

    # 레시피 계산에 바로 쓰기 좋은 기준 단위
    # g/ml/개는 대부분의 재료에서 쓰고,
    # 장/토막은 recipes.json에 실제로 들어있는 단위라 유지한다.
    STANDARD_UNITS = ["g", "ml", "개", "장", "토막"]

    UNIT1_MAPPING = {
        "그램": "g",
        "gram": "g",
        "g": "g",

        "킬로그램": "kg",
        "kilogram": "kg",
        "kilo": "kg",
        "kg": "kg",

        "밀리리터": "ml",
        "milliliter": "ml",
        "ml": "ml",
        "cc": "ml",
        "씨씨": "ml",

        "리터": "l",
        "liter": "l",
        "l": "l",

        "알": "개",
        "pcs": "개",
        "piece": "개",
        "개": "개",

        "큰스푼": "큰술",
        "스푼": "큰술",
        "tbsp": "큰술",
        "큰술": "큰술",

        "티스푼": "작은술",
        "tsp": "작은술",
        "작은술": "작은술",

        "그릇": "공기",
        "공기": "공기",

        "cup": "컵",
        "c": "컵",
        "컵": "컵",

        "온즈": "oz",
        "온스": "oz",
        "oz": "oz",

        "pint": "pt",
        "파인트": "pt",
        "pt": "pt",

        "quart": "qt",
        "쿼트": "qt",
        "qt": "qt",

        "통": "통",
        "모": "모",
        "대": "대",
        "쪽": "쪽",
        "단": "단",
        "판": "판",
        "봉": "봉",
        "봉지": "봉",
        "pack": "팩",
        "package": "팩",
        "bag": "봉",
        "팩": "팩",
        "묶음": "묶음",
        "줌": "줌",
        "주먹": "줌",
        "장": "장",
        "토막": "토막",
        "마리": "마리",
        "캔": "캔",
        "병": "병",
    }

    UNIT2_MAPPING = {
        "kg": 1000,
        "컵": 200,
        "oz": 30,
        "pt": 473,
        "qt": 946,
        "l": 1000,
    }

    UNIT3_MAPPING = {
        "kg": "g",
        "컵": "ml",
        "oz": "ml",
        "pt": "ml",
        "qt": "ml",
        "l": "ml",
    }

    INGREDIENT_MAPPING = {
        ("김치", "통"): (500, "g"),
        ("두부", "모"): (300, "g"),
        ("밥", "공기"): (210, "g"),
        ("양파", "개"): (150, "g"),
        ("무", "개"): (800, "g"),
        ("오이", "개"): (100, "g"),
        ("토마토", "개"): (200, "g"),
        ("감자", "개"): (150, "g"),
        ("고구마", "개"): (150, "g"),
        ("대파", "대"): (80, "g"),
        ("대파", "단"): (300, "g"),
        ("마늘", "쪽"): (5, "g"),
        ("간장", "큰술"): (15, "ml"),
        ("식용유", "큰술"): (15, "ml"),
        ("올리브유", "큰술"): (15, "ml"),
        ("참기름", "큰술"): (15, "ml"),
        ("식초", "큰술"): (15, "ml"),
        ("계란", "판"): (30, "개"),
        ("참치캔", "캔"): (1, "개"),
        ("라면", "봉"): (1, "개"),
        ("짜장라면", "봉"): (1, "개"),
        ("오레오", "g"): (0.1, "개"),
        ("라면", "팩"): (1, "개"),
        ("우동면", "봉"): (1, "개"),
        ("소면", "봉"): (500, "g"),
        ("파스타면", "봉"): (500, "g"),
        ("스파게티면", "봉"): (500, "g"),
        ("쌀국수면", "봉"): (300, "g"),
        ("메밀면", "봉"): (300, "g"),
        ("떡볶이떡", "봉"): (500, "g"),
        ("떡국떡", "봉"): (500, "g"),
        ("아스파라거스", "대"): (20, "g"),
        ("브로콜리", "개"): (300, "g"),
        ("양배추", "개"): (800, "g"),
        ("파프리카", "개"): (150, "g"),
        ("피망", "개"): (100, "g"),
        ("가지", "개"): (150, "g"),
        ("애호박", "개"): (250, "g"),
        ("단호박", "개"): (800, "g"),
        ("레몬", "개"): (1, "개"),
        ("라임", "개"): (1, "개"),
        ("아보카도", "개"): (1, "개"),
        ("바나나", "개"): (1, "개"),
        ("사과", "개"): (1, "개"),
        ("배", "개"): (1, "개"),
        ("망고", "개"): (1, "개"),
        ("식빵", "봉"): (20, "장"),
        ("또띠아", "팩"): (8, "장"),
        ("치즈", "장"): (1, "장"),
        ("오레오", "봉"): (10, "개"),
    }

    KEYBOARD_TO_KOREAN = {
        "q": "ㅂ", "Q": "ㅃ", "w": "ㅈ", "W": "ㅉ", "e": "ㄷ", "E": "ㄸ",
        "r": "ㄱ", "R": "ㄲ", "t": "ㅅ", "T": "ㅆ", "y": "ㅛ", "u": "ㅕ",
        "i": "ㅑ", "o": "ㅐ", "O": "ㅒ", "p": "ㅔ", "P": "ㅖ", "a": "ㅁ",
        "s": "ㄴ", "d": "ㅇ", "f": "ㄹ", "g": "ㅎ", "h": "ㅗ", "j": "ㅓ",
        "k": "ㅏ", "l": "ㅣ", "z": "ㅋ", "x": "ㅌ", "c": "ㅊ", "v": "ㅍ",
        "b": "ㅠ", "n": "ㅜ", "m": "ㅡ",
        "A": "ㅁ", "S": "ㄴ", "D": "ㅇ", "F": "ㄹ", "G": "ㅎ", "H": "ㅗ",
        "J": "ㅓ", "K": "ㅏ", "L": "ㅣ", "Z": "ㅋ", "X": "ㅌ", "C": "ㅊ",
        "V": "ㅍ", "B": "ㅠ", "N": "ㅜ", "M": "ㅡ", "Y": "ㅛ", "U": "ㅕ", "I": "ㅑ",
    }

    CHOSEONG = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
    JUNGSEONG = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"]
    JONGSEONG = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
    VOWEL_COMBINE = {
        ("ㅗ", "ㅏ"): "ㅘ", ("ㅗ", "ㅐ"): "ㅙ", ("ㅗ", "ㅣ"): "ㅚ",
        ("ㅜ", "ㅓ"): "ㅝ", ("ㅜ", "ㅔ"): "ㅞ", ("ㅜ", "ㅣ"): "ㅟ",
        ("ㅡ", "ㅣ"): "ㅢ",
    }
    FINAL_COMBINE = {
        ("ㄱ", "ㅅ"): "ㄳ", ("ㄴ", "ㅈ"): "ㄵ", ("ㄴ", "ㅎ"): "ㄶ",
        ("ㄹ", "ㄱ"): "ㄺ", ("ㄹ", "ㅁ"): "ㄻ", ("ㄹ", "ㅂ"): "ㄼ",
        ("ㄹ", "ㅅ"): "ㄽ", ("ㄹ", "ㅌ"): "ㄾ", ("ㄹ", "ㅍ"): "ㄿ",
        ("ㄹ", "ㅎ"): "ㅀ", ("ㅂ", "ㅅ"): "ㅄ",
    }

    def compose_syllable(self, cho, jung, jong=""):
        if cho not in self.CHOSEONG or jung not in self.JUNGSEONG or jong not in self.JONGSEONG:
            return cho + jung + jong
        code = 0xAC00 + (self.CHOSEONG.index(cho) * 21 + self.JUNGSEONG.index(jung)) * 28 + self.JONGSEONG.index(jong)
        return chr(code)

    def english_keyboard_to_korean(self, text):
        """
        한/영키를 잘못 눌러 영어처럼 입력된 값을 한글 자판 기준으로 복원한다.
        예: ekfrif -> 달걀, rPfkS -> 계란, fk면 -> 라면
        """
        raw = str(text).strip()
        if raw == "":
            return raw

        jamos = []
        for ch in raw:
            if ch in self.KEYBOARD_TO_KOREAN:
                jamos.append(self.KEYBOARD_TO_KOREAN[ch])
            else:
                jamos.append(ch)

        result = ""
        i = 0
        while i < len(jamos):
            current = jamos[i]

            if current in self.CHOSEONG and i + 1 < len(jamos) and jamos[i + 1] in self.JUNGSEONG:
                cho = current
                jung = jamos[i + 1]
                i = i + 2

                if i < len(jamos) and (jung, jamos[i]) in self.VOWEL_COMBINE:
                    jung = self.VOWEL_COMBINE[(jung, jamos[i])]
                    i = i + 1

                jong = ""
                if i < len(jamos) and jamos[i] in self.CHOSEONG:
                    # 다음 자음 뒤에 모음이 오면 그 자음은 다음 글자의 초성이므로 받침으로 쓰지 않는다.
                    if i + 1 < len(jamos) and jamos[i + 1] in self.JUNGSEONG:
                        jong = ""
                    else:
                        if i + 1 < len(jamos) and (jamos[i], jamos[i + 1]) in self.FINAL_COMBINE:
                            if i + 2 < len(jamos) and jamos[i + 2] in self.JUNGSEONG:
                                jong = jamos[i]
                                i = i + 1
                            else:
                                jong = self.FINAL_COMBINE[(jamos[i], jamos[i + 1])]
                                i = i + 2
                        else:
                            jong = jamos[i]
                            i = i + 1

                result = result + self.compose_syllable(cho, jung, jong)
            else:
                result = result + current
                i = i + 1

        return result

    def normalize_name(self, name):
        name = str(name).strip()
        key = name.lower()

        if key in self.NAME_MAPPING:
            return self.NAME_MAPPING[key]

        if name in self.NAME_MAPPING:
            return self.NAME_MAPPING[name]

        # 한/영키를 잘못 누른 입력을 먼저 복원해 본다.
        # 예: ekfrif -> 달걀 -> 계란, fk면 -> 라면
        keyboard_fixed = self.english_keyboard_to_korean(name)

        if keyboard_fixed != name:
            fixed_key = keyboard_fixed.lower()

            if fixed_key in self.NAME_MAPPING:
                return self.NAME_MAPPING[fixed_key]

            if keyboard_fixed in self.NAME_MAPPING:
                return self.NAME_MAPPING[keyboard_fixed]

            # 변환 결과가 한글 식재료명처럼 보이면 그 값을 사용한다.
            # 최종 저장 가능 여부는 FridgeManager가 recipes.json 기준으로 다시 검사한다.
            return keyboard_fixed

        return name

    def normalize_unit_name(self, unit):
        unit = str(unit).strip().lower()

        if unit in self.UNIT1_MAPPING:
            return self.UNIT1_MAPPING[unit]

        return unit

    def is_standard_unit(self, unit):
        unit = self.normalize_unit_name(unit)
        return unit in self.STANDARD_UNITS

    def needs_ai_conversion(self, name, unit):
        """
        로컬 규칙으로 변환한 뒤에도 표준 단위가 아니면 AI 변환이 필요하다.
        예: 1봉, 1팩, 1묶음, 한 줌처럼 계산용 단위가 아닌 경우.
        """

        unit = self.normalize_unit_name(unit)

        if unit in self.STANDARD_UNITS:
            return False

        return True

    def unit_conversion(self, target):
        """
        target = [재료명, 수량, 단위, 유통기한]
        로컬 규칙으로 변환 가능한 단위만 변환한다.
        로컬 규칙으로 모르는 단위는 그대로 돌려주고,
        FridgeManager에서 필요하면 AI 변환을 시도한다.
        """

        if target is None or len(target) < 4:
            raise ValueError("target은 [재료명, 수량, 단위, 유통기한] 형식이어야 합니다.")

        name = self.normalize_name(target[0])
        quantity = float(target[1])
        unit = self.normalize_unit_name(target[2])
        expire_days = target[3]

        key = (name, unit)

        if key in self.INGREDIENT_MAPPING:
            ratio = self.INGREDIENT_MAPPING[key][0]
            new_unit = self.INGREDIENT_MAPPING[key][1]

            return [name, quantity * ratio, new_unit, expire_days]

        if unit in self.UNIT2_MAPPING:
            return [name, quantity * self.UNIT2_MAPPING[unit], self.UNIT3_MAPPING[unit], expire_days]

        return [name, quantity, unit, expire_days]


class Ingredient:
    """냉장고에 저장될 재료 객체"""

    def __init__(self, name, quantity, unit, expire_days):
        self.name = str(name).strip()
        self.quantity = float(quantity)
        self.unit = str(unit).strip()
        self.expire_days = int(expire_days)

        if self.name == "":
            raise ValueError("재료명이 비어 있습니다.")

        if self.unit == "":
            raise ValueError("단위가 비어 있습니다.")

        if self.quantity <= 0:
            raise ValueError("수량은 0보다 커야 합니다.")

        if self.expire_days < 0:
            raise ValueError("유통기한은 0일 이상이어야 합니다.")

    def to_dict(self):
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "expire_days": self.expire_days,
        }

    @staticmethod
    def from_dict(data):
        return Ingredient(
            data["name"],
            data["quantity"],
            data["unit"],
            data["expire_days"],
        )


class Recipe:
    """레시피 정보를 담는 객체"""

    def __init__(
        self,
        recipe_id,
        name,
        category,
        minutes,
        difficulty,
        spicy_level,
        servings,
        ingredients_list,
        essential_ingredients,
        used_ingredients,
        instructions,
    ):
        self.recipe_id = recipe_id
        self.name = name
        self.category = category
        self.minutes = int(minutes)
        self.difficulty = difficulty
        self.spicy_level = int(spicy_level)
        self.servings = int(servings)
        self.ingredients_list = ingredients_list
        self.essential_ingredients = essential_ingredients
        self.used_ingredients = used_ingredients
        self.instructions = instructions

    @staticmethod
    def from_dict(data):
        unit_manager = UnitManager()

        ingredients_text = data.get("ingredients_ko", "")
        ingredients_list = []

        for item in ingredients_text.split(","):
            item = unit_manager.normalize_name(item)
            if item != "":
                ingredients_list.append(item)

        essential_text = data.get("essential_ingredients_ko", "")
        essential_ingredients = []

        for item in essential_text.split(","):
            item = unit_manager.normalize_name(item)
            if item != "":
                essential_ingredients.append(item)

        used_ingredients = []

        for item in data.get("used_ingredients", []):
            name = str(item.get("name", "")).strip()
            amount = item.get("amount", 0)
            unit = item.get("unit", "")

            target = [name, amount, unit, 0]

            try:
                target = unit_manager.unit_conversion(target)
                name = target[0]
                amount = target[1]
                unit = target[2]
            except Exception:
                name = unit_manager.normalize_name(name)
                amount = float(amount)

            used_ingredients.append({
                "name": name,
                "amount": amount,
                "unit": unit,
            })

        return Recipe(
            data.get("recipe_id", ""),
            data.get("recipe_name_ko", ""),
            data.get("category", ""),
            data.get("minutes", 0),
            data.get("difficulty", ""),
            data.get("spicy_level_0_4", 0),
            data.get("servings", 1),
            ingredients_list,
            essential_ingredients,
            used_ingredients,
            data.get("instructions_ko", ""),
        )
