class Ingredient:
    def __init__(self, name, quantity, unit, expire_days):
        self.name = str(name).strip()
        self.quantity = float(quantity)
        self.unit = str(unit).strip()
        self.expire_days = int(expire_days)

    def to_dict(self):
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "expire_days": self.expire_days
        }

    def from_dict(data):
        return Ingredient(
            name=data.get("name"),
            quantity=data.get("quantity"),
            unit=data.get("unit"),
            expire_days=data.get("expire_days")
        )
