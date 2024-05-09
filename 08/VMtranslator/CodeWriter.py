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
        self._current_function = "none" 
        self._call_function_counter = {}

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

    def write_label(self, label):
        """
        Writes assembly code that effects the label command.
        """     
        # Comment
        self._generate_asm([
            f"// LABEL {self._current_function}${label}",
        ])
        # Code
        self._generate_asm([
            f"({self._current_function}${label})"
        ])

    def write_goto(self, label):
        """
        Writes assembly code that effects the goto command.
        """
        # Comment
        self._generate_asm([
            f"// GOTO {self._current_function}${label}",
        ])
        # Code
        self._generate_asm([
            f"@{self._current_function}${label}",
            "0;JMP"
        ])

    def write_if(self, label):
        """
        Writes assembly code that effects the if-goto command.
        """
        # Comment
        self._generate_asm([
            f"// IF-GOTO {self._current_function}${label}",
        ])
        self._write_pop_to_register_d()
        # Code
        self._generate_asm([
            f"@{self._current_function}${label}",
            "D;JNE" # jumps if the popped value != 0
        ])

    def write_function(self, function_name: str, n_local_variables: str):
        """
        Writes assembly code that effects the function command (initializes to 0 the n of local variables)
        """

        def _init_local_variables(n_local_variables: str):
            for i in range(int(n_local_variables)):
                self._generate_asm([
                    "@0",
                    "D=A",
                ])
                self._write_push_to_stack()

        # Tell CodeWriter we are in a new function
        self._current_function = function_name.split(".")[-1]

        # Comment 
        self._generate_asm([
            f"// FUNCTION {function_name} WITH {n_local_variables} LOCAL VARIABLES",
            f"({function_name})",
        ])
        # Code 
        _init_local_variables(n_local_variables)

    def write_return(self):
        """
        Writes assembly code that effects the return command
        """

        def _restore_previous_stack(index: int, name: str):
            return [
                f"@{index}",
                "D=A",
                "@frame",
                "A=M-D",
                "D=M",
                f"@{name}",
                "M=D", ### TOCHECK
            ]
        
        # Comment
        self._generate_asm([
            f"// FUNCTION RETURN {self._current_function}" 
        ])
        
        # Code
        # frame = LCL, points to the end of the frame for relative references
        # retAddr = *(frame-5), puts the return address in a temporary variable
        self._generate_asm([
            # frame = LCL, points to the end of the frame for relative references
            "// frame = LCL, points to the end of the frame for relative references",
            "@LCL",
            "D=M",
            "@frame",
            "M=D",
            # retAddr = *(frame-5), puts the return address in a temporary variable
            "// retAddr = *(frame-5)",
            "@5",
            "D=A",
            "@frame",
            "A=M-D",
            "D=M",
            "@retAddr",
            "M=D",
        ])

        # *ARG = pop(), repositions the return value for the caller
        self._generate_asm(["// *ARG = pop(), repositions the return value for the caller"])
        self._write_pop_to_register_d()
        self._generate_asm([
            "@ARG",
            "A=M",
            "M=D",
        ])

        # SP = ARG+1, repositions SP for the caller
        self._generate_asm([
            "@ARG",
            "D=M",
            "A=D+1",
            "D=A",
            "@SP",
            "M=D", 
        ])

        # code
        # THAT = *(frame-1)
        # THIS = *(frame-2)
        # ARG = *(frame-3)LCL
        # LCL = *(frame-4)
        self._generate_asm([
            # THAT = *(frame-1)
            "@frame",
            "D=M",
            "A=D-1",
            "D=M",
            "@THAT",
            "M=D",
            # THIS = *(frame-2)
            *_restore_previous_stack(2, "THIS"),
            # ARG = *(frame-3)
            *_restore_previous_stack(3, "ARG"),
            # LCL = *(frame-4)
            *_restore_previous_stack(4, "LCL"),
            # goto retAddr
            f"// GOTO retAddr",
            "@retAddr",
            "A=M",
            "0;JMP",
        ])
        
    def set_file_name(self, filename: str):
        """ 
        Informs that the translation of a new VM file has started (called by the VMTranslator).
        """
        self._file_name = filename

    def write_call(self, function_name: str, n_args: int):
        """
        Writes assembly code that effects the call command
        """

        def _save_caller(segment: str):
            self._generate_asm([
                f"@{segment}",
                "D=M",
            ])
            self._write_push_to_stack()
             
        # Comment 
        self._generate_asm([
            f"// CALL FUNCTION {function_name} WITH {n_args} ARGUMENTS",
        ])

        # push returnAddress (generates a label and pushes it to the stack)
        # init the call counter, or update +1
        if function_name in self._call_function_counter:
            self._call_function_counter[function_name] += 1
        else:
            self._call_function_counter[function_name] = 0

        ret_function_name = f"{function_name}$ret{self._call_function_counter[function_name]}"

        # push returnAddress (generates a label and puses it to the stack) 
        self._generate_asm([
            f"@{ret_function_name}",
            "D=A",
        ])
        self._write_push_to_stack()
        # push LCL
        _save_caller("LCL")
        # push ARG
        _save_caller("ARG")
        # push THIS
        _save_caller("THIS")
        # push THAT
        _save_caller("THAT")
        # ARG = SP-5-nArgs (repositions ARGS)
        self._generate_asm([
            "@SP",
            "D=M",
            f"@{n_args}",
            "D=D-A",
            "@5",
            "D=D-A",
            "@ARG",
            "M=D",
        ])
        # LCL = SP (repositions LCL)
        self._generate_asm([
            "@SP",
            "D=M",
            "@LCL",
            "M=D",
        ])
        # goto f (transfers control to the callee)
        self._generate_asm([
            f"@{function_name}",
            "0;JMP",
        ])
        # (returnAddress) Injects the return address label into the code
        self._generate_asm([
            f"({ret_function_name})",
        ])

    def bootstrap(self):
        """
        Prepare the code:
            - SP = 256
            call Sys.init
        """  
        # Comment
        self._generate_asm([
            "// BOOSTRAP!",
        ])
        # SP = 256 
        self._generate_asm([
            "@256",
            "D=A",
            "@SP",
            "M=D",
        ])
        # call Sys.init
        self.write_call("Sys.init", 0)

    def finish_him(self):
        """
        Gracefully terminates the execution flow, avoiding infinite execution
            - (FINISH)
            - @FINISH
            - 0;JMP
        """  
        # Comment
        self._generate_asm([
            "// FINISH HIM!",
        ])
        # Code
        self._generate_asm([
            "(FINISH)",
            "@FINISH",
            "0;JMP",
        ])
# debug
if __name__ == "__main__":
    code_writer = CodeWriter("prueba")
    code_writer.write_arithmetic("eq")
