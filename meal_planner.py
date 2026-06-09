def make_meal_plan(results):
    plan = []
    count = 0

    for day in range(1, 4):
        lunch = None
        dinner = None

        if count < len(results):
            lunch = results[count].recipe.name #레시피 객체의 name 속성을 사용하여 점심 메뉴 이름을 가져온다.
            count = count + 1

        if count < len(results):
            dinner = results[count].recipe.name
            count = count + 1
          #레시피 추천 결과가 없을 경우 발생할 오류 방지하고 None으로 처리

        plan.append({
            "day": day,
            "lunch": lunch,
            "dinner": dinner,
        })

    return plan


def print_meal_plan(plan):
    print("\n[3일 식단 추천]")

    for item in plan:
        lunch = item["lunch"]
        dinner = item["dinner"]

        if lunch is None:
            lunch = "추천 없음"

        if dinner is None:
            dinner = "추천 없음"

        print(str(item["day"]) + "일차")
        print("점심:", lunch)
        print("저녁:", dinner)
