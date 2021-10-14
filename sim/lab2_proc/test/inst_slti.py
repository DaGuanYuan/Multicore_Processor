#=========================================================================
# slti
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 5
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slti x3, x1, 6
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 1
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
    gen_rimm_dest_dep_test( 5, "slti", 0x00000f0f, 0x0ff, 0x00000000),
    gen_rimm_dest_dep_test( 4, "slti", 0x0000f0f0, 0xff0, 0x00000000),
    gen_rimm_dest_dep_test( 3, "slti", 0x00000f0f, 0xf00, 0x00000000),
    gen_rimm_dest_dep_test( 2, "slti", 0x0000f0f0, 0x00f, 0x00000000),
    gen_rimm_dest_dep_test( 1, "slti", 0x00000f0f, 0xfff, 0x00000000),
    gen_rimm_dest_dep_test( 0, "slti", 0x0000f0f0, 0x0f0, 0x00000000),
  ]


def gen_src_dep_test():
  return [
    gen_rimm_src_dep_test( 5, "slti", 0x00000f0f, 0x0ff, 0x00000000),
    gen_rimm_src_dep_test( 4, "slti", 0x0000f0f0, 0xff0, 0x00000000),
    gen_rimm_src_dep_test( 3, "slti", 0x00000f0f, 0xf00, 0x00000000),
    gen_rimm_src_dep_test( 2, "slti", 0x0000f0f0, 0x00f, 0x00000000),
    gen_rimm_src_dep_test( 1, "slti", 0x00000f0f, 0xfff, 0x00000000),
    gen_rimm_src_dep_test( 0, "slti", 0x0000f0f0, 0x0f0, 0x00000000),
  ]


def gen_srcs_dest_test():
    return [
        gen_rimm_src_eq_dest_test( "slti", 0x00000f0f, 0xf00, 0x00000000 ),
    ]

def gen_value_test():
  return [
    gen_rimm_value_test( "slti", 0xff00ff00, 0xf0f, 0x00000001),
    gen_rimm_value_test( "slti", 0x0ff00ff0, 0x0f0, 0x00000000),
    gen_rimm_value_test( "slti", 0x00ff00ff, 0x0ff, 0x00000000),
    gen_rimm_value_test( "slti", 0xf00ff00f, 0xff0, 0x00000001),
  ]

def gen_random_test():
    asm_code = []
    for i in xrange(100):
        # from 0 to 0xffffffff, signed or unsigned is decided by the interpretation of signed bit
        src  = Bits( 32, random.randint(0,0xffffffff))
        imm  = Bits( 12, random.randint(0,0x00000fff))
        dest = Bits( 32, src.int() < sext(imm,32).int(), trunc=True)
        asm_code.append( gen_rimm_value_test( "slti", src.int(), imm.int(), dest.int() ) )
    return asm_code