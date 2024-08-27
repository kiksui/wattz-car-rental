from bson import ObjectId

class User:
    def __init__(self, telegram_id, first_name, last_name=None, username=None, phone_number=None, kyc_status="not_submitted", _id=None):
        self._id = _id or ObjectId()
        self.telegram_id = telegram_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.phone_number = phone_number
        self.kyc_status = kyc_status

    def to_dict(self):
        return {
            "_id": str(self._id),
            "telegram_id": self.telegram_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "phone_number": self.phone_number,
            "kyc_status": self.kyc_status
        }

    @classmethod
    def from_dict(cls, data):
        data['_id'] = ObjectId(data['_id'])
        return cls(**data)