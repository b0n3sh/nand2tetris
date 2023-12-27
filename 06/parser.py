#!venv/bin/python3
import re

class Parser:
    def __init__(self, path):
        self.gen = self._open_file(path)
        self._has_next = None

    # Open the file and return a generator item, ready to parse it
    def _open_file(self, path):
        with open(path, "r") as f:
            for line in f:
                yield line
    
    def __iter__(self):
        return self

    def __next__(self):
        if self._has_next:
            return self._next_value
        else:
            return next(self.gen)

    # Are there more lines in the input?
    def hasMoreLines(self):
        try:
            self._next_value = next(self.gen)
            self._has_next = True
        except:
            self._has_next = False 

        return self._has_next

    # Skips over white space and comments, if neccesary.
    # Reads the next instruction from the input, and makes it the current instruction.
    # This routine should be called only if hasMoreLines is true.
    # Initially there is no current instruction.
    def advance(self):
        line = next(self)
        if re.match("//", line) or line=="\n":
            if self.hasMoreLines():
                self._current_instruction = self.advance() 
                return self._current_instruction
        else:
            self._current_instruction = line
            return self._current_instruction

    # Returns the type of the current instruction:
    #   - A_INSTRUCTION for @xxx, where xxx is either a decimal number or a symbol
    #   - C_INSTRUCTION for dest=comp;jump
    #   - L_INSTRUCTION for (xxx), where xxx is a symbol
    def instructionType(self):
        if self._current_instruction[0] == "@":
            return "A_INSTRUCTION"
        elif self._current_instruction[0] == "(":
            return "L_INSTRUCTION"
        else:
            return "C_INSTRUCTION"

    # If the current instruction is (xxx), returns teh symbol xxx.
    # If the current instruction is @xxx, returns the symbol or decimal xxx (as a string).
    # Should be called only if instructionType is A_INSTRUCTION or L_INSTRUCTION.
    def symbol(self):
        instruction_type = self.instructionType()
        if instruction_type == "A_INSTRUCTION":
            return re.search("@(\w+)", self._current_instruction).group(1)
        elif instruction_type == "L_INSTRUCTION":
            return re.search("\((\w+)\)", self._current_instruction).group(1)

    # Returns the symbolic dest part of the current C-instruction (8 possibilities).
    # Should be called only if instructionType is C_INSTRUCTION
    def dest(self):
        instruction_type = self.instructionType() 
        if instruction_type == "C_INSTRUCTION":
            return re.search("(\w+)=", self._current_instruction).group(1)

    # Returns the symbolic comp part of the current C-instruction (28 possibilities).
    # Should be called only if instructionType is C_INSTRUCTION
    def comp(self):
        instruction_type = self.instructionType()
        if instruction_type == "C_INSTRUCTION":
            return re.search("=([\w+\-]+)", self._current_instruction).group(1)  

    # Returns the symbolic jump part of the current C-instruction (8 possibilities).
    # Should be called only if instructionType is C_INSTRUCTION
    def jump(self):
        instruction_type = self.instructionType()
        if instruction_type == "C_INSTRUCTION":
            if ";" in self._current_instruction:
                return re.search("(?<=;)\w+", self._current_instruction).group(0)
            else:
                return "null"
        
# Debug
if __name__ == "__main__":
    my_assembler = Parser("max/Max.asm")

    while my_assembler.hasMoreLines():
        print(my_assembler.advance())
        print(my_assembler.jump())
