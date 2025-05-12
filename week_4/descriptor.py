class Value:
    def __get__(self, obj, obj_type):
        if obj is None:
            return self
        return getattr(obj, '_amount', 0)

    def __set__(self, obj, value):
        calculated_value = value - value * obj.commission
        obj._amount = calculated_value

class Account:
    amount = Value()

    def __init__(self, commission):
        self.commission = commission
