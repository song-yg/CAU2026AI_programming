class UnitManager:
    def __init__(self):
        pass
    UNIT1_MAPPING = { #단위 통일 : 단순히 용어 대체
        "그램" : "g",
        "gram" : "g",
        "킬로그램" : "kg",
        "kilogram" : "kg",
        "kilo" : "kg",
        "밀리리터" : "ml",
        "milliliter" : "ml",
        "mL" : "ml",
        "cc" : "ml",
        "씨씨" : "ml",
        "리터" : "l",
        "liter" : "l",
        "알" : "개",
        "pcs" : "개",
        "piece" : "개",
        "큰스푼" : "큰술",
        "스푼" : "큰술",
        "tbsp" : "큰술",
        "티스푼" : "작은술",
        "tsp" : "작은술",
        "그릇" : "공기",
        "cup" : "컵",
        "c" : "컵",
        "온즈" : "oz",
        "온스" : "oz",
        "pint" : "pt",
        "파인트" : "pt",
        "quart" : "qt",
        "쿼트" : "qt"
    }
    UNIT2_MAPPING = { #단위 통일 : 수량 변환
        "컵" : 200,  #1컵 = 200ml 기준
        "oz" : 30, #1oz = 30ml 기준 (정확히 29.57ml이지만 편의상 30ml로 계산)
        "pt" : 473, #1pt = 473ml 기준
        "qt" : 946, #1qt = 946ml 기준
    }
    UNIT3_MAPPING = { #ml로 통일
        "컵" : "ml",
        "oz" : "ml",
        "pt" : "ml",
        "qt" : "ml"
    }
    def unit_conversion(self, target=[0,0,0,0]): #타겟

        '''
        냉장고 재료 추가가 다음과 같은 형식이라 가정하고 코드를 작성하겠다.
        target = [재료명, 수량, 단위, 유통기한]
        '''
        self.target = target
        unit = str(target[2]).strip().lower() #소문자로 통일, 한글이어도 오류 X
        if unit in self.UNIT1_MAPPING: #만일 단위가 통일되어야 하는 (수정되어야하는) 경우라면
            target[2] = self.UNIT1_MAPPING[unit] #그 단위를 통일된 단위로 바꿔준다.
        if target[2] in self.UNIT2_MAPPING: #만일 단위가 수량 변환이 필요한 단위라면
            target[1] = float(float(target[1]) * float(self.UNIT2_MAPPING[target[2]])) #수량 변환
            target[2] = self.UNIT3_MAPPING[target[2]] #단위 변환
        return target
