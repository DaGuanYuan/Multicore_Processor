#=========================================================================
# lui
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    lui x1, 0x0001
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x1 > 0x00001000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

# ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define additional directed and random test cases.
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


# testStartFlag


def gen_dest_dep_test():
  return [
    gen_imm_dest_dep_test( 5, "lui", 0x00000f00, 0x00f00000),
    gen_imm_dest_dep_test( 4, "lui", 0x000fff00, 0xfff00000),
    gen_imm_dest_dep_test( 3, "lui", 0x00000000, 0x00000000),
    gen_imm_dest_dep_test( 2, "lui", 0x000fffff, 0xfffff000),
    gen_imm_dest_dep_test( 1, "lui", 0x00000000, 0x00000000),
    gen_imm_dest_dep_test( 0, "lui", 0x0000fff0, 0x0fff0000),
  ]

def gen_value_test():
  return [
    gen_imm_value_test( "lui", 0x00000f00, 0x00f00000),
    gen_imm_value_test( "lui", 0x000fff00, 0xfff00000),
    gen_imm_value_test( "lui", 0x00000000, 0x00000000),
    gen_imm_value_test( "lui", 0x000fffff, 0xfffff000),
    gen_imm_value_test( "lui", 0x00000000, 0x00000000),
    gen_imm_value_test( "lui", 0x0000fff0, 0x0fff0000),
  ]

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    imm  = Bits( 32, random.randint(0,0x000fffff) )
    dest = Bits( 32, (imm << 12), trunc=True)
    asm_code.append( gen_imm_value_test("lui", imm.int(), dest.int() ) )
  return asm_code