#!venv/bin/python3

class Parser():
    def __init__(self, file: str):
        self.gen_file = self.get_gen(file)  # Get the generator
        self._has_more_lines = None
        self._next_line = None
        self._current_instruction = None

    def __next__(self):
        "Implement next, if using hasMorelines, takes the previous fetched value, if not, uses next of the generator"
        if self._has_more_lines:
            return self._next_line
        else:
            return next(self.gen_file)

    def __iter__(self):
        "Defines an iterable"
        return self
    
    def get_gen(self, file: str) -> str:
        "Get the generator" 
        with open(file, "r") as f:
            for line in f:
                yield line.strip()

    def has_more_lines(self) -> bool:
        "If has more lines, return true and prepares the next fetch"
        try:
            self._next_line = next(self.gen_file)    
            self._has_more_lines = True
        except:
            self._has_more_lines = False
        return self._has_more_lines

    def advance(self) -> str:
        next_line = next(self)
        if next_line[:2] == "//" or next_line == "":
            if self.has_more_lines():
                self._current_instruction = self.advance()
                return self._current_instruction
        else:
            self._current_instruction = next_line
            return self._current_instruction

    def command_type(self) -> str:
        """
            # Returns the type of the current command:
            #   [+] C_ARITHMETIC
            #   [+] C_PUSH 
            #   [+] C_POP 
            #   [+] C_LABEL 
            #   [+] C_GOTO 
            #   [+] C_IF 
            #   [+] C_FUNCTION 
            #   [+] C_RETURN 
            #   [+] C_CALL 
        """
        cmds = self._current_instruction.split()
        if cmds[0] in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
            return "C_ARITHMETIC"
        elif cmds[0] == "push":
            return "C_PUSH"
        elif cmds[0] == "pop":
            return "C_POP"
        # To implement the rest
        ...

    def arg1(self):
        command_type = self.command_type()
        if command_type != "C_RETURN":
            cmds = self._current_instruction.split()
            if command_type == "C_ARITHMETIC":
                return cmds[0]
            else:
                return cmds[1]
         
    def arg2(self):
        if self.command_type() in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]:
            return self._current_instruction.split()[2]

# Debug
if __name__ == "__main__":
    object_parser = Parser("prueba")
    while object_parser.has_more_lines():
        print(object_parser.advance())
        print(object_parser.command_type())
        print(f"El primero es : {object_parser.arg1()},  el segundo es: {object_parser.arg2()}")
