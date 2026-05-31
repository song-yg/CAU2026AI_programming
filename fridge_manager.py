from models import Ingredient, UnitManager
from storage import load_json, save_json


class FridgeManager:

    def __init__(self, ai_helper, path = "data/fridge.json"):
        self.ai_helper = ai_helper
        self.ingredients  = []
        self.path = path
        self.load()

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

    def save(self):
        data = []
        
        for item in self.ingredients:
            data.append(item.to_dict())

        save_json(self.path, data)


    def sort_ingredients(self):
            self.ingredients.sort(key=lambda x: (x.name, x.expire_days))



    def add_ingredient_object(self,new_ingredient):

        '''
        이름, 단위에 유통기한까지 같은 경우에만 추가한다
        '''

        for ingredient in self.ingredients:
            if ingredient.name == new_ingredient.name and ingredient.unit == new_ingredient.unit
            and ingredient.expire_days == new_ingredient.expire_days
            :
                ingredient.quantity += new_ingredient.quantity
                return

        self.ingredients.append(new_ingredient)


    def get_batches(self, name):
        '''
        같은 재료들을 임박한 순서대로
        '''

        unit_manager = UnitManager()
        name = unti_manager.normalize_name(name)

        batches = []

        for ingredient in self.ingredients:
            if ingredient.name == name:
                batches.append(ingredient)

        batches.sort(key=lambda x: x.expire_days)
        return batches



    def find_ingredient(self, name):
        '''
        이름이 같은 재료 중에서 유통기한이 가장 임박한 재료를 반환한다
        '''
        
        batches = self.get_batches(name)

        if len(batches) == 0:
            return None
        
        return batches[0]


    def get_total_quantity(self, name, unit):
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

        for ingredient in batches:
            if ingredient.unit != unit:
                return True

        return False


    def get_ai_helper(self):
        '''
        main에서 메뉴 1번을 선택했을 시 자체적으로 Aihelper를 사용한다
        '''

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
        '''
        API 가 있는 경우 aihelper를 반환하며
        없는 경우에는 로컬 규칙으로 단위를 정한다
        '''

        ai_helper = self.get_ai_helper()

        if ai_helper is None:
            return None

        if ai_helper.api_key() is None or str(ai_helper.api_key().strip()) == "":
            # print("[AIHelper의 API 키가 없습니다.]")
            return None

        return ai_helper


    def validate_converted_target(self, target):

        if target is None or len(target) != 4:
            return False

        name = target[0]
        quantity = target[1]
        unit = target[2]
        expire_days = target[3]

        if name == "":
            raise ValueError("재료명이 비어 있습니다")
        
        if unit == "":
            raise ValueError("단위가 비어 있습니다")

        if quantity <= 0:
            raise ValueError("수량은 1 이상이어야 합니다")

        if expire_days <= 0:
            raise ValueError("유통기한은 1 이상이어야 합니다")

        return [name, quantity, unit, expire_days]


    def convert_with_ai_if_needed(self, name, quantity, unit, expire_days):
        unit_manager = UnitManager()

        original_target = [name, quantity, unit, expire_days]
        local_target = None
        local_is_standard = False
        local_error = None

        try:
            local_target = unit_manager.unit_conversion(original_target)
            local_target = self.validate_converted_target(local_target)
            local_name = local_target[0]
            local_unit = local_target[2]
            local_is_standard = not unit_manager.needs_ai(local_name, local_unit)
        except Exception as e:
            local_error = e
        
        ai_helper = self.get_usable_ai_helper()

        '''
        ai를 통한 교차 검증!!
        '''

        if ai_helper is not None:
            print("[AI 재료명/단위 정규화 시도]")
            ai_target = ai_convert_ingredient_unit(name, quantity, unit, expire_days)

            if ai_target is not None:
                try:
                    ai_target = unit_manager.unit_conversion(ai_target)
                    ai_target = self.validate_converted_target(ai_target)
                 except Exception as e:
                        print("[AI 정규화 실패] AI 결과값이 저장 가능한 형태가 아닙니다.")
                        print(f"오류 내용: {e}")
                        ai_target = None

                ai_name = ai_target[0]
                ai_unit = ai_target[2]

                if not unit_manager.needs_ai_conversion(ai_name, ai_unit):
                    return ai_target, True
                
                print(f'[AI 정규화 실패] AI 결과값이 표준 단위가 아닙니다. : {ai_unit}')

                '''
                AI가 실패해도 로컬 정규화가 성공할 수도 있다
                '''

            if local_is_standard:
                    print("[로컬 정규화 성공] AI는 실패했지만 로컬 규칙으로 정규화에 성공했습니다.")
                    return local_target, False

            print("[추가 실패]")
            print('AI와 로컬 정규화 모두 실패했습니다.')
            print('해결 방법: g, ml, 개처럼 표준 단위를 사용하여 재료를 추가하거나 openrouter_key.txt를 확인하세요.')
            return None, False

        if local_is_standard:
            return local_target, False
        
        print("[추가 실패]")

        if local_error is not None:
            print('입력값을 숫자/단위로 해석하지 못했습니다.')
        elif local_target is not None:
            print('로컬 정규화로 처리하기 어려운 입력입니다.', local_target[0], local_target[1], local_target[2])

        print('이 경우에는 AI 정규화가 필요합니다. openrouter_key.txt 또는 OPENROUTER_API_KEY를 설정해 주세요.')
        return None, False          0.
            
        
    def add_ingredient(self, name, quantity, unit, expire_days):
        unit_manager = UnitManager()

        try:
            target = [name, quantity, unit, expire_days]

            before_quantity = float(quantity)
            before_unit = str(unit).strip()

            target = unit_manager.unit_conversion(target)

            name = target[0]
            quantity = target[1]
            unit = target[2]
            expire_days = int(target[3])

        except:
            print("[추가 실패]")
            print("수량 또는 유통기한이 올바르지 않습니다.")





        






