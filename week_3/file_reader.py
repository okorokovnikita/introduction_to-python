class FileReader:
    def __init__(self, path_to_file):
        self.path = path_to_file

    def read(self):
        try:
            with open(self.path) as f:
                return f.read()
        except FileNotFoundError:
            return ""
