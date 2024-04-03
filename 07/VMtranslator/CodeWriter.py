#!venv/bin/python3
import os

segment_mapping = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT",
}

class CodeWriter:
    def __init__(self, path):
        splitted = path.split("/")
        file_name, rest_path= splitted[-1].split(".")[0], "/".join(splitted[:-1])
        self._write_file = open(os.path.join(rest_path, file_name + ".asm"), "w")
        self._file_name = file_name
        self._jump_ctr = 0

    def __del__(self):
        self._write_file.close()

    def _generate_asm(self, cmds: list):
        """
        Auxiliary function for generating assembly code from a VM command.
        """
        for command in cmds:
            self._write_file.write(command + "\n")

    def _write_comment(self, comment):
        """
        Writes comment after //
        """
        self._write_file.write(f"// {comment}\n")
    
    def _write_command(self, command):
        """
        Writes asm command
        """
        self._write_file.write(f"{command}\n")

    def _write_push_to_stack(self):
        """ 
        Pushes value of D register in to the stack, and then increases the stack pointer.
        RAM[SP] = D 
        SP++
        """
        # Get Stack pointer (n+1), being n the last value on the stack
        self._write_command("@SP")
        self._write_command("A=M")
        # Push the value on the stack
        self._write_command("M=D")
        # SP++
        self._write_command("@SP")
        self._write_command("M=M+1")
        
    def _write_pop_to_register_d(self):
        """
        Pops the topmost value from the stack, and then stores it on register D.
        """ 
        # Update stack (SP--)
        self._write_command("@SP")
        self._write_command("M=M-1")
        # Get the SP value and store on the D register
        self._write_command("A=M")
        self._write_command("D=M")
        
    def _write_load_register_d_to_segment_index(self, segment, index):
        """ 
        Puts the content of register d into the desired segment_index
        """
        if segment == "constant":
            raise ValueError("You can't use a pop instruction on a constant segment!")

        # Store D on temporal register
        self._write_command("@R13")
        self._write_command("M=D")
        # Select segment 
        self._select_segment_index(segment, index)
        # Save segment address into the register
        self._write_command("D=A")
        self._write_command("@R14")
        self._write_command("M=D")
        # Save value on segment address
        self._write_command("@R13")
        self._write_command("D=M")
        self._write_command("@R14")
        self._write_command("A=M")
        self._write_command("M=D")
        
    def _select_segment_index(self, segment, index):
        """
        Select the segment[index] value
        """
        if segment != "constant":
            # get value from index (offset)
            if segment in segment_mapping:
                """
                Any access to the i-th entry of a virtual segment (in the context of a VM “push /
                pop segmentName i” command) should be translated into assembly code that
                accesses address in the RAM, where base is one of the pointers LCL,
                ARG, THIS, or THAT
                """
                self._write_command(f"@{index}")
                self._write_command(f"D=A")
                # get value from segment (with the offset)
                self._write_command(f"@{segment_mapping[segment]}")
                self._write_command(f"A=M+D")
            elif segment == "pointer":
                """
                Unlike the virtual segments described above, the pointer segment contains exactly two values and 
                is mapped directly onto RAM locations 3 and 4.
                """
                if index == "0":
                    self._write_command(f"@THIS")
                elif index == "1":
                    self._write_command(f"@THAT")
            elif segment == "temp":
                """
                This 8-word segment is also fixed and mapped directly on RAM locations 5 – 12.
                """
                self._write_command(f"@{int(index)+5}")
            elif segment == "static":
                """
                Each reference to static i in a VM program stored in file Foo.vm can
                be translated to the assembly symbol Foo.i
                """
                self._write_command(f"@{self._file_name}{index}")
        else:
            """
            This virtual memory segment is truly virtual, as it does not occupy any physical RAM space.
            """
            self._write_command(f"@{index}") 

    def _prepare_segment_index(self, segment, index):
        """
        Prepares into register D, the desired value of segment[index], for later push.
        """
        # Select segment[index]
        self._select_segment_index(segment, index) 
        # Put on D
        if segment != "constant":
            self._write_command(f"D=M")
        else:
            """
            This virtual memory segment is truly virtual, as it does not occupy any physical RAM space.
            """
            self._write_command("D=A")
        
    def write_push_pop(self, command, segment, index):
        """
        Writes to the output file the assembly code that implements the given
        push or pop command.
        """
        if command == "C_PUSH":
            # Comment (// push)
            self._write_comment(f"push {segment} {index}")
            # Put the content of the desired segment[index] into register D
            self._prepare_segment_index(segment, index)
            # Push content of register D into the stack
            self._write_push_to_stack()
        elif command == "C_POP":
            # Comment (// pop)
            self._write_comment(f"pop {segment} {index}")
            # Pop content of stack to register D
            self._write_pop_to_register_d()
            # Put the content of register D into desired segment[index]
            self._write_load_register_d_to_segment_index(segment, index) 

    def write_arithmetic(self, command: str):
        """
        Writes to the output file the assembly code that implements the given
        arithmetic-logical command.
        """
        def _helper_arithmetic_comparisor_gen(op):
            op = op.upper()
            self._generate_asm([
                f"// {op}"
            ]) 
            # POP R13
            self._write_pop_to_register_d()
            # Store in R13
            self._generate_asm([
                "@R13",
                "M=D",
            ])
            # POP
            self._write_pop_to_register_d()
            # SUB
            self._generate_asm([
                "@R13",
                "D=D-M",
            ])
            # compare result == 0: (equal)
            self._generate_asm([
                f"@IS_{op}_{self._jump_ctr}",
                f"D;J{op}",
            ])
            # result != op 
            self._generate_asm([
                "D=0",
                f"@END_COMP_{self._jump_ctr}",
                "0;JMP"
            ])
            # result == op 
            self._generate_asm([
                f"(IS_{op}_{self._jump_ctr})",
                "D=-1",
                f"(END_COMP_{self._jump_ctr})",
            ])
            # PUSH
            self._write_push_to_stack()
            
            # inc jump ctr (t make aevery label unique)
            self._jump_ctr += 1
        # add
        if command == "add":
            """
            Adds the 2 topmost stack values:
                (x+y)
                 ___      ___
                |...|    |...|
                | x | => |x+y|
                | y |     ‾‾‾      
                 ‾‾‾
                - POP R13
                - POP D
                - SUM R13 D
                - PUSH 
            """
            self._generate_asm([
                "// ADD",
            ])
            # POP
            self._write_pop_to_register_d()
            # Store in R13
            self._generate_asm([
                "@R13",
                "M=D",
            ])
            # POP
            self._write_pop_to_register_d()
            # SUM
            self._generate_asm([
                "@R13",
                "D=D+M"
            ])
            # PUSH
            self._write_push_to_stack()
        # sub
        if command == "sub":
            """
            Subtract the 2 topmost stack values:
                (x-y)
                 ___      ___
                |...|    |...|
                | x | => |x-y|
                | y |     ‾‾‾      
                 ‾‾‾
                - POP R13
                - POP D
                - SUB R13
                - PUSH
            """
            self._generate_asm([
                "// SUB"
            ]) 
            # POP R13
            self._write_pop_to_register_d()
            # Store in R13
            self._generate_asm([
                "@R13",
                "M=D",
            ])
            # POP
            self._write_pop_to_register_d()
            # SUB
            self._generate_asm([
                "@R13",
                "D=D-M"
            ])
            # PUSH
            self._write_push_to_stack()
        # neg
        if command == "neg":
            """ 
            Gets the topmost value and negates it
                -y
                 ___      ___
                |...|    |...|
                | x | => | x |
                | y |    |-y |
                 ‾‾‾      ‾‾‾
                - POP D
                - NEG D 
                - PUSH
            """
            self._generate_asm([
                "// NEG"
            ]) 
            # POP  
            self._write_pop_to_register_d()
            # NEG
            self._generate_asm([
                "D=-D"
            ])
            # PUSH
            self._write_push_to_stack()
        if command == "eq":
        # eq
            """ 
            Makes an arithmetic-logical == operation
            true = -1 (111...111)
            false = 0 (000...000)
                - POP R13
                - POP D
                - D-R13
                    - if result == 0: PUSH -1
                    - else: PUSH 0

                x==y
                
                if x == y:
                 ___      ___
                |...|    |...|
                | x | => |-1 |
                | y |     ‾‾‾      
                 ‾‾‾
                else:
                 ___      ___
                |...|    |...|
                | x | => |-0 |
                | y |     ‾‾‾      
                 ‾‾‾
            """
            _helper_arithmetic_comparisor_gen("eq")
        # gt
        if command == "gt":
            """ 
            Makes an arithmetic-logical > operation
            true = -1 (111...111)
            false = 0 (000...000)
                - POP R13
                - POP D
                - D-R13
                    - if result > 0: PUSH -1
                    - else: PUSH 0

                x>y
                
                if x > y:
                 ___      ___
                |...|    |...|
                | x | => |-1 |
                | y |     ‾‾‾      
                 ‾‾‾
                else:
                 ___      ___
                |...|    |...|
                | x | => |-0 |
                | y |     ‾‾‾      
                 ‾‾‾
            """
            _helper_arithmetic_comparisor_gen("gt")
        # lt
        if command == "lt":
            """ 
            Makes an arithmetic-logical < operation
            true = -1 (111...111)
            false = 0 (000...000)
                - POP R13
                - POP D
                - D-R13
                    - if result > 0: PUSH -1
                    - else: PUSH 0

                x<y
                
                if x < y:
                 ___      ___
                |...|    |...|
                | x | => |-1 |
                | y |     ‾‾‾      
                 ‾‾‾
                else:
                 ___      ___
                |...|    |...|
                | x | => |-0 |
                | y |     ‾‾‾      
                 ‾‾‾
            """
            _helper_arithmetic_comparisor_gen("lt")
        # and
        if command == "and":
            """ 
            Makes an arithmetic-logical bit-wise & operation
                [0&0 = 0, 0&1=0, 1&0=0, 1&1=1]
                - POP R13
                - POP D
                - D&R13
                - PUSH

                x&y
                 ___      ___
                |...|    |...|
                | x | => |x&y|
                | y |     ‾‾‾      
                 ‾‾‾
            """
            self._generate_asm([
                "// AND",
            ])
            # POP
            self._write_pop_to_register_d()
            # Store in R13
            self._generate_asm([
                "@R13",
                "M=D",
            ])
            # POP
            self._write_pop_to_register_d()
            # D&R13
            self._generate_asm([
                "@R13",
                "D=D&M",
            ])
            # PUSH
            self._write_push_to_stack()
        # or
        if command == "or":
            """ 
            Makes an arithmetic-logical bit-wise || operation
                [0||0 = 0, 0||1=1, 1||0=1, 1||1=1]
                - POP R13
                - POP D
                - D||R13
                - PUSH

                x||y
                 ___      ____
                |...|    |....|
                | x | => |x||y|
                | y |     ‾‾‾‾       
                 ‾‾‾
            """
            self._generate_asm([
                "// OR",
            ])
            # POP
            self._write_pop_to_register_d()
            # Store in R13
            self._generate_asm([
                "@R13",
                "M=D",
            ])
            # POP
            self._write_pop_to_register_d()
            # D&R13
            self._generate_asm([
                "@R13",
                "D=D|M",
            ])
            # PUSH
            self._write_push_to_stack()
        # not
        if command == "not":
            """ 
            Makes an arithmetic-logical bit-wise ! operation
                [!0=1, !1=0]
                - POP D
                - !D
                - PUSH

                !y
                 ___      ___
                |...|    |...|
                | x | => | x |
                | y |    |!y |
                 ‾‾‾      ‾‾‾
            """
            self._generate_asm([
                "// NOT",
            ])
            # POP
            self._write_pop_to_register_d()
            # !D 
            self._generate_asm([
                "D=!D",
            ])
            # PUSH
            self._write_push_to_stack()
    
    def finish_him(self):
        """
        Gracefully terminates the execution flow, avoiding infinite execution
            - (FINISH)
            - @FINISH
            - 0;JMP
        """  
        self._generate_asm([
            "// FINISH HIM!",
        ])
        self._generate_asm([
            "(FINISH)",
            "@FINISH",
            "0;JMP",
        ])
# debug
if __name__ == "__main__":
    code_writer = CodeWriter("prueba")
    code_writer.write_arithmetic("eq")
