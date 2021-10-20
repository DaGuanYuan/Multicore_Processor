#=========================================================================
# jal
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
    addi  x3, x0, 0     # 0x0200
                        #
    nop                 # 0x0204
    nop                 # 0x0208
    nop                 # 0x020c
    nop                 # 0x0210
    nop                 # 0x0214
    nop                 # 0x0218
    nop                 # 0x021c
    nop                 # 0x0220
                        #
    jal   x1, label_a   # 0x0224
    addi  x3, x3, 0b01  # 0x0228

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
    csrw  proc2mngr, x1 > 0x0228 

    # Only the second bit should be set if jump was taken
    csrw  proc2mngr, x3 > 0b10

  """

# ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define additional directed and random test cases.
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def gen_one_jump_test():
  return [
    gen_jal_simple_test(),
    gen_jal_simple_test(),
    gen_jal_simple_test(),
    gen_jal_simple_test(),
    gen_jal_simple_test(),
    gen_jal_simple_test(),
  ]

def gen_seq_test():
  return[
    gen_jal_seq_template(),
    gen_jal_seq_template(),
    gen_jal_seq_template(),
    gen_jal_seq_template(),
    gen_jal_seq_template(),
    gen_jal_seq_template()
  ]

def gen_back_test():
  return[
    gen_jal_back_template(),
    gen_jal_back_template(),
    gen_jal_back_template(),
    gen_jal_back_template(),
    gen_jal_back_template(),
    gen_jal_back_template()
  ]

def gen_seq_and_back_test():
  return [
    gen_jal_test(),
    gen_jal_test(),
    gen_jal_test(),
    gen_jal_test(),
    gen_jal_test(),
    gen_jal_test(),
  ]


def gen_random_test():
  asm_code = []
  for i in xrange(25):
    target = "label_{}".format( random.randint(1, 5) )
    asm_code.append( gen_jal_value_test("jal", target) )
  return asm_code