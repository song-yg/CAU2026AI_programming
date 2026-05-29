class Recipe:

    def __init__(self, recipe_id, name, category, minutes, difficulty,
                 spicy_level, servings, ingredients_list, 
                 essential_ingredients, used_ingredients, instructions):
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
        ingredients_text = data.get("ingredients_ko", "") #json파일에서 ingredients 한국어로 받아옴

        ingredients_list = [] #리스트에 따로 저장
        for item in ingredients_text:
            item = item.strip(",")
            if ingredients_text != "":
                ingredients_list.append(item)

        essential_text = data.get("essential_ingredients_ko", "") #json파일에서 essential ingredient 한국어로 받아옴

        essential_list = [] #리스트에 따로 저장
        for item in essential_text:
            item = item.strip(",")
            if essential_text != "":
                essential_list.append(item)

        used_list = []
        for item in data.get("used_ingredients",[]):
            name = item.get("name", "")
            amount = item.get("amount", 0)
            unit = item.get("unit", "")

            target_list = [name, amount, unit, 0] # 유닛메니저의 함수를 쓰기 위해서 타겟 만들기

            changed_target_list = UnitManager.unit_conversion(target_list) 

            used_list.append({"name" : changed_target_list[0],
                             "amount": changed_target_list[1],
                             "unit": changed_target_list[2]})
            
        return Recipe(
            data.get("recipe_id", ""),
            data.get("recipe_name_ko", ""),
            data.get("category", ""),
            data.get("mintues", 0),
            data.get("difficulty", ""),
            data.get("spicy_level_0_4", 0),
            data.get("servings", 1),
            ingredients_list,
            essential_list,
            used_list,
            data.get("instructions_ko", "")

        )
