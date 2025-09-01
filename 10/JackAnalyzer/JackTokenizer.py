class JackTokenizer:
    def __init__(self, file):
        self.__opened_file = self.open_file(file)
        self.__next_value = None
        self.__has_more_tokens = None

    def __next__(self):
        pass 
    
    def hasMoreTokens(self):
        next_token = self.__opened_file

    def open_file(self, file):
        with open(file, "r") as f:
            for line in f:
                for word in line:
                    yield(word)

tokenizer = JackTokenizer("test.jack")
tokenizer.hasMoreTokens()
