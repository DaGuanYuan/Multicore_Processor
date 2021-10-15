#=========================================================================
# sltu
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 4
    csrr x2, mngr2proc < 5
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sltu x3, x1, x2
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
def gen_dest_dep_test():
  return [
    gen_rr_dest_dep_test( 5, "sltu", 5, 6, 1),
    gen_rr_dest_dep_test( 4, "sltu", 8, 10, 1),
    gen_rr_dest_dep_test( 3, "sltu", 5, 0, 0),
    gen_rr_dest_dep_test( 2, "sltu", 3, 1, 0),
    gen_rr_dest_dep_test( 1, "sltu", 10, 8, 0),
    gen_rr_dest_dep_test( 0, "sltu", 1, 5, 1),
  ]


def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "sltu", 2, 2, 0),
    gen_rr_src0_dep_test( 4, "sltu", 1, 8, 1),
    gen_rr_src0_dep_test( 3, "sltu", 7, 9, 1),
    gen_rr_src0_dep_test( 2, "sltu", 2, 5, 1),
    gen_rr_src0_dep_test( 1, "sltu", 3, 2, 0),
    gen_rr_src0_dep_test( 0, "sltu", 0, 0, 0),
  ]


def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "sltu", 4, 10, 1),
    gen_rr_src1_dep_test( 4, "sltu", 1, 4, 1),
    gen_rr_src1_dep_test( 3, "sltu", 0, 1, 1),
    gen_rr_src1_dep_test( 2, "sltu", 5, 1, 0),
    gen_rr_src1_dep_test( 1, "sltu", 3, 9, 1),
    gen_rr_src1_dep_test( 0, "sltu", 0, 7, 1),
  ]


def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "sltu", 9, 7, 0),
    gen_rr_srcs_dep_test( 4, "sltu", 0, 1, 1),
    gen_rr_srcs_dep_test( 3, "sltu", 0, 0, 0),
    gen_rr_srcs_dep_test( 2, "sltu", 2, 6, 1),
    gen_rr_srcs_dep_test( 1, "sltu", 10, 2, 0),
    gen_rr_srcs_dep_test( 0, "sltu", 9, 4, 0),
  ]


def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "sltu", 4, 4, 0),
    gen_rr_src1_eq_dest_test( "sltu", 7, 5, 0),
    gen_rr_src0_eq_src1_test( "sltu", 8, 0),
    gen_rr_srcs_eq_dest_test( "sltu", 0, 0),
  ]

def gen_value_test():
  return [
    gen_rr_value_test( "sltu", 0x00000000, 0x00000000, 0x00000000),
    gen_rr_value_test( "sltu", 0x00000001, 0x00000001, 0x00000000),
    gen_rr_value_test( "sltu", 0x00000003, 0x00000001, 0x00000000),
    gen_rr_value_test( "sltu", 0x00000000, 0xffff8000, 0x00000001),
    gen_rr_value_test( "sltu", 0x80000000, 0x00000000, 0x00000000),
    gen_rr_value_test( "sltu", 0x80000000, 0xffff8000, 0x00000001),
    gen_rr_value_test( "sltu", 0x80000000, 0xffff8000, 0x00000001),
    gen_rr_value_test( "sltu", 0x00000000, 0x00007fff, 0x00000001),
    gen_rr_value_test( "sltu", 0x7fffffff, 0x00ffff00, 0x00000000),
    gen_rr_value_test( "sltu", 0x7fffffff, 0x00007fff, 0x00000000),
    gen_rr_value_test( "sltu", 0x80000000, 0x00007fff, 0x00000000),
    gen_rr_value_test( "sltu", 0x7fffffff, 0xffff8000, 0x00000001),
  ]

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(-1 * (1 << 31), (1 << 31) - 1))
    src1 = Bits( 32, random.randint(-1 * (1 << 31), (1 << 31) - 1))
    dest = Bits( 32, src0.uint() < src1.uint(), trunc=True)
    asm_code.append( gen_rr_value_test( "sltu", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code
   
