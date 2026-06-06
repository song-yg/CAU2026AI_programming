 from models import Ingredient, UnitManager
from storage import load_json, save_json


class FridgeManager:

    def __init__(self, ai_helper = None, path = "data/fridge.json", recipe_path = "data/recipes.json"):
        self.ai_helper = ai_helper
        self.ingredients  = []
        self.path = path
        self.recipe_unit_index = {}
        self.recipe_unit_index = self.load_recipe_unit_index(path)
        self.recipe_path = recipe_path
        self.load()


    def load_recipe_unit_index(self, recipe_path):

        unit_manager = UnitManager()
        recipe_unit_index = {}
        data = load_json(recipe_path, [])

        for recipe in data:
            used_ingredients = recipe.get("ingredients", [])

            for item in used_ingredients:
               try:
                name = unit_manager.normalize_name(item.get("name", ""))
                unit = unit_manager.normalize_name(item.get("unit", ""))

                if name == "" or unit == "" :
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
            retrun self.recipe_unit_index[name]

        return []



    def is_recipe_compatible(self, name, unit):
        unit_manager = UnitManager()
        name = unit_manager.normalize_name(name)
        unit = unit_manager.normalize_unit_name(unit)

        if name == '물':
            return True

        if len(self.recipe_unit_index) == 0:
            return True

        recipe_units = self.get_recipe_units(name)

        if len(recipe_units) == 0:
            return False


        return unit in recipe_units


    def make_recipe_unit_context(self, name):
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

            if count >= 160:
                break

        return "\n".join(lines)

    
    def print_recipe_unit_error(self, name, unit):
        recipe_units = self.get.recipe_units(name)

        print("[추가 실패]")

        if len(recipe_units) == 0:
            print(name, "(은)는 현재 recipes.json의 레시피에서 사용되지 않습니다.")
            print("AI가 다른 표준 재료명으로 바꾸지 못하면 재료는 냉장고에 저장되지 않습니다.")
        else:
            print(name, "재료는 recipes.json에서 다음 단위로만 사용됩니다:", recipe_units)
            print("입력/변환된 단위",unit, "는 추천과 차감에 사용할 수 없어 저장하지 않습니다.")
        
        print("해결 방법: 레시피에 쓰이는 단위로 입력하거나, AI 정규화가 가능하도록 API 키를 확인하세요.")
        


    def load(self):
        data = load_json(self.path, [])
        self.ingredients = []
        unit_manager = UnitManager()

        for item in data:
            try:
                target = [item["name"], item["quantity"], item["unit"], item["expire_days"]]
                target = unit_manager.unit_conversion(target)
                ingredient = Ingredient(target[0], target[1], target[2], target[3])
                self.add_ingredient_object(ingredient)

            except Exception as e:
                print("냉장고 재료 하나를 불러오지 못헀습니다.")
                print(f"오류 내용: {e}")

        self.sort_ingredients()

    def save(self):
        self.sort_ingredients()
        data = []
        
        for item in self.ingredients:
            data.append(item.to_dict())

        save_json(self.path, data)


    def sort_ingredients(self):
            self.ingredients.sort(key=lambda x: (x.name, x.expire_days))



    def add_ingredient_object(self,new_ingredient):

        for ingredient in self.ingredients:
            if ingredient.name == new_ingredient.name and ingredient.unit == new_ingredient.unit
            and ingredient.expire_days == new_ingredient.expire_days
            :
                ingredient.quantity += new_ingredient.quantity
                return

        self.ingredients.append(new_ingredient)


    def get_batches(self, name):

        unit_manager = UnitManager()
        name = unti_manager.normalize_name(name)

        batches = []

        for ingredient in self.ingredients:
            if ingredient.name == name:
                batches.append(ingredient)

        batches.sort(key=lambda x: x.expire_days)
        return batches



    def find_ingredient(self, name):
        
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
            total += ingredient.quantity

        return total

    def get_earliest_expire_days(self, name):
        batches = self.get_batches(name)

        if len(batches) == 0:
            return None

        return batches[0].expire_days

    def has_name_with_different_unit(self, name, unit):
        batches = self.get_batches(name)
        unit_manager = UnitManager()
        name = unit_manager.normalize_name(name)
        unit = unit_manager.normalize_unit_name(unit)

        for ingredient in batches:
            if ingredient.unit != unit:
                return True

        return False


    def get_ai_helper(self):
        

        if self.ai_helper is not None:
            return self.ai_helper

        try:
            from ai_helper import AIHelper
            self.ai_helper = AIHelper()
            return self.ai_helper
        except Exception as e:
            print("[AIHelper를 불러오지 못했습니다.]")
            print(f"오류 내용: {e}")
            return None


    def get_usable_ai_helper(self):

        ai_helper = self.get_ai_helper()

        if ai_helper is None:
            return None

        if ai_helper.api_key() is None or str(ai_helper.api_key().strip()) == "":
            # print("[AIHelper의 API 키가 없습니다.]")
            return None

        return ai_helper


    def validate_converted_target(self, target):

        if target is None or len(target) < 4:
            return False

        name = str(target[0])
        quantity = float(target[1])
        unit = str(target[2])
        expire_days = int(target[3])

        if name == "":
            raise ValueError("재료명이 비어 있습니다")
        
        if unit == "":
            raise ValueError("단위가 비어 있습니다")

        if quantity <= 0:
            raise ValueError("수량은 1 이상이어야 합니다")

        if expire_days <= 0:
            raise ValueError("유통기한은 1 이상이어야 합니다")

        return [name, quantity, unit, expire_days]


    def call_ai_converter(self, ai, name, quantity, unit, expire_days, recipe_unit_context):
        
        try:
            return ai.convert_ingredient_unit(
                name,
                quantity,
                unit,
                expire_days,
                recipe_unit_context
            )
        except TypeError:
            return ai.convert_ingredient_unit(name, quantity, unit, expire_days)

    def convert_with_ai_if_needed(self, name, quantity, unit, expire_days):
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
            local_is_standard = not unit_manager.needs_ai(local_name, local_unit)
            local_is_recipe_compatible = local_is_standard and self.is_recipe_compatible(local_name, local_unit)

        except Exception as e:
            local_error = e

        if local_is_recipe_compatible:
            return local_target, False

        ai_helper = self.get_usable_ai_helper()

        if ai_helper is not None:
            context_name = name
            
            if local target is not None:
                context_name = local_target[0]

            recipe_unit_context = self.make_recipe_unit_context(context_name)
            ai_target = self.call_ai_converter(name, quantity, unit, expire_days, recipe_unit_context)

            if ai_target is not None:
                try:
                    ai_target = unit_manager.unit_conversion(ai_target)
                    ai_target = self.validate_converted_target(ai_target)
                 except Exception as e:
                        ai_target = None

            if ai_target is not None:

                ai_name = ai_target[0]
                ai_unit = ai_target[2]

                if unit_manager.needs_ai_conversion(ai_name, ai_unit):
                    pass
                elif self.is_recipe_compatible(ai_name, ai_unit):
                    return ai_target, True
                else:
                    self.print_recipe_unit_error(ai_name, ai_unit)
                    return None, False
                
           if local_is_recipe_compatible:
                return local_target, False

           if local_target is not None and local_is_standard:
                self.print_recipe_unit_error(local_target[0], local_target[2])
                return None, False

            print("Python 기본 기능으로는 recipes.json 기준 단위로 변환 할 수 없습니다.")
            print("[추가 실패]")
            print("레시피에 쓰이는 단위로 직접 입력해 주세요")
            return None, False

        if local_is_recipe_compatible:
            return local_target, False

        if local_target is not None and local_is_standard:
            self.print_recipe_unit_error(local_target[0], local_target[2])
            return None, False

        print("[추가 실패]")
        print("Python 기본 기능으로는 recipes.json 기준 단위로 변환 할 수 없습니다.")
        print("레시피에 쓰이는 단위로 직접 입력해 주세요.")
        return None, False

    if local_is_recipe_compatible:
        return local_target, False

    if local_error is not None:
            print("[추가 실패]")
            print("입력값을 숫자/단위로 해석하지 못했습니다.")
     elif local target is not None:
            if local_is_standard:
               self.print_recipe_unit_error[local_target[0], local_target[2]]
               return None, False
        
            print("[추가 실패]")
            print("Python 기본 기능으로 처리하기 어려운 입력입니다.")

        print("AI 호출에 실패했습니다. Python 기본 기능만 사용합니다.")
        print("레시피에 쓰이는 단위로 직접 입력해 주세요.")
        return None, False          
            
        
    def add_ingredient(self, name, quantity, unit, expire_days):

        try:
            before_quantity = float(quantity)
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

            changed = before_quantity != str(quantity) or before_unit != str(unit)

        except Exception as e:
            print("[추가 실패]")
            print("입력값이 올바르지 않습니다.")
            return

        if self.has_name_with_different_unit(name, unit):
            print("[추가 실패]")
            print(name, "(이)가 이미 다른 단위로 저장되어 있습니다.")
            print("같은 재료는 같은 단위로 저장해야 안전하게 계산할 수 있습니다.")
            return

        new_ingredient = Ingredient(name, quantity, unit, expire_days)
        self.add_ingredient_object(new_ingredient)
        self.save()

        if used_ai == True:
            print('AI가 recipe.json 기준으로 재료명/단위를 정규화하여 저장했습니다.')
        elif changed == True:
            print("단위가 변환되어 저장되었습니다.")

        print("저장 형태:", name, str(round(quantity,2)) + unit, "/", str(expire_days) + "일 남음")
        print("재료가 추가되었습니다.")

    def print_all(self):
        print("\n[냉장고 재료 목록]")

        if len(self.ingredients) == 0:
            print("등록된 재료가 없습니다.")
            return

        self.sort_ingredients()

        for i in range(len(self.ingredients)):
            ingredient = self.ingredients[i]u
            print(
                str(i+1) + "." +
                ingredient.name + "|" +
                str(round(ingredient.quantity,2))  + Ingredient.unit + "|" +
                str(ingredient.expire_days) + "일 남음"
            )
  

    def print_expiring_soon(self):
        print("\n[유통기한 임박 재료]")

        found = False
        self.sort_ingredients()

        for ingredient in self.ingredients:
            if ingredient.expire_days <= 3:
                print(
                    ingredient.name + "|" +
                    str(round(Ingredient.quantity, 2) + ingredient.unit + "|" +
                    str(ingredient.expire_days) + "일 남음")
                )
                found = True

            if found = False:
                print("유통기한이 임박한 재료가 없습니다.")



    def delete_ingredients(self, name):

        unit_manager = UnitManager()
        name = unit_manager.normalize_name(name)

        new_list = []
        deleted = False

        for ingredient in self.ingredients:
            if ingredient.name == name:
                deleted = True
            else:
                new_list.append(ingredient)

        self.ingredients == new_list

        if deleted = True:
            self.save()
            print("재료를 전부 삭제했습니다")
        else:
            print("해당 재료를 찾지 못했습니다.")


    def convert_discard_input(self, name, quantity, unit):
        
        result = convert_with_ai_if_needed(name, quantity, unit, 0)
        target = result[0]

        if target is None:
            return None

        return [target[0], target[1], target[2]]



    def discard_ingredient(self, name, quantity, unit):
        try:
            target = self.convert_discard_input(name, quantity, unit)

            if target is None:
                return False

            name = target[0]
            quantity = target[1]
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
            print("해당 재료가 존재하지 않습니다.")
            return False

        total = self.get_total_quantityi(name, unit)


        if total == 0:
            print("[삭제 실패]")
            print(name, "(은)는 있지만 단위가 일치하지 않습니다.")
            print("입력 단위:",  unit)
            print("저장된 단위:", batches[0].unit)
            return False

        if total < quantity:
            print("[삭제 실패]")
            print("버리려는 수량이 현재 재고보다 많습니다.")
            print("버리려는 수량:", round(quantity,2), unit)
            print("현재 총 수량:", unit)
            print("냉장고 재고는 변경되지 않았습니다.")
            return False

        print("\n[재료 일부 삭제]")




        






