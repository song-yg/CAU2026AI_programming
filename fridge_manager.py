from models import Ingredient, UnitManager
from storage import load_json, save_json


class FridgeManager:

    def __init__(self, path = "data/fridge.json"):
        self.ingredients  = []
        self.path = path
        self.load()

    def load(self):
        data = load_json(self.path, [])
        self.ingredients = []

        for item in data:
            try:
                self.ingredient = Ingredient.from_dict(item)
                self.ingredients.append(self.ingredient)
            except:
                print("냉장고 재료 하나를 불러오지 못헀습니다.")

    def save(self):
        data = []
        
        for item in self.ingredients:
            data.append(item.to_dict())

        save_json(self.path, data)


    def find_ingredient(self, name):
        name = name.strip()

        for ingredient in self.ingredients:
            if name == ingredient.name:
                return ingredient
            else:
                return None
            
    
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





        







