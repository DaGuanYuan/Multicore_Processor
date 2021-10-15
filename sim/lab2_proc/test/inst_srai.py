#=========================================================================
# srai
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 0x00008000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    srai x3, x1, 0x03
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x00001000
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
    gen_rimm_dest_dep_test( 5, "srai", 0x00000f0f, 0x01e, 0x00000000),
    gen_rimm_dest_dep_test( 4, "srai", 0x0000f0f0, 0x01d, 0x00000000),
    gen_rimm_dest_dep_test( 3, "srai", 0x00000f0f, 0x01d, 0x00000000),
    gen_rimm_dest_dep_test( 2, "srai", 0x0000f0f0, 0x00c, 0x0000000f),
    gen_rimm_dest_dep_test( 1, "srai", 0x00000f0f, 0x016, 0x00000000),
    gen_rimm_dest_dep_test( 0, "srai", 0x0000f0f0, 0x019, 0x00000000),
  ]


def gen_src_dep_test():
  return [
    gen_rimm_src_dep_test( 5, "srai", 0x00000f0f, 0x011, 0x00000000),
    gen_rimm_src_dep_test( 4, "srai", 0x0000f0f0, 0x018, 0x00000000),
    gen_rimm_src_dep_test( 3, "srai", 0x00000f0f, 0x00f, 0x00000000),
    gen_rimm_src_dep_test( 2, "srai", 0x0000f0f0, 0x001, 0x00007878),
    gen_rimm_src_dep_test( 1, "srai", 0x00000f0f, 0x007, 0x0000001e),
    gen_rimm_src_dep_test( 0, "srai", 0x0000f0f0, 0x00f, 0x00000001),
  ]


def gen_srcs_dest_test():
    return [
        gen_rimm_src_eq_dest_test( "srai", 0x00000f0f, 0x000, 0x00000f0f ),
    ]

def gen_value_test():
  return [
    gen_rimm_value_test( "srai", 0xff00ff00, 0x000, 0xff00ff00),
    gen_rimm_value_test( "srai", 0x0ff00ff0, 0x013, 0x000001fe),
    gen_rimm_value_test( "srai", 0x00ff00ff, 0x01c, 0x00000000),
    gen_rimm_value_test( "srai", 0xf00ff00f, 0x013, 0xfffffe01),
  ]

def gen_random_test():
    asm_code = []
    for i in xrange(100):
        # from 0 to 0xffffffff, signed or unsigned is decided by the interpretation of signed bit
        src  = Bits( 32, random.randint(0,0xffffffff))
        imm  = Bits( 5, random.randint(0,0x0000001f))
        dest = Bits( 32, src.int() >> imm.uint(), trunc=True)
        asm_code.append( gen_rimm_value_test( "srai", src.int(), imm.uint(), dest.int() ) )
    return asm_code