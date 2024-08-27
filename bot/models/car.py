from bson import ObjectId

class Car:
    def __init__(self, brand, model, year, car_type, daily_rate, status="available", _id=None):
        self._id = _id or ObjectId()
        self.brand = brand
        self.model = model
        self.year = year
        self.car_type = car_type
        self.daily_rate = daily_rate
        self.status = status

    def to_dict(self):
        return {
            "_id": str(self._id),
            "brand": self.brand,
            "model": self.model,
            "year": self.year,
            "car_type": self.car_type,
            "daily_rate": self.daily_rate,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        data['_id'] = ObjectId(data['_id'])
        return cls(**data)