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
    andi x6, x5, 1
    auipc x7, 0
    addi x7, x7, 0x14
    bne x6, x0, func
    addi x8, x0, 2
    mul x5, x5, x8
    sw x5, 0(x11)

    addi x3, x3, 1
    blt x3, x2, loop

    # data section
    csrr x1, mngr2proc < 0x00002010 # load the address of the array into x1
    addi x1, x1, 0
    lw  x2, 0(x1)
    csrw proc2mngr, x2 > 0

    csrr x1, mngr2proc < 0x00002010 # load the address of the array into x1
    addi x1, x1, 4
    lw  x2, 0(x1)
    csrw proc2mngr, x2 > 8

    csrr x1, mngr2proc < 0x00002010 # load the address of the array into x1
    addi x1, x1, 8
    lw  x2, 0(x1)
    csrw proc2mngr, x2 > 4

    csrr x1, mngr2proc < 0x00002010 # load the address of the array into x1
    addi x1, x1, 0xc
    lw  x2, 0(x1)
    csrw proc2mngr, x2 > 8

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