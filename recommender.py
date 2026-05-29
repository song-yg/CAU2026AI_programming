class RecommendationResult:
    def __init__(self, recipe, score, match_rate, missing_ingredients, urgent_ingredients):
        self.recipe = recipe
        self.score = score
        self.match_rate = match_rate
        self.missing_ingredients = missing_ingredients
        self.urgent_ingredients = urgent_ingredients
    
    #fridge_manager에서 재료 이름 목록을 가져오는 함수
    def get_fridge_names(self, fridge_manager):
        names = []

        #fridge_manager의 재료 목록에서 이름을 추출하여 names 리스트에 추가
        for ingredient in fridge_manager.ingredients:
            names.append(ingredient.name)
        return names
    
    #fridge_manager에서 특정 이름의 재료를 찾는 함수
    def find_fridge_item(self, fridge_manager, name):
        for ingredient in fridge_manager.ingredients:
            if ingredient.name == name:
                return ingredient
        return None
    
    #일치하는 재료의 비율을 계산하는 함수
    def calculate_match_rate(self, recipe, fridge_manager):
        fridge_names = self.get_fridge_names(fridge_manager)

        #재료가 없는 경우 0%로 처리
        total = len(recipe.ingredients_list)
        if total <= 0: 
            return 0
        
        #레시피와 일치하는 재료의 수를 계산하여 일치율을 반환
        matched = 0
        for name in recipe.ingredients_list:
            if name in fridge_names:
                matched = matched + 1
        return matched / total * 100 if total > 0 else 0
    
    #부족한 재료 목록을 반환하는 함수. 
    def find_missing_ingredients(self, recipe, fridge_manager):
        fridge_names = self.get_fridge_names(fridge_manager)
        missing = []
        for name in recipe.ingredients_list:
            if name not in fridge_names:
                missing.append(name)
        return missing
    
    #유통기한이 임박한 재료 목록과 긴급도를 계산하는 함수
    def calculate_expire_urgency(self, recipe, fridge_manager):
        urgency = 0
        urgent_ingredients = []
        for name in recipe.ingredients_list:
            item = self.find_fridge_item(fridge_manager, name)
            #레시피 재료 중 냉장고에 있는 재료의 유통기한을 고려하여 긴급도를 계산.
            if item is not None: #레시피에 존재하지 않는 재료는 유통기한이 반영되지 않는건가???
                urgency = urgency + 1 / (item.expire_days + 1)
                if item.expire_days <= 3:
                    urgent_ingredients.append(name)
        return urgency, urgent_ingredients
    
    #최종 점수를 계산하는 함수
    def calculate_score(self, recipe, fridge_manager):
        match_rate = self.calculate_match_rate(recipe, fridge_manager)
        missing = self.find_missing_ingredients(recipe, fridge_manager)
        urgency, urgent_ingredients = self.calculate_expire_urgency(recipe, fridge_manager)

        score = match_rate + 20 * urgency - 5 * len(missing) - 0.3 * recipe.minutes

        return RecommendationResult(
            recipe,
            score,
            match_rate,
            missing,
            urgent_ingredients
        )

    #점수 계산 후 상위 top_n개의 추천 결과를 반환하는 함수
    def recommend_recipes(self, recipes, fridge_manager, top_n):
        return None 
