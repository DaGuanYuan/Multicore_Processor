#=========================================================================
# Integrated test
#=========================================================================

import random

from pymtl import *
from inst_utils import *

def gen_integ_test_mz588():
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

def gen_integ_test_estimating_execution_time():
  return """

    # initialization
    csrr x13, mngr2proc < 0x00002000  # src1 address
    csrr x14, mngr2proc < 0x00002004  # src2 address
    csrr x12, mngr2proc < 0x00003000  # dest address
    csrr x15, mngr2proc < 64          # iteration 64 times
    csrr x16, mngr2proc < 0x00003000  # address for verification
    csrr x17, mngr2proc < 0x00003004  # address for verification
    csrr x18, mngr2proc < 0x00003008  # address for verification
    csrr x19, mngr2proc < 0x0000300c  # address for verification

    # getting into the loop
  loop:
    lw    x5,  0(x13)
    lw    x6,  0(x14)
    add   x7,  x5,  x6
    sw    x7,  0(x12)
    addi  x13, x13,  4
    addi  x14, x14,  4
    addi  x12, x12,  4
    addi  x15, x15, -1
    bne   x15, x0,  loop

    # check the addresses and the counter
    csrw proc2mngr, x13 > 0x00002100
    csrw proc2mngr, x14 > 0x00002104
    csrw proc2mngr, x12 > 0x00003100
    csrw proc2mngr, x15 > 0

    # check the destination array
    lw    x1,  0(x16)
    csrw proc2mngr, x1  > 0x00010001
    lw    x1,  0(x17)
    csrw proc2mngr, x1  > 0x00000001
    lw    x1,  0(x18)
    csrw proc2mngr, x1  > 0x00000000
    lw    x1,  0(x19)
    csrw proc2mngr, x1  > 0x00000000

    .data

    # src array
    .word 0x00010000
    .word 0x00000001
  """

def gen_integ_test_3_regs_raw_data_hazards():
  return """
    csrr x1, mngr2proc < 0
    csrr x2, mngr2proc < 1
    csrr x3, mngr2proc < 2

    addi  x1, x0, 1       # x1 = 1
    ori   x2, x1, 2       # x2 = 3
    andi  x3, x2, 3       # x3 = 3
    xori  x1, x3, 4       # x1 = 7
    slti  x2, x1, 10      # x2 = 1
    srai  x3, x2, 0       # x3 = 1
    srli  x1, x3, 0       # x1 = 1
    slli  x2, x1, 1       # x2 = 2

    csrw proc2mngr, x1  > 1
    csrw proc2mngr, x2  > 2
    csrw proc2mngr, x3  > 1
    
  """

def gen_integ_test_2_regs_raw_data_hazards():
  return """
    csrr x1, mngr2proc < 0
    csrr x2, mngr2proc < 1

    addi  x1, x0, 1       # x1 = 1
    ori   x2, x1, 2       # x2 = 3
    andi  x1, x2, 3       # x1 = 3
    xori  x2, x1, 4       # x2 = 7
    slti  x1, x2, 10      # x1 = 1
    srai  x2, x1, 0       # x2 = 1
    srli  x1, x2, 0       # x1 = 1
    slli  x2, x1, 1       # x2 = 2

    csrw proc2mngr, x1  > 1
    csrw proc2mngr, x2  > 2
    
  """

def gen_integ_test_branch_over_jumps():
  return """
    csrr  x1, mngr2proc < 1
    csrr  x2, mngr2proc < 0

    bne   x1, x0, F1       # branch should have higher priority than jump
    jal   x1, F2           # x1 should be squashed
    nop
    nop
    nop

  F2:
    addi  x2, x2, 0x01

  F1:
    addi  x2, x2, 0x10

    csrw  proc2mngr, x1 > 1
    csrw  proc2mngr, x2 > 0x10
    
  """