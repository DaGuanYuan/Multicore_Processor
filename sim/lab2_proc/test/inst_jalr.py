#=========================================================================
# jalr
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """

    # Use r3 to track the control flow pattern
    addi  x3, x0, 0           # 0x0200
                              #
    lui x1,      %hi[label_a] # 0x0204
    addi x1, x1, %lo[label_a] # 0x0208
                              #
    nop                       # 0x020c
    nop                       # 0x0210
    nop                       # 0x0214
    nop                       # 0x0218
    nop                       # 0x021c
    nop                       # 0x0220
    nop                       # 0x0224
    nop                       # 0x0228
                              #
    jalr  x31, x1, 0          # 0x022c
    addi  x3, x3, 0b01        # 0x0230

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

  label_a:
    addi  x3, x3, 0b10

    # Check the link address
    csrw  proc2mngr, x31 > 0x0230

    # Only the second bit should be set if jump was taken
    csrw  proc2mngr, x3  > 0b10

  """

# ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define additional directed and random test cases.
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
def gen_lsb_test():
  return [
    gen_jalr_lsb_test("jalr", 0),
    gen_jalr_lsb_test("jalr", 1),
  ]


def gen_one_jump_test():
  return [
    gen_jalr_simple_test(),
    gen_jalr_simple_test(),
    gen_jalr_simple_test(),
    gen_jalr_simple_test(),
    gen_jalr_simple_test(),
    gen_jalr_simple_test(),
  ]

def gen_seq_test():
  return [
    gen_jalr_value_test("jalr", 0),
    gen_jalr_value_test("jalr", 24),
    gen_jalr_value_test("jalr", 48),
    gen_jalr_value_test("jalr", 72),
    gen_jalr_value_test("jalr", 80),
  ]


def gen_random_test():
  asm_code = []
  for i in xrange(9):
    imm = random.randint(0, 1)
    asm_code.append( gen_jalr_value_test("jalr", imm) )
  return asm_code