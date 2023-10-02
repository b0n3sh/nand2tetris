// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

// Pseudocode
// 
// (RESTART)
//     if (KBD == 0) goto WHITE;
//     for (i=0; i<8192; i++):
//         SCREEN[i] = -1;
//         i++;
//     JMP RESTART
// (WHITE)
//     if SCREEN 0 goto START;
//     for (i=0; i<8192; i++):
//         SCREEN[i] = -1;
    
    //screen_size = 8192
    @8192
    D=A
    @screen_size
    M=D
(RESTART)
    // if (KBD == 0) goto WHITE;
    @KBD
    D=M
    @WHITE
    D;JEQ 
    // Paint black.
    @i
    M=0
    // for (i=0; i<8192; i++):
    (LOOPBLACK)
        @screen_size
        D=M
        @i
        D=D-M
        @RESTART
        D;JEQ
        // Paint.
        @i
        D=M
        @SCREEN
        A=A+D
        M=-1
        // i++
        @i
        M=M+1
        // KEEP LOOPING.
        @LOOPBLACK
        0;JMP
(WHITE)
    // if SCREEN[0]=0 goto RESTART;
    @SCREEN
    D=M
    @RESTART
    D;JEQ
    // else, paint white.
    @i
    M=0
    (LOOPWHITE)
        @screen_size
        D=M
        @i
        D=D-M
        @RESTART
        D;JEQ
        // Paint.
        @i
        D=M
        @SCREEN
        A=A+D 
        M=0
        // i++
        @i
        M=M+1
        // KEEP LOOPING.
        @LOOPWHITE
        0;JMP
