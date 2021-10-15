#=========================================================================
# srli
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
    srli x3, x1, 0x03
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
    gen_rimm_dest_dep_test( 5, "srli", 0x00000f0f, 0x014, 0x00000000),
    gen_rimm_dest_dep_test( 4, "srli", 0x0000f0f0, 0x01e, 0x00000000),
    gen_rimm_dest_dep_test( 3, "srli", 0x00000f0f, 0x00d, 0x00000000),
    gen_rimm_dest_dep_test( 2, "srli", 0x0000f0f0, 0x01e, 0x00000000),
    gen_rimm_dest_dep_test( 1, "srli", 0x00000f0f, 0x005, 0x00000078),
    gen_rimm_dest_dep_test( 0, "srli", 0x0000f0f0, 0x00e, 0x00000003),
  ]


def gen_src_dep_test():
  return [
    gen_rimm_src_dep_test( 5, "srli", 0x00000f0f, 0x00f, 0x00000000),
    gen_rimm_src_dep_test( 4, "srli", 0x0000f0f0, 0x003, 0x00001e1e),
    gen_rimm_src_dep_test( 3, "srli", 0x00000f0f, 0x018, 0x00000000),
    gen_rimm_src_dep_test( 2, "srli", 0x0000f0f0, 0x00a, 0x0000003c),
    gen_rimm_src_dep_test( 1, "srli", 0x00000f0f, 0x001, 0x00000787),
    gen_rimm_src_dep_test( 0, "srli", 0x0000f0f0, 0x00b, 0x0000001e),
  ]


def gen_srcs_dest_test():
    return [
        gen_rimm_src_eq_dest_test( "srli", 0x00000f0f, 0x000, 0x00000f0f ),
    ]

def gen_value_test():
  return [
    gen_rimm_value_test( "srli", 0xff00ff00, 0x00f, 0x0001fe01),
    gen_rimm_value_test( "srli", 0x0ff00ff0, 0x012, 0x000003fc),
    gen_rimm_value_test( "srli", 0x00ff00ff, 0x00a, 0x00003fc0),
    gen_rimm_value_test( "srli", 0xf00ff00f, 0x005, 0x07807f80),
  ]

def gen_random_test():
    asm_code = []
    for i in xrange(100):
        # from 0 to 0xffffffff, signed or unsigned is decided by the interpretation of signed bit
        src  = Bits( 32, random.randint(0,0xffffffff))
        imm  = Bits( 5, random.randint(0,0x0000001f))
        dest = Bits( 32, src >> imm.uint(), trunc=True)
        asm_code.append( gen_rimm_value_test( "srli", src.int(), imm.uint(), dest.int() ) )
    return asm_code