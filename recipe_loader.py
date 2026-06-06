from storage import load_json
from models import Recipe

def load_recipes(path="data/recipes.json"):
    data = load_json(path, [])
    recipes = []

    for item in data:
        try:
            recipe = Recipe.from_dict(item)
            recipes.append(recipe)
        except Exception as e:
            print("레시피 하나를 불러오지 못했습니다.")
            print("오류 내용:", e)

    return recipes
