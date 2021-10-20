import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    # Send value 0x00002000 from test source into processor
    csrr x2, mngr2proc < 0x00002000
    csrr x4, mngr2proc < 0x00002010

    # store the addr value
    addi x5, x4, 0

    # loop over four elements in array
    addi x1, x0, 4
    loop:
    lw x3, 0(x2)
    addi x3, x3, 1
    sw x3, 0(x4)
    addi x2, x2, 4
    addi x4, x4, 4
    addi x1, x1, -1
    bne x1, x0, loop

    # Read out the four results and send to test sink for verification

    lw x3, 0(x5)
    csrw proc2mngr, x3 > 2

    addi x5, x5, 0x4
    lw x3, 0(x5)
    csrw proc2mngr, x3 > 3

    addi x5, x5, 0x4
    lw x3, 0(x5)
    csrw proc2mngr, x3 > 4

    addi x5, x5, 0x4
    lw x3, 0(x5)
    csrw proc2mngr, x3 > 5

    # Data section
    .data

    # src array
    .word 0x00000001
    .word 0x00000002
    .word 0x00000003
    .word 0x00000004

    # dest array
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
  """

#-------------------------------------------------------------------------
# test for covering all instructions
#-------------------------------------------------------------------------

def gen_alg1_test():
  return """
    csrr x1,  mngr2proc < 0x00002000  # load the address of the array into x1
    csrr x10, mngr2proc < 0x00002010 # load the address of the array into x1
    addi x2, x0, 0x00000004         # put the size of the array in x2
    addi x3, x0, 0                  # set the length counter
    jal x0, loop                    # start the loop
  func:
    addi x5, x5, -1
    jalr x0, x7, 0
  loop:
    slli x12, x3, 2
    add x4, x12, x1
    add x11, x12, x10
    lw x5, 0(x4)
    sw x5, 0(x4)
    andi x6, x5, 1
    auipc x7, 0
    addi x7, x7, 0x14
    bne x6, x0, func
    addi x8, x0, 2
    mul x5, x5, x8
    sw x5, 0(x11)
    addi x3, x3, 1
    blt x3, x2, loop
    
    addi x10, x10, 0
    lw  x2, 0(x10)
    csrw proc2mngr, x2 > 0
    addi x10, x10, 4
    lw  x2, 0(x10)
    csrw proc2mngr, x2 > 8
    addi x10, x10, 4
    lw  x2, 0(x10)
    csrw proc2mngr, x2 > 4
    addi x10, x10, 4
    lw  x2, 0(x10)
    csrw proc2mngr, x2 > 8
    # data section
    .data
    # src array
    .word 0x00000001
    .word 0x00000004
    .word 0x00000005
    .word 0x00000009
    # dest array
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
  """

# algorithm : given array of length 5, convert all of them to multiple of 4
# if number is negative, get absolute value
def gen_alg2_test():
  return """
    # load address of src array and dest array 
    csrr  x1, mngr2proc < 0x00002000 
    csrr  x2, mngr2proc < 0x00002014  
    xor   x12, x12, x12     # set x12 to 0
    add   x12, x12, x2      # set x12 to start address of dest array
     
    # initialize data 
    ori   x5, x0, 0xfff     # set x5 to value -1
    ori   x6, x0, 0x1       # set x6 to value 1
    slli  x7, x6, 0x2       # left shift 2 bits to get x7 == 4  
    andi  x4, x4, 0x0       # set x4 to 0    
    or    x4, x0, x7        # set x4 to value 4, 

    csrw  proc2mngr, x4 > 0x4
    csrw  proc2mngr, x5 > 0xffffffff
    csrw  proc2mngr, x6 > 0x1

    # begin loop
    loop:
    lw    x7, 0(x1)         # get data from src array
    xor   x8, x8, x8        # set x8 to 0
    slt   x8, x7, x0        # if data is less than 0, set x8
    beq   x8, x6, func      # if x8 == 1, this is negative, jump to func

    label_a:
    sra   x7, x7, x6        # right shift 
    srai  x7, x7, 0x1       # right shift 
    sll   x7, x7, x6        # left shift   
    slli  x7, x7, 0x1       # left shift  
    lw    x9, 0(x2)         # get original value from dest array
    add   x7, x7, x9        # add
    sw    x7, 0(x2)         # store final value into dest array

    addi  x1, x1, 0x4       # move pointer
    addi  x2, x2, 0x4       # move pointer

    sub   x4, x4, x6        # subtract 1 from x4
    bge   x4, x0, loop      # if x4 >= 0, jump to loop
    jal   x10, end          # if x4 < 0, jump to end
    
    func:
    mul   x7, x7, x5        # get abs by muliplying -1
    jal   x10, label_a      # jump back


    # verify the final data
    end:
    lw    x2, 0(x12)
    csrw proc2mngr, x2 > 0x2

    addi  x12, x12, 0x4
    lw    x2, 0(x12)
    csrw proc2mngr, x2 > 0x8

    addi  x12, x12, 0x4
    lw    x2, 0(x12)
    csrw proc2mngr, x2 > 0x4
 
    addi  x12, x12, 0x4
    lw    x2, 0(x12)
    csrw proc2mngr, x2 > 0x10

    addi  x12, x12, 0x4
    lw    x2, 0(x12)
    csrw proc2mngr, x2 > 0x00110000

    .data
    # src array
    .word 0xffffffff
    .word 0x0000000a
    .word 0x00000005
    .word 0x00000010
    .word 0x00110000
    
    # dest array
    .word 0x00000002
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000
    .word 0x00000000

  """

# same algorithm with different strategy
def gen_alg3_test():
  return """
    # load address of src array and dest array 
    csrr  x1, mngr2proc < 0x00002000 
    csrr  x2, mngr2proc < 0x00002014  
    xor   x12, x12, x12     # set x12 to 0
    add   x12, x12, x2      # set x12 to start address of dest array
     
    # initialize data 
    ori   x5, x0, 0xfff     # set x5 to value -1
    ori   x6, x0, 0x1       # set x6 to value 1
    slli  x7, x6, 0x2       # left shift 2 bits to get x7 == 4  
    srli  x4, x4, 0x1f      # set x4 to 0
    srl   x4, x4, x6    
    or    x4, x0, x7        # set x4 to value 4, 
    addi  x4, x4, 0x1

    csrw  proc2mngr, x4 > 0x5
    csrw  proc2mngr, x5 > 0xffffffff
    csrw  proc2mngr, x6 > 0x1

    # begin loop
    loop:
    lw    x7, 0(x1)         # get data from src array
    xor   x8, x8, x8        # set x8 to 0
    slti  x8, x7, 0x0        # if data is less than 0, set x8
    beq   x8, x6, func      # if x8 == 1, this is negative, jump to func

    label_a:
    sra   x7, x7, x6        # right shift 
    srai  x7, x7, 0x1       # right shift 
    sll   x7, x7, x6        # left shift   
    slli  x7, x7, 0x1       # left shift  
    sw    x7, 0(x2)         # store final value into dest array

    addi  x1, x1, 0x4       # move pointer
    addi  x2, x2, 0x4       # move pointer

    sub   x4, x4, x6        # subtract 1 from x4
    bgeu  x4, x6, loop      # if x4 >= 1, jump to loop
    jal   x10, end          # if x4 < 0, jump to end
    
    func:
    lui   x11, 0x80000      # set the highest number to 1
    srai  x11, x11, 0x1f    # right shift 32 bits to get -1
    mul   x7, x7, x11       # get abs by muliplying -1

    lw    x9, 0(x2)         # get original value from dest array
    bltu  x7, x9, label_a   # if less than value of dest array, jump back
    andi  x7, x7, 0x0       # else get value from dest array
    add   x7, x7, x9        
    jal   x10, label_a      # jump back


    # verify the final data
    end:
    lw    x2, 0(x12)
    csrw proc2mngr, x2 > 0xaa0

    addi  x12, x12, 0x4
    lw    x2, 0(x12)
    csrw proc2mngr, x2 > 0x0

    addi  x12, x12, 0x4
    lw    x2, 0(x12)
    csrw proc2mngr, x2 > 0x54
 
    addi  x12, x12, 0x4
    lw    x2, 0(x12)
    csrw proc2mngr, x2 > 0x10

    addi  x12, x12, 0x4
    lw    x2, 0(x12)
    csrw proc2mngr, x2 > 0x00110000

    .data
    # src array
    .word 0x00000aa1
    .word 0xffffffff
    .word 0xfffff003
    .word 0x00000010
    .word 0x00110000
    
    # dest array
    .word 0x000000b0
    .word 0x00000002
    .word 0x00000055
    .word 0x00000100
    .word 0x01100000

  """


#-------------------------------------------------------------------------
# test for triggering instruction hazard
#-------------------------------------------------------------------------