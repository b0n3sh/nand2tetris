// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.

// Pseudocode
// i=0;
// res=0;
// (MULT)
//     if(i=R1) goto SAVE;
//     res=res+R0;
//     i++;
//     JMP MULT;
// (SAVE)
//     R2=res
// (END)
//     JMP END;

    // i=0.
    @i
    M=0
    // res=0.
    @res
    M=0
(MULT)
    // if(i=R1) goto SAVE.
    @R1
    D=M
    @i
    D=D-M
    @SAVE
    D;JEQ
    // res=res+R0
    @R0
    D=M
    @res
    M=M+D
    // i++
    @i
    M=M+1
    // JMP MULT
    @MULT
    0;JMP
(SAVE)    
    // R2=res
    @res
    D=M
    @R2
    M=D
(END)
    @END
    0;JMP
