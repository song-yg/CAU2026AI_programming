class Ingredient:
    def __init__(self, name, quantity, unit, expire_days):
        self.name = str(name).strip()
        self.quantity = float(quantity)
        self.unit = str(unit).strip()
        self.expire_days = int(expire_days)

        if self.name == "":
            raise ValueError("재료명이 비어있습니다.")

        if self.quantity <= 0:
            raise ValueError("수량은 양수여야 합니다.")

        if self.unit == "":
            raise ValueError("단위가 비어 있습니다.")

        if self.expire_days < 0:
            raise ValueError("유통기한은 0일 이상이어야 합니다.")

    def to_dict(self):
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "expire_days": self.expire_days
        }
    @staticmethod
    #data 딕셔너리는 storage.py에서 fridge.json을 읽어와서 만듦. 재료 하나를 Ingeridient 객체로 만듦. 
    def from_dict(data):
        return Ingredient(
            data.get("name"),
            data.get("quantity"),
            data.get("unit"),
            data.get("expire_days")
        )
