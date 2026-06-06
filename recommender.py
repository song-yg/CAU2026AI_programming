from models import UnitManager

ALWAYS_AVAILABLE = ["물"]

class RecommendationResult:
    def __init__(self, recipe, score, match_rate, missing_ingredients, urgent_ingredients):
        self.recipe = recipe
        self.score = score
        self.match_rate = match_rate
        self.missing_ingredients = missing_ingredients
        self.urgent_ingredients = urgent_ingredients


# 함수들이 클래스 밖에 있는 이유: main에서 전체 클래스 호출 안하고도 부분부분 뽑아쓰려고. 


# 냉장고에 있는 재료 이름 목록을 만든다.
def get_fridge_names(fridge_manager):
    names = []

    for ingredient in fridge_manager.ingredients: #현재 냉장고 재료 각각 추출
        if ingredient.name not in names: #19번째 줄에서 선언한 빈 리스트에 냉장고 재료 목록 작성
            names.append(ingredient.name)

    return names #냉장고 재료 목록 반환


''' 실직적으로 안쓰이는 함수인데... 공유된 파일에 있어서 남겨는 놓겠습니다.
def find_fridge_item(fridge_manager, name):
    return fridge_manager.find_ingredient(name)
'''


def get_required_items(recipe):
    """
    레시피가 실제로 요구하는 재료 목록을 만든다.
    used_ingredients가 있으면 수량과 단위까지 검사할 수 있고,
    없으면 이름만 검사한다.
    """
    if len(recipe.used_ingredients) > 0:
        """used_ingredients = [{
                "name": name,
                "amount": amount,
                "unit": unit,
            }, ...] 딕셔너리가 들어있는 리스트"""
        return recipe.used_ingredients
    
    #레시피 재료가 이름만 있는 경우
    required_items = []

    for name in recipe.ingredients_list: 
        required_items.append({
            "name": name,
            "amount": None,
            "unit": None, #오류가 나지 않도록 리스트 안에 딕셔너리로 형태를 맞춰줌.
        })
    return required_items

#재료 정보 정리 함수 추가
def normalize_required_item(required):
    unit_manager = UnitManager()

    name = unit_manager.normalize_name(required["name"])
    amount = required.get("amount")
    unit = required.get("unit")

    if unit is not None: #추출한 레시피에서 단위가 존재하는 경우
        unit = unit_manager.normalize_unit_name(unit)

    return name, amount, unit


# 냉장고에 필요한 재료가 있는지 검사
def check_required_item(fridge_manager, required):
    name, amount, unit = normalize_required_item(required) #UnitManager 돌고 온 변수로 변경

    if name in ALWAYS_AVAILABLE: #물
        return True, ""
    
    #batches = 냉장고에 한 재료가 여러번 저장된 경우, 그 재료의 여러 저장된 양을 합쳐야할 수도 있어서 냉장고에 저장된 재료의 목록을 가져옴
    batches = fridge_manager.get_batches(name)

    #냉장고에 재료가 하나도 없는 경우
    if len(batches) == 0:
        return False, name
    
    #레시피에 수량/단위가 없는 경우 냉장고에 재료가 있는지만 검사
    if amount is None or unit is None: #위에서 이미 재료가 없는 경우는 다 걸려나감.
        return True, ""
    
    #냉장고에 해당 재료 총량을 필요 단위로 환산
    total = fridge_manager.get_total_quantity(name, unit)

    if total == 0: #레시피와 냉장고에 재료가 있는데도 단위가 달라서 뻑나는 구간. fredge_manager에서 get_total_quantity 부분 수정 필요함
        return False, name + "(단위 다름: 냉장고 " + batches[0].unit + ", 필요 " + unit + ")"

    if total < amount: #부족해서 부족하다고 알려주는 구간
        shortage = amount - total
        return False, name + "(" + str(round(shortage, 2)) + unit + " 부족)"

    return True, ""


# 레시피와 냉장고를 비교해서 일치하는 재료의 비율을 계산한다.
def calculate_match_rate(recipe, fridge_manager):
    required_items = get_required_items(recipe)

    #레시피가 재료를 요구하지 않는 경우. 일치율 0% 반환
    total = len(required_items)
    if total == 0:
        return 0
    
    #초깃값 설정
    matched = 0

    for required in required_items:
        #message는 튜플 자릿수 맞추려고 넣은거라 실제로는 사용 안함
        is_available, message = check_required_item(fridge_manager, required)
        if is_available == True:
            matched = matched + 1

    return matched / total * 100 #백분율


# 레시피에 필요한 재료 중에서 냉장고에 없는 재료의 목록을 만든다.
def find_missing_ingredients(recipe, fridge_manager):
    required_items = get_required_items(recipe)
    missing = []
    for required in required_items:
        is_available, message = check_required_item(fridge_manager, required)
        
        #사용 불가한 재료만 메시지와 함께 missing 리스트에 추가
        if is_available == False:
            missing.append(message)
    #부족한 재료 메시지 목록 반환 (예: ["멸치육수(50.0ml 부족)", "된장"])
    return missing


# 레시피에 필요한 재료 중에서 냉장고에서 곧 상할 재료의 긴급도를 계산한다.
def calculate_expire_urgency(recipe, fridge_manager):
    urgency = 0
    urgent_ingredients = []

    for required in get_required_items(recipe):
        name, amount, unit = normalize_required_item(required)

        #물 유통기한 제외
        if name in ALWAYS_AVAILABLE:
            continue

        #유통기한 임박한 것 가져오기
        expire_days = fridge_manager.get_earliest_expire_days(name)
        if expire_days is not None:
            safe_days = expire_days
            if safe_days < 0:
                safe_days = 0
            urgency = urgency + 1 / (safe_days + 1)

            # 유통기한이 3일 이내인 재료는 긴급하게 사용해야 함
            if expire_days <= 3:
                text = name + "(" + str(expire_days) + "일)"

                if text not in urgent_ingredients:
                    urgent_ingredients.append(text)

    return urgency, urgent_ingredients


# 최종 점수 계산
def calculate_score(recipe, fridge_manager):
    match_rate = calculate_match_rate(recipe, fridge_manager)
    missing = find_missing_ingredients(recipe, fridge_manager)
    urgency, urgent_ingredients = calculate_expire_urgency(recipe, fridge_manager)

    score = match_rate + 20 * urgency - 5 * len(missing) - 0.3 * recipe.minutes

    result = RecommendationResult(
        recipe,
        score,
        match_rate,
        missing,
        urgent_ingredients,
    )

    return result


# 레시피 목록과 냉장고를 비교해서 점수가 높은 순으로 레시피를 추천한다.
def recommend_recipes(recipes, fridge_manager, top_n):
    results = []

    for recipe in recipes:
        result = calculate_score(recipe, fridge_manager)
        results.append(result)
    results.sort(key=lambda x: x.score, reverse=True)

    return results[:top_n]
