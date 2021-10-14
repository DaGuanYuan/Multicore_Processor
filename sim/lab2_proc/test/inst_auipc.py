#=========================================================================
# auipc
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    auipc x1, 0x00010                       # PC=0x200
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw  proc2mngr, x1 > 0x00010200
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
    gen_imm_dest_dep_test( 5, "auipc", 0x00000fff, 0x00fff200),
    gen_imm_dest_dep_test( 4, "auipc", 0x000000ff, 0x000ff21c),
    gen_imm_dest_dep_test( 3, "auipc", 0x00000f0f, 0x00f0f234),
    gen_imm_dest_dep_test( 2, "auipc", 0x000ff0f0, 0xff0f0248),
    gen_imm_dest_dep_test( 1, "auipc", 0x00000f0f, 0x00f0f258),
    gen_imm_dest_dep_test( 0, "auipc", 0x000f0ff0, 0xf0ff0264),
  ]

def gen_value_test():
  return [
    gen_imm_value_test( "auipc", 0x00000fff, 0x00fff200),
    gen_imm_value_test( "auipc", 0x000000ff, 0x000ff208),
    gen_imm_value_test( "auipc", 0x00000f0f, 0x00f0f210),
    gen_imm_value_test( "auipc", 0x000ff0f0, 0xff0f0218),
    gen_imm_value_test( "auipc", 0x00000f0f, 0x00f0f220),
    gen_imm_value_test( "auipc", 0x000f0ff0, 0xf0ff0228),
  ]

def gen_random_test():
  asm_code = []
  PCCount = 0
  for i in xrange(100):
    imm  = Bits( 32, random.randint(0,0x000fffff) )
    dest = Bits( 32, (imm << 12) + PCCount + 0x200, trunc=True)
    asm_code.append( gen_imm_value_test("auipc", imm.int(), dest.int() ) )
    PCCount += 2 * 4
  return asm_code