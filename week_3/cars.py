import os

class CarBase:
    def __init__(self, brand, photo_file_name, carrying):
      self.brand = brand
      self.photo_file_name = photo_file_name
      self.carrying = float(carrying)
      
    def get_photo_file_ext(self):
        _, ext = os.path.splitext(self.photo_file_name)
        
        return ext
    

class Car(CarBase):
    car_type = "car"
    def __init__(self, brand, photo_file_name, carrying, passenger_seats_count):
        super().__init__(brand, photo_file_name, carrying)
        self.passenger_seats_count = int(passenger_seats_count)
        
class Truck(CarBase):
    car_type = "truck"
    def __init__(self, brand, photo_file_name, carrying, body_whl):
        super().__init__(brand, photo_file_name, carrying)
        try:
            length, width, height = (float(c) for c in body_whl.split("x", 2))
        except Exception:
            length, width, height = .0, .0, .0

        self.body_length = length
        self.body_width = width
        self.body_height = height
        
    def get_body_volume(self):
        return self.length * self.width * self.body_height
    

class SpecMachine(CarBase):
    car_type = "spec_machine"
    def __init__(self, brand, photo_file_name, carrying, extra):
        super().__init__(brand, photo_file_name, carrying)
        self.extra = extra
