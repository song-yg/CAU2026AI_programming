def make_shopping_list(results):
    shopping = {}

    for result in results:
        recipe_name = result.recipe.name

        for item in result.missing_ingredients:
            if item not in shopping:
                shopping[item] = []

            shopping[item].append(recipe_name)

    return shopping


def print_shopping_list(shopping):
    print("\n[장보기 목록]")

    if len(shopping) == 0:
        print("부족한 재료가 없습니다.")
        return

    for item in shopping:
        print(item)
        print("- 필요한 요리:", shopping[item])
