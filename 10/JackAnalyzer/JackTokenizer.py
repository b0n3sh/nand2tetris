class JackTokenizer:
    def __init__(self, file):
        self.__opened_file = self.open_file(file)
        self.__next_token = None
        self.__has_more_tokens = None
        self.__current_token = '' # Will held the full token for the current op

    def __next__(self):
        if self.__has_more_tokens:
            return self.__next_token
        else:
            return next(self.__opened_file)
    
    def hasMoreTokens(self):
        try:
            self.__next_token = next(self.__opened_file)
            self.__has_more_tokens = True
        except:
            self.__has_more_tokens = False
        return self.__has_more_tokens

    def open_file(self, file):
        with open(file, "r") as f:
            for line in f:
                for word in line:
                    yield(word)

    def advance(self):
        self.__current_token = next(self)
        return self.__current_token
        
tokenizer = JackTokenizer("test.jack")
while tokenizer.hasMoreTokens():
    print(tokenizer.advance())
