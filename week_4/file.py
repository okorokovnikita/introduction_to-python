import os
import uuid

class File:
    def __init__(self, path_to_file):
        self.offset = 0
        self.path_to_file = path_to_file
        if not os.path.exists(self.path_to_file):
            with open(self.path_to_file, 'w'):
                pass
    
    def read(self):
        with open(self.path_to_file, "r") as f:
            return f.read()
        
    def write(self, content):
        with open(self.path_to_file, "w") as f:
            f.write(content)   
        return(len(content))
    
    def __str__(self):
        return self.path_to_file
    
    def __add__(self, obj):
        new_path = os.path.join(
            os.path.dirname(self.path_to_file),
            str(uuid.uuid4().hex)
        )
        new_file = File(new_path)
        new_file.write(self.read() + obj.read())

        return new_file
    
    def __iter__(self):
        return self
    
    def __next__(self):
        with open(self.path_to_file, 'r') as file:
            file.seek(self.offset)
            line = file.readline()
            if not line:
                raise StopIteration('End of File reached')
            self.offset= file.tell()
            return line
