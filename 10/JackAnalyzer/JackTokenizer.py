class JackTokenizer:
    def __init__(self, file):
        self.opened_file = self.open_file(file)
    
    def hasMoreTokens(self):
        next_token = self.opened_file.seek(1)
        print(next_token)

    def open_file(self, file):
        with open(file, "r") as f:
            yield f

tokenizer = JackTokenizer("test.jack")
