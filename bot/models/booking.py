from datetime import datetime
from bson import ObjectId

class Booking:
    def __init__(self, user_id, car_id, start_date, end_date, pickup_location, dropoff_location, total_price, status="pending", _id=None):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.car_id = car_id
        self.start_date = start_date
        self.end_date = end_date
        self.pickup_location = pickup_location
        self.dropoff_location = dropoff_location
        self.total_price = total_price
        self.status = status
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            "_id": str(self._id),
            "user_id": self.user_id,
            "car_id": self.car_id,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "pickup_location": self.pickup_location,
            "dropoff_location": self.dropoff_location,
            "total_price": self.total_price,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        data['_id'] = ObjectId(data['_id'])
        data['start_date'] = datetime.fromisoformat(data['start_date'])
        data['end_date'] = datetime.fromisoformat(data['end_date'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)