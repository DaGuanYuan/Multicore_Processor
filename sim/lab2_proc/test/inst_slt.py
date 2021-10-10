#=========================================================================
# slt
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
    slt x3, x1, x2
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
    gen_rr_dest_dep_test( 5, "slt", 9, 8, 0),
    gen_rr_dest_dep_test( 4, "slt", -10, 3, 1),
    gen_rr_dest_dep_test( 3, "slt", 10, 6, 0),
    gen_rr_dest_dep_test( 2, "slt", -8, 4, 1),
    gen_rr_dest_dep_test( 1, "slt", -1, 10, 1),
    gen_rr_dest_dep_test( 0, "slt", -6, 4, 1),
  ]


def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "slt", -7, -3, 1),
    gen_rr_src0_dep_test( 4, "slt", 4, -6, 0),
    gen_rr_src0_dep_test( 3, "slt", 10, 10, 0),
    gen_rr_src0_dep_test( 2, "slt", -7, 1, 1),
    gen_rr_src0_dep_test( 1, "slt", -4, 4, 1),
    gen_rr_src0_dep_test( 0, "slt", 8, 1, 0),
  ]


def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "slt", 4, 2, 0),
    gen_rr_src1_dep_test( 4, "slt", 0, 3, 1),
    gen_rr_src1_dep_test( 3, "slt", 5, -6, 0),
    gen_rr_src1_dep_test( 2, "slt", -1, 3, 1),
    gen_rr_src1_dep_test( 1, "slt", 1, -9, 0),
    gen_rr_src1_dep_test( 0, "slt", 4, -3, 0),
  ]


def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "slt", 2, -9, 0),
    gen_rr_srcs_dep_test( 4, "slt", 3, -4, 0),
    gen_rr_srcs_dep_test( 3, "slt", -10, -9, 1),
    gen_rr_srcs_dep_test( 2, "slt", 0, 6, 1),
    gen_rr_srcs_dep_test( 1, "slt", -5, -3, 1),
    gen_rr_srcs_dep_test( 0, "slt", -8, -6, 1),
  ]


def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "slt", 3, 1, 0),
    gen_rr_src1_eq_dest_test( "slt", -5, -2, 1),
    gen_rr_src0_eq_src1_test( "slt", -6, 0),
    gen_rr_srcs_eq_dest_test( "slt", 0, 0),
  ]

def gen_value_test():
  return [
    gen_rr_value_test( "slt", 0x00000000, 0x00000000, 0x00000000),
    gen_rr_value_test( "slt", 0x00000001, 0x00000001, 0x00000000),
    gen_rr_value_test( "slt", 0x00000003, 0x00000001, 0x00000000),
    gen_rr_value_test( "slt", 0x00000000, 0xffff8000, 0x00000000),
    gen_rr_value_test( "slt", 0x80000000, 0x00000000, 0x00000001),
    gen_rr_value_test( "slt", 0x80000000, 0xffff8000, 0x00000001),
    gen_rr_value_test( "slt", 0x80000000, 0xffff8000, 0x00000001),
    gen_rr_value_test( "slt", 0x00000000, 0x00007fff, 0x00000001),
    gen_rr_value_test( "slt", 0x7fffffff, 0x00ffff00, 0x00000000),
    gen_rr_value_test( "slt", 0x7fffffff, 0x00007fff, 0x00000000),
    gen_rr_value_test( "slt", 0x80000000, 0x00007fff, 0x00000001),
    gen_rr_value_test( "slt", 0x7fffffff, 0xffff8000, 0x00000000),
  ]

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(-1 * (1 << 31), (1 << 31) - 1))
    src1 = Bits( 32, random.randint(-1 * (1 << 31), (1 << 31) - 1))
    dest = Bits( 32, src0.int() < src1.int(), trunc=True)
    asm_code.append( gen_rr_value_test( "slt", src0.int(), src1.int(), dest.int() ) )
  return asm_code
   