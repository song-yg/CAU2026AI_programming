from fridge_manager import FridgeManager
from recipe_loader import load_recipes
from recommender import recommend_recipes
from ai_helper import AIHelper
from shopping_list import make_shopping_list, print_shopping_list
from meal_planner import make_meal_plan, print_meal_plan
# models와 storage는 왜 없음?
# main.py에서 직접적으로 사용하는 부분이 없어서 import 안 해도 될 것 같음.

def print_recommendations(results): 
    print("\n[추천 결과]")

    if len(results) == 0:
        print("추천 결과가 없습니다.")
        return

    for i in range(len(results)):
        result = results[i]

        print("\n" + str(i + 1) + ". " + result.recipe.name)
        print("추천 점수:", round(result.score, 2))
        print("재료 일치율:", round(result.match_rate, 1), "%")
        print("부족한 재료:", result.missing_ingredients)
        print("조리 시간:", result.recipe.minutes, "분")
        print("유통기한 임박 재료:", result.urgent_ingredients)

#results는 recommend_recipes()의 반환값인 RecommendationResult 객체들의 list.


def get_fridge_names(fridge):
    names = []

    for ingredient in fridge.ingredients:
        names.append(ingredient.name)

    return names
#현재 냉장고에 보관중인 모든 재료의 이름만 가져와서 문자열 list를 반환. 
#ai_helper.rewrite_instructions() 함수에서 냉장고에 있는 재료 이름들을 전달해서, 레시피의 조리법을 냉장고 재료에 맞게 재작성할 때 사용.

# fridge 객체는 FridgeManager 클래스의 객체. main.py의 main()에서 
# main.py에서 FridgeManager 객체를 만들어서 그 객체에 냉장고 정보를 불러온 다음에, ai_helper.rewrite_instructions() 함수를 호출할 때 fridge 객체를 인자로 전달해주면 됩니다.

def select_result_from_results(results, max_count, empty_message):
    if len(results) == 0:
        print(empty_message)
        return None

    visible_results = results[:max_count]
    print_recommendations(visible_results)

    try:
        number = int(input("요리 번호: "))
    except Exception:
        print("숫자를 입력해야 합니다.")
        return None

    if number < 1 or number > len(visible_results):
        print("잘못된 번호입니다.")
        return None

    return visible_results[number - 1]


def select_result_from_last_results(last_results, max_count):
    return select_result_from_results(
        last_results,
        max_count,
        "먼저 레시피 추천을 받아야 합니다."
    )


def get_available_results(results):
    available_results = []

    for result in results:
        if len(result.missing_ingredients) == 0:
            available_results.append(result)

    return available_results


def print_consumption_candidates(results):
    print("\n[추천 요리 및 재료 차감 가능 여부]")

    if len(results) == 0:
        print("추천 결과가 없습니다.")
        return

    for i in range(len(results)):
        result = results[i]

        if len(result.missing_ingredients) == 0:
            status = "차감 가능"
        else:
            status = "차감 불가"

        print("\n" + str(i + 1) + ". " + result.recipe.name + " [" + status + "]")
        print("추천 점수:", round(result.score, 2))
        print("재료 일치율:", round(result.match_rate, 1), "%")
        print("조리 시간:", result.recipe.minutes, "분")
        print("유통기한 임박 재료:", result.urgent_ingredients)

        if len(result.missing_ingredients) == 0:
            print("부족한 재료: 없음")
        else:
            print("부족한 재료:", result.missing_ingredients)


def select_result_for_consumption(results, max_count):
    if len(results) == 0:
        print("추천 결과가 없습니다.")
        return None

    visible_results = results[:max_count]
    print_consumption_candidates(visible_results)

    try:
        number = int(input("요리 번호: "))
    except Exception:
        print("숫자를 입력해야 합니다.")
        return None

    if number < 1 or number > len(visible_results):
        print("잘못된 번호입니다.")
        return None

    return visible_results[number - 1]


def main():
    ai = AIHelper()
    fridge = FridgeManager(ai_helper=ai)
    recipes = load_recipes()

    last_results = []

    print("레시피", len(recipes), "개를 불러왔습니다.")

    while True:
        print("\n===== FridgeMate =====")
        print("1. 냉장고 재료 추가")
        print("2. 냉장고 재료 목록 보기")
        print("3. 유통기한 임박 재료 보기")
        print("4. Python 레시피 추천 받기")
        print("5. 기본 조리법 보기")
        print("6. 추천 요리 선택 후 재료 차감")
        print("7. 장보기 목록 생성")
        print("8. 3일 식단 추천")
        print("9. 냉장고 재료 버리기/삭제")
        print("10. AI 추천 재정렬")
        print("11. AI 대체재 / 맞춤 조리법 보기")
        print("0. 종료")

        choice = input("메뉴 선택: ")

        if choice == "1":
            name = input("재료명: ")
            quantity = input("수량: ")
            unit = input("단위: ")
            expire_days = input("유통기한까지 남은 날짜: ")

            fridge.add_ingredient(name, quantity, unit, expire_days)

            if len(last_results) > 0:
                last_results = recommend_recipes(recipes, fridge, 10)

        elif choice == "2":
            fridge.print_all()

        elif choice == "3":
            fridge.print_expiring_soon()

        elif choice == "4":
            top10 = recommend_recipes(recipes, fridge, 10)
            last_results = top10

            print("\nPython 알고리즘으로 추천 결과를 계산했습니다.")
            print_recommendations(top10)

        elif choice == "5":
            result = select_result_from_last_results(last_results, 10)

            if result is None:
                continue

            selected_recipe = result.recipe

            print("\n선택한 요리:", selected_recipe.name)

            print("\n[기본 조리법]")
            print(selected_recipe.instructions)

            print("\n[부족한 재료]")
            if len(result.missing_ingredients) == 0:
                print("부족한 재료가 없습니다.")
            else:
                print(result.missing_ingredients)

        elif choice == "6":
            # 재료 차감은 실제 냉장고 재고가 변했을 수 있으므로
            # 현재 재고 기준으로 추천 결과를 다시 계산한다.
            fresh_results = recommend_recipes(recipes, fridge, len(recipes))
            last_results = fresh_results[:10]

            result = select_result_for_consumption(fresh_results, 10)

            if result is None:
                continue

            if len(result.missing_ingredients) > 0:
                print("\n이 요리는 아직 재료가 부족해서 차감할 수 없습니다.")
                print("부족한 재료:", result.missing_ingredients)
                print("7번 메뉴에서 장보기 목록을 확인하거나, 1번 메뉴에서 부족한 재료를 추가하세요.")
                continue

            success = fridge.consume_ingredients(result.recipe)

            if success == True:
                last_results = recommend_recipes(recipes, fridge, 10)

        elif choice == "7":
            if len(last_results) == 0:
                print("먼저 레시피 추천을 받아야 합니다.")
                continue

            shopping = make_shopping_list(last_results[:5])
            print_shopping_list(shopping)

        elif choice == "8":
            if len(last_results) == 0:
                print("먼저 레시피 추천을 받아야 합니다.")
                continue

            plan = make_meal_plan(last_results[:6])
            print_meal_plan(plan)

        elif choice == "9":
            name = input("버릴 재료명: ")
            quantity = input("버릴 수량(전부 삭제하려면 Enter): ")

            if quantity.strip() == "":
                fridge.delete_ingredient(name)
            else:
                unit = input("단위: ")
                fridge.discard_ingredient(name, quantity, unit)

            last_results = recommend_recipes(recipes, fridge, 10)

        elif choice == "10":
            if len(last_results) == 0:
                print("먼저 4번 메뉴에서 Python 추천을 받아야 합니다.")
                continue

            user_condition = input("원하는 조건을 입력하세요: ")
            ai_result = ai.rerank_recipes(last_results[:10], user_condition)

            if ai_result is None:
                print("\n대신 Python 추천 결과를 출력합니다.")
                print_recommendations(last_results[:5])

            else:
                print("\n[AI 추천 재정렬 결과]")
                print(ai_result)

        elif choice == "11":
            result = select_result_from_last_results(last_results, 10)

            if result is None:
                continue

            selected_recipe = result.recipe

            print("\n선택한 요리:", selected_recipe.name)

            print("\n[기본 조리법]")
            print(selected_recipe.instructions)

            if len(result.missing_ingredients) > 0:
                ai_sub = ai.suggest_substitutes(result.missing_ingredients)

                if ai_sub is None:
                    print("\n부족한 재료:", result.missing_ingredients)

                else:
                    print("\n[AI 대체재 추천]")
                    print(ai_sub)

            else:
                print("\n부족한 재료가 없어 AI 대체재 추천을 생략합니다.")

            fridge_names = get_fridge_names(fridge)
            ai_recipe = ai.rewrite_instructions(selected_recipe, fridge_names)

            if ai_recipe is None:
                print("\n기본 조리법을 사용하세요.")

            else:
                print("\n[AI 맞춤 조리법]")
                print(ai_recipe)

        elif choice == "0":
            print("프로그램을 종료합니다.")
            break

        else:
            print("잘못된 메뉴입니다.")


if __name__ == "__main__":
    main()
# main 파일을 직접 실행할 때만 main() 함수를 호출하도록 하는 조건문입니다.
# 이 조건문이 실행되어서 main() 함수가 호출되면, 프로그램이 시작되고 사용자에게 메뉴가 출력되면서 상호작용이 가능해집니다.
