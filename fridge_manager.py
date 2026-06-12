from models import Ingredient, UnitManager
from storage import load_json, save_json


class FridgeManager:
    def __init__(self, path="data/fridge.json", ai_helper=None, recipe_path="data/recipes.json"):
        self.path = path
        self.recipe_path = recipe_path
        self.ai_helper = ai_helper
        self.recipe_unit_index = self.load_recipe_unit_index(recipe_path)
        self.ingredients = []
        self.load()

    def load_recipe_unit_index(self, recipe_path):
        """
        recipes.json에 실제로 쓰이는 재료명과 단위를 미리 모아둔다.
        예: 라면 -> 개, 대파 -> g, 우유 -> ml
        이 목록을 기준으로 냉장고에 저장되는 단위가 추천/차감에 쓸 수 있는지 검사한다.
        """

        unit_manager = UnitManager()
        recipe_unit_index = {}
        data = load_json(recipe_path, [])

        for recipe in data:
            used_ingredients = recipe.get("used_ingredients", [])

            for item in used_ingredients:
                try:
                    name = unit_manager.normalize_name(item.get("name", ""))
                    unit = unit_manager.normalize_unit_name(item.get("unit", ""))

                    if name == "" or unit == "":
                        continue

                    if name not in recipe_unit_index:
                        recipe_unit_index[name] = []

                    if unit not in recipe_unit_index[name]:
                        recipe_unit_index[name].append(unit)

                except Exception:
                    pass

        return recipe_unit_index

    def get_recipe_units(self, name):
        unit_manager = UnitManager()
        name = unit_manager.normalize_name(name)

        if name in self.recipe_unit_index:
            return self.recipe_unit_index[name]

        return []

    def is_recipe_compatible(self, name, unit):
        """
        냉장고 저장 형태가 recipes.json에서 실제로 쓰일 수 있는지 확인한다.
        예: 라면 1개 -> 가능, 라면 1봉지 그대로 저장 -> 불가능
        """

        unit_manager = UnitManager()
        name = unit_manager.normalize_name(name)
        unit = unit_manager.normalize_unit_name(unit)

        if name == "물":
            return True

        # recipe_unit_index가 비어 있으면 recipes.json을 못 읽은 상황이므로
        # 프로그램 전체가 막히지 않게 일단 허용한다.
        if len(self.recipe_unit_index) == 0:
            return True

        recipe_units = self.get_recipe_units(name)

        if len(recipe_units) == 0:
            return False

        return unit in recipe_units

    def make_recipe_unit_context(self, name):
        """
        AI에게 넘겨줄 recipes.json 기준 단위 정보를 만든다.
        전체 레시피를 보내지 않고, 재료명/단위 목록만 보내서 토큰을 줄인다.
        """

        unit_manager = UnitManager()
        name = unit_manager.normalize_name(name)
        recipe_units = self.get_recipe_units(name)

        if len(recipe_units) > 0:
            return name + ": " + ", ".join(recipe_units)

        lines = []
        count = 0

        for recipe_name in sorted(self.recipe_unit_index.keys()):
            units = self.recipe_unit_index[recipe_name]
            lines.append(recipe_name + ": " + ", ".join(units))
            count = count + 1

            if count >= 350:
                break

        return "\n".join(lines)

    def print_recipe_unit_error(self, name, unit, fail_title="[추가 실패]"):
        recipe_units = self.get_recipe_units(name)

        print(fail_title)

        if len(recipe_units) == 0:
            print(name, "재료는 현재 recipes.json의 레시피에서 사용되지 않습니다.")
            print("AI가 다른 표준 재료명으로 바꾸지 못하면 냉장고에 저장하지 않습니다.")
        else:
            print(name, "재료는 recipes.json에서 다음 단위로만 사용됩니다:", recipe_units)
            print("입력/변환된 단위", unit, "는 추천과 차감에 사용할 수 없어 저장하지 않습니다.")

        print("해결 방법: 레시피에 쓰이는 단위로 입력하거나, AI 정규화가 가능하도록 API 키를 확인하세요.")

    def simple_key(self, text):
        """
        재료명 비교를 위해 공백과 대소문자 차이를 줄인다.
        예: ' Green Onion ' -> 'greenonion'
        """

        return str(text).strip().lower().replace(" ", "")

    def edit_distance(self, a, b):
        """
        아주 간단한 편집 거리 계산 함수.
        AI가 바꾼 재료명이 원래 입력과 너무 다르면 거부하기 위해 사용한다.
        """

        a = self.simple_key(a)
        b = self.simple_key(b)

        dp = []

        for i in range(len(a) + 1):
            row = []

            for j in range(len(b) + 1):
                if i == 0:
                    row.append(j)
                elif j == 0:
                    row.append(i)
                else:
                    row.append(0)

            dp.append(row)

        for i in range(1, len(a) + 1):
            for j in range(1, len(b) + 1):
                cost = 0

                if a[i - 1] != b[j - 1]:
                    cost = 1

                dp[i][j] = min(
                    dp[i - 1][j] + 1,
                    dp[i][j - 1] + 1,
                    dp[i - 1][j - 1] + cost,
                )

        return dp[len(a)][len(b)]

    def similarity(self, a, b):
        """
        문자열이 어느 정도 비슷한지 0~1 사이 값으로 계산한다.
        영어 오타 eggg -> egg 같은 경우를 허용하기 위한 보조 함수이다.
        """

        try:
            from difflib import SequenceMatcher
            return SequenceMatcher(None, self.simple_key(a), self.simple_key(b)).ratio()
        except Exception:
            return 0

    def get_aliases_for_name(self, canonical_name):
        """
        UnitManager.NAME_MAPPING에서 특정 표준 재료명으로 이어지는 별칭들을 모은다.
        예: 계란 -> egg, eggs, 달걀, 삶은계란
        """

        unit_manager = UnitManager()
        aliases = [canonical_name]

        for alias in unit_manager.NAME_MAPPING:
            try:
                if unit_manager.normalize_name(alias) == canonical_name:
                    aliases.append(alias)
            except Exception:
                pass

        return aliases

    def is_close_to_alias(self, original_name, canonical_name):
        """
        원래 입력이 AI가 반환한 재료명 또는 그 별칭과 충분히 가까운지 검사한다.
        이 검사를 통과하지 못하면 AI가 억지로 다른 재료로 바꾼 것으로 보고 거부한다.
        """

        original_key = self.simple_key(original_name)

        if original_key == "":
            return False

        aliases = self.get_aliases_for_name(canonical_name)

        for alias in aliases:
            alias_key = self.simple_key(alias)

            if alias_key == "":
                continue

            if original_key == alias_key:
                return True

            if len(original_key) >= 2 and (original_key in alias_key or alias_key in original_key):
                return True

            # 짧은 한글 오타: 걔란 -> 계란 같은 1글자 차이는 허용
            if min(len(original_key), len(alias_key)) >= 2 and self.edit_distance(original_key, alias_key) <= 1:
                return True

            # 긴 영어 오타: eggg -> egg, scallionn -> scallion 같은 경우 허용
            if max(len(original_key), len(alias_key)) >= 4 and self.similarity(original_key, alias_key) >= 0.75:
                return True

        return False

    def is_safe_ai_name_change(self, original_name, ai_name):
        """
        AI가 입력 재료명을 완전히 다른 재료로 바꿔버리는 것을 막는다.
        예: ekfrif -> 양파, 피카츄 -> 새우, 젠슨황 -> 밥 같은 변환은 거부한다.
        """

        unit_manager = UnitManager()
        original_normalized = unit_manager.normalize_name(original_name)
        ai_normalized = unit_manager.normalize_name(ai_name)

        if ai_normalized == "":
            return False

        # recipes.json에 없는 재료로 바꾸는 것은 저장 가치가 없으므로 거부한다.
        if len(self.recipe_unit_index) > 0 and ai_normalized != "물" and ai_normalized not in self.recipe_unit_index:
            return False

        # 로컬 정규화만으로 같은 이름이면 안전하다.
        if original_normalized == ai_normalized:
            return True

        # 사용자가 이미 recipes.json에 있는 재료명을 입력했는데 AI가 다른 재료로 바꾸면 위험하다.
        if original_normalized in self.recipe_unit_index and original_normalized != ai_normalized:
            return False

        # 원래 입력이 AI 결과의 별칭/오타로 볼 수 있을 정도로 가까운 경우만 허용한다.
        if self.is_close_to_alias(original_name, ai_normalized):
            return True

        return False

    def load(self):
        data = load_json(self.path, [])
        self.ingredients = []
        unit_manager = UnitManager()

        for item in data:
            try:
                target = [
                    item["name"],
                    item["quantity"],
                    item["unit"],
                    item["expire_days"],
                ]
                # 저장된 파일을 불러올 때는 AI를 호출하지 않는다.
                # 프로그램 시작할 때마다 네트워크 요청이 생기면 느리고 불안정해지기 때문이다.
                target = unit_manager.unit_conversion(target)

                ingredient = Ingredient(
                    target[0],
                    target[1],
                    target[2],
                    target[3],
                )

                self.add_ingredient_object(ingredient)

            except Exception as e:
                print("냉장고 재료 하나를 불러오지 못했습니다.")
                print("오류 내용:", e)

        self.sort_ingredients()

    def save(self):
        self.sort_ingredients()

        data = []

        for ingredient in self.ingredients:
            data.append(ingredient.to_dict())

        save_json(self.path, data)

    def sort_ingredients(self):
        self.ingredients.sort(key=lambda x: (x.name, x.expire_days))

    def add_ingredient_object(self, new_ingredient):
        """
        같은 재료라도 유통기한이 다르면 다른 묶음으로 보관한다.
        이름 + 단위 + 유통기한이 모두 같을 때만 수량을 합친다.
        """

        for ingredient in self.ingredients:
            same_name = ingredient.name == new_ingredient.name
            same_unit = ingredient.unit == new_ingredient.unit
            same_expire = ingredient.expire_days == new_ingredient.expire_days

            if same_name and same_unit and same_expire:
                ingredient.quantity = ingredient.quantity + new_ingredient.quantity
                return

        self.ingredients.append(new_ingredient)

    def get_batches(self, name):
        unit_manager = UnitManager()
        name = unit_manager.normalize_name(name)

        batches = []

        for ingredient in self.ingredients:
            if ingredient.name == name:
                batches.append(ingredient)

        batches.sort(key=lambda x: x.expire_days)
        return batches

    def find_ingredient(self, name):
        """
        기존 코드와 호환하려고 남겨둔 함수.
        같은 재료가 여러 묶음이면 유통기한이 가장 짧은 묶음을 돌려준다.
        """

        batches = self.get_batches(name)

        if len(batches) == 0:
            return None

        return batches[0]

    def get_total_quantity(self, name, unit):
        unit_manager = UnitManager()
        name = unit_manager.normalize_name(name)
        unit = unit_manager.normalize_unit_name(unit)

        total = 0
        batches = self.get_batches(name)

        for ingredient in batches:
            if ingredient.unit == unit:
                total = total + ingredient.quantity

        return total

    def get_earliest_expire_days(self, name):
        batches = self.get_batches(name)

        if len(batches) == 0:
            return None

        return batches[0].expire_days

    def has_name_with_different_unit(self, name, unit):
        unit_manager = UnitManager()
        name = unit_manager.normalize_name(name)
        unit = unit_manager.normalize_unit_name(unit)
        batches = self.get_batches(name)

        for ingredient in batches:
            if ingredient.unit != unit:
                return True

        return False

    def get_ai_helper(self):
        """
        main.py에서 AIHelper를 넘겨주지 않은 경우에도 메뉴 1번에서 필요하면 생성한다.
        """

        if self.ai_helper is not None:
            return self.ai_helper

        try:
            from ai_helper import AIHelper
            self.ai_helper = AIHelper()
            return self.ai_helper
        except Exception:
            print("AI 호출에 실패했습니다. Python 기본 기능만 사용합니다.")
            return None

    def get_usable_ai_helper(self):
        """
        API 키가 준비된 경우에만 AIHelper를 돌려준다.
        API 키가 없으면 일반적인 g/ml/개 입력은 로컬 규칙만으로 저장한다.
        """

        ai = self.get_ai_helper()

        if ai is None:
            return None

        if ai.api_key is None or str(ai.api_key).strip() == "":
            return None

        return ai

    def validate_converted_target(self, target):
        """
        로컬 변환 또는 AI 변환 결과가 실제 저장 가능한 값인지 검사한다.
        잘못된 AI 응답이나 이상한 사용자 입력이 냉장고 파일에 저장되는 것을 막는다.
        """

        if target is None or len(target) < 4:
            return None

        name = str(target[0]).strip()
        quantity = float(target[1])
        unit = str(target[2]).strip()
        expire_days = int(target[3])

        if name == "":
            raise ValueError("재료명이 비어 있습니다.")

        if unit == "":
            raise ValueError("단위가 비어 있습니다.")

        if quantity <= 0:
            raise ValueError("수량은 0보다 커야 합니다.")

        if quantity > 1000000:
            raise ValueError("수량이 비정상적으로 큽니다.")

        if expire_days < 0:
            raise ValueError("유통기한은 0일 이상이어야 합니다.")

        if expire_days > 3650:
            raise ValueError("유통기한이 비정상적으로 깁니다.")

        return [name, quantity, unit, expire_days]

    def call_ai_converter(self, ai, name, quantity, unit, expire_days, recipe_unit_context):
        """
        새 버전 AIHelper는 recipe_unit_context를 받을 수 있다.
        혹시 예전 FakeAI나 예전 AIHelper를 테스트에 쓰더라도 깨지지 않게 TypeError를 처리한다.
        """

        try:
            return ai.convert_ingredient_unit(
                name,
                quantity,
                unit,
                expire_days,
                recipe_unit_context,
            )
        except TypeError:
            return ai.convert_ingredient_unit(name, quantity, unit, expire_days)

    def convert_with_ai_if_needed(self, name, quantity, unit, expire_days, fail_title="[추가 실패]"):
        unit_manager = UnitManager()

        original_target = [name, quantity, unit, expire_days]
        local_target = None
        local_is_standard = False
        local_is_recipe_compatible = False
        local_error = None

        try:
            local_target = unit_manager.unit_conversion(original_target)
            local_target = self.validate_converted_target(local_target)
            local_name = local_target[0]
            local_unit = local_target[2]
            local_is_standard = not unit_manager.needs_ai_conversion(local_name, local_unit)
            local_is_recipe_compatible = local_is_standard and self.is_recipe_compatible(local_name, local_unit)
        except Exception as e:
            local_error = e

        # 로컬 규칙만으로 레시피 단위까지 맞으면 AI를 부르지 않고 바로 저장한다.
        # 예: 라면 1봉지 -> 라면 1개, 파 1단 -> 대파 300g
        if local_is_recipe_compatible:
            return local_target, False

        ai = self.get_usable_ai_helper()

        if ai is not None:
            context_name = name

            if local_target is not None:
                context_name = local_target[0]

            recipe_unit_context = self.make_recipe_unit_context(context_name)
            ai_target = self.call_ai_converter(ai, name, quantity, unit, expire_days, recipe_unit_context)

            if ai_target is not None:
                try:
                    ai_target = unit_manager.unit_conversion(ai_target)
                    ai_target = self.validate_converted_target(ai_target)
                except Exception:
                    ai_target = None

            if ai_target is not None:
                ai_name = ai_target[0]
                ai_unit = ai_target[2]

                if self.is_safe_ai_name_change(name, ai_name) == False:
                    print(fail_title)
                    print("입력한 재료를 recipes.json 기준 식재료로 안전하게 판단하지 못했습니다.")
                    print("재료명을 더 정확하게 입력해 주세요.")
                    return None, False

                if unit_manager.needs_ai_conversion(ai_name, ai_unit):
                    pass
                elif self.is_recipe_compatible(ai_name, ai_unit):
                    return ai_target, True
                else:
                    self.print_recipe_unit_error(ai_name, ai_unit, fail_title)
                    return None, False

            # AI가 실패했어도 로컬 규칙으로 recipes.json 단위까지 맞으면 저장한다.
            if local_is_recipe_compatible:
                return local_target, False

            if local_target is not None and local_is_standard:
                self.print_recipe_unit_error(local_target[0], local_target[2], fail_title)
                return None, False

            print(fail_title)
            print("Python 기본 기능으로는 recipes.json 기준 단위로 변환할 수 없습니다.")
            print("레시피에 쓰이는 단위로 직접 입력해 주세요.")
            return None, False

        # API 키가 없어도 로컬 규칙으로 recipes.json 단위까지 맞는 입력은 저장한다.
        if local_is_recipe_compatible:
            return local_target, False

        if local_error is not None:
            print(fail_title)
            print("입력값을 숫자/단위로 해석하지 못했습니다.")
            return None, False

        if local_target is not None:
            if local_is_standard:
                self.print_recipe_unit_error(local_target[0], local_target[2], fail_title)
                return None, False

            print(fail_title)
            print("Python 기본 기능으로 처리하기 어려운 입력입니다.")

        print("AI 호출에 실패했습니다. Python 기본 기능만 사용합니다.")
        print("레시피에 쓰이는 단위로 직접 입력해 주세요.")
        return None, False

    def add_ingredient(self, name, quantity, unit, expire_days):
        try:
            before_quantity = str(quantity).strip()
            before_unit = str(unit).strip()

            result = self.convert_with_ai_if_needed(name, quantity, unit, expire_days)
            target = result[0]
            used_ai = result[1]

            if target is None:
                return

            name = target[0]
            quantity = target[1]
            unit = target[2]
            expire_days = int(target[3])

            changed = before_quantity != str(quantity) or before_unit != unit

        except Exception:
            print("[추가 실패]")
            print("입력값이 올바르지 않습니다.")
            return

        if self.has_name_with_different_unit(name, unit):
            print("[추가 실패]")
            print(name, "재료가 이미 다른 단위로 저장되어 있습니다.")
            print("같은 재료는 같은 단위로 저장해야 안전하게 계산할 수 있습니다.")
            return

        new_ingredient = Ingredient(name, quantity, unit, expire_days)
        self.add_ingredient_object(new_ingredient)
        self.save()

        if used_ai == True:
            print("AI가 recipes.json 기준으로 재료명/단위를 정규화하여 저장했습니다.")
        elif changed == True:
            print("단위가 변환되어 저장되었습니다.")

        print("저장 형태:", name, str(round(quantity, 2)) + unit, "/", str(expire_days) + "일 남음")
        print("재료가 추가되었습니다.")

    def print_all(self):
        print("\n[냉장고 재료 목록]")

        if len(self.ingredients) == 0:
            print("등록된 재료가 없습니다.")
            return

        self.sort_ingredients()

        for i in range(len(self.ingredients)):
            ingredient = self.ingredients[i]

            print(
                str(i + 1) + ". " +
                ingredient.name + " | " +
                str(round(ingredient.quantity, 2)) + ingredient.unit + " | " +
                str(ingredient.expire_days) + "일 남음"
            )

    def print_expiring_soon(self):
        print("\n[유통기한 임박 재료]")

        found = False
        self.sort_ingredients()

        for ingredient in self.ingredients:
            if ingredient.expire_days <= 3:
                print(
                    ingredient.name + " | " +
                    str(round(ingredient.quantity, 2)) + ingredient.unit + " | " +
                    str(ingredient.expire_days) + "일 남음"
                )
                found = True

        if found == False:
            print("유통기한이 임박한 재료가 없습니다.")

    def delete_ingredient(self, name):
        """
        해당 재료의 모든 유통기한 묶음을 삭제한다.
        9번 메뉴에서 수량을 비워두면 이 함수가 실행된다.
        """

        unit_manager = UnitManager()
        name = unit_manager.normalize_name(name)

        new_list = []
        deleted = False

        for ingredient in self.ingredients:
            if ingredient.name == name:
                deleted = True
            else:
                new_list.append(ingredient)

        self.ingredients = new_list

        if deleted == True:
            self.save()
            print(name, "재료를 전부 삭제했습니다.")
        else:
            print("해당 재료를 찾지 못했습니다.")

    def convert_discard_input(self, name, quantity, unit):
        """
        버릴 재료 입력을 저장 단위와 같은 형태로 바꾼다.
        예: 달걀 1판 -> 계란 30개, 파 1단 -> 대파 300g
        AI가 준비되어 있으면 애매한 입력도 AI 정규화를 시도한다.
        """

        result = self.convert_with_ai_if_needed(name, quantity, unit, 0, "[삭제 실패]")
        target = result[0]

        if target is None:
            return None

        return [target[0], target[1], target[2]]

    def discard_ingredient(self, name, quantity, unit):
        """
        재료를 원하는 수량만 버린다.
        같은 재료가 여러 유통기한 묶음으로 나뉘어 있으면 유통기한이 짧은 것부터 버린다.
        재고가 부족하면 아예 차감하지 않는다.
        """

        try:
            target = self.convert_discard_input(name, quantity, unit)

            if target is None:
                return False

            name = target[0]
            quantity = float(target[1])
            unit = target[2]

            if quantity <= 0:
                print("[삭제 실패]")
                print("버릴 수량은 0보다 커야 합니다.")
                return False

        except Exception as e:
            print("[삭제 실패]")
            print("입력값이 올바르지 않습니다.")
            print("오류 내용:", e)
            return False

        batches = self.get_batches(name)

        if len(batches) == 0:
            print("[삭제 실패]")
            print("해당 재료를 찾지 못했습니다.")
            return False

        total = self.get_total_quantity(name, unit)

        if total == 0:
            print("[삭제 실패]")
            print(name, "재료는 있지만 단위가 일치하지 않습니다.")
            print("입력 단위:", unit)
            print("저장된 단위:", batches[0].unit)
            return False

        if total < quantity:
            print("[삭제 실패]")
            print("버리려는 수량이 현재 재고보다 많습니다.")
            print("버리려는 수량:", round(quantity, 2), unit)
            print("현재 총수량:", round(total, 2), unit)
            print("냉장고 재고는 변경되지 않았습니다.")
            return False

        print("\n[재료 일부 삭제]")
        self.consume_one_ingredient(name, quantity, unit)

        new_list = []

        for ingredient in self.ingredients:
            if ingredient.quantity > 0:
                new_list.append(ingredient)

        self.ingredients = new_list
        self.save()

        print("선택한 수량만 삭제했습니다.")
        return True

    def check_available_for_recipe(self, recipe):
        """
        레시피에 필요한 재료가 충분한지 먼저 검사한다.
        여러 유통기한 묶음이 있으면 같은 단위끼리 수량을 합산해서 판단한다.
        """

        if len(recipe.used_ingredients) == 0:
            print("[재료 차감 실패]")
            print("이 레시피에는 차감용 재료 정보가 없습니다.")
            return False

        always_available = ["물"]
        unit_manager = UnitManager()

        for used in recipe.used_ingredients:
            name = unit_manager.normalize_name(used["name"])
            amount = used["amount"]
            unit = unit_manager.normalize_unit_name(used["unit"])

            if name in always_available:
                continue

            batches = self.get_batches(name)

            if len(batches) == 0:
                print("[재료 차감 실패]")
                print(name, "재료가 냉장고에 없습니다.")
                print("냉장고 재고는 변경되지 않았습니다.")
                return False

            total = self.get_total_quantity(name, unit)

            if total == 0:
                print("[재료 차감 실패]")
                print(name, "의 단위가 일치하지 않습니다.")
                print("레시피 필요 단위:", unit)
                print("냉장고 저장 단위:", batches[0].unit)
                print("냉장고 재고는 변경되지 않았습니다.")
                return False

            if total < amount:
                print("[재료 차감 실패]")
                print(name, "수량이 부족합니다.")
                print("필요 수량:", amount, unit)
                print("현재 총수량:", round(total, 2), unit)
                print("냉장고 재고는 변경되지 않았습니다.")
                return False

        return True

    def consume_one_ingredient(self, name, amount, unit):
        """
        한 재료를 유통기한이 짧은 묶음부터 차감한다.
        예: 계란 2일 남은 것부터 쓰고, 부족하면 5일 남은 것을 이어서 쓴다.
        """

        unit_manager = UnitManager()
        name = unit_manager.normalize_name(name)
        unit = unit_manager.normalize_unit_name(unit)
        batches = self.get_batches(name)
        remaining = amount

        for ingredient in batches:
            if ingredient.unit != unit:
                continue

            if remaining <= 0:
                break

            before = ingredient.quantity

            if ingredient.quantity >= remaining:
                ingredient.quantity = ingredient.quantity - remaining
                used_amount = remaining
                remaining = 0
            else:
                used_amount = ingredient.quantity
                remaining = remaining - ingredient.quantity
                ingredient.quantity = 0

            after = ingredient.quantity

            print(
                name + "(" + str(ingredient.expire_days) + "일 남음): " +
                str(round(before, 2)) + unit +
                " -> " +
                str(round(after, 2)) + unit +
                "  / 사용 " + str(round(used_amount, 2)) + unit
            )

    def consume_ingredients(self, recipe):
        if self.check_available_for_recipe(recipe) == False:
            return False

        print("\n[" + recipe.name + " 재료 차감]")

        always_available = ["물"]
        unit_manager = UnitManager()

        for used in recipe.used_ingredients:
            name = unit_manager.normalize_name(used["name"])
            amount = used["amount"]
            unit = unit_manager.normalize_unit_name(used["unit"])

            if name in always_available:
                continue

            self.consume_one_ingredient(name, amount, unit)

        new_list = []

        for ingredient in self.ingredients:
            if ingredient.quantity > 0:
                new_list.append(ingredient)

        self.ingredients = new_list
        self.save()

        print("요리에 사용된 재료가 냉장고에서 차감되었습니다.")
        return True
