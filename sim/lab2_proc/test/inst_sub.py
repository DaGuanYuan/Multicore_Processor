#=========================================================================
# sub
#=========================================================================

from math import trunc
import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 5
    csrr x2, mngr2proc < 4
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sub x3, x1, x2
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

def gen_dest_dep_test():
  return [
    gen_rr_dest_dep_test( 5, "sub", 7, -6, 13),
    gen_rr_dest_dep_test( 4, "sub", 3, -9, 12),
    gen_rr_dest_dep_test( 3, "sub", -10, -4, -6),
    gen_rr_dest_dep_test( 2, "sub", -3, 1, -4),
    gen_rr_dest_dep_test( 1, "sub", 1, 10, -9),
    gen_rr_dest_dep_test( 0, "sub", -7, 3, -10),
  ]


def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "sub", -4, -9, 5),
    gen_rr_src0_dep_test( 4, "sub", 1, -3, 4),
    gen_rr_src0_dep_test( 3, "sub", -8, 2, -10),
    gen_rr_src0_dep_test( 2, "sub", 1, -3, 4),
    gen_rr_src0_dep_test( 1, "sub", -5, -1, -4),
    gen_rr_src0_dep_test( 0, "sub", -1, 4, -5),
  ]


def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "sub", -6, 0, -6),
    gen_rr_src1_dep_test( 4, "sub", 1, -10, 11),
    gen_rr_src1_dep_test( 3, "sub", 3, 4, -1),
    gen_rr_src1_dep_test( 2, "sub", -9, -4, -5),
    gen_rr_src1_dep_test( 1, "sub", -9, 6, -15),
    gen_rr_src1_dep_test( 0, "sub", 4, 8, -4),
  ]


def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "sub", 6, -7, 13),
    gen_rr_srcs_dep_test( 4, "sub", -4, -5, 1),
    gen_rr_srcs_dep_test( 3, "sub", 7, -6, 13),
    gen_rr_srcs_dep_test( 2, "sub", 7, 4, 3),
    gen_rr_srcs_dep_test( 1, "sub", -10, -8, -2),
    gen_rr_srcs_dep_test( 0, "sub", -8, 6, -14),
  ]


def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "sub", 3, 7, -4),
    gen_rr_src1_eq_dest_test( "sub", -10, 7, -17),
    gen_rr_src0_eq_src1_test( "sub", -3, 0),
    gen_rr_srcs_eq_dest_test( "sub", 9, 0),
  ]

def gen_value_test():
  return [
    gen_rr_value_test( "sub", 0x00000000, 0x00000000, 0x00000000),
    gen_rr_value_test( "sub", 0x00000001, 0x00000001, 0x00000000),
    gen_rr_value_test( "sub", 0x00000003, 0x00000001, 0x00000002),
    gen_rr_value_test( "sub", 0x00000000, 0xffff8000, 0x00008000),
    gen_rr_value_test( "sub", 0x80000000, 0x00000000, 0x80000000),
    gen_rr_value_test( "sub", 0x80000000, 0xffff8000, 0x80008000),
    gen_rr_value_test( "sub", 0x80000000, 0xffff8000, 0x80008000),
    gen_rr_value_test( "sub", 0x00000000, 0x00007fff, 0xffff8001),
    gen_rr_value_test( "sub", 0x7fffffff, 0x00ffff00, 0x7f0000ff),
    gen_rr_value_test( "sub", 0x7fffffff, 0x00007fff, 0x7fff8000),
    gen_rr_value_test( "sub", 0x80000000, 0x00007fff, 0x7fff8001),
    gen_rr_value_test( "sub", 0x7fffffff, 0xffff8000, 0x80007fff),
  ]

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(-1 * (1 << 31), (1 << 31) - 1))
    src1 = Bits( 32, random.randint(-1 * (1 << 31), (1 << 31) - 1))
    dest = Bits( 32, src0.int() - src1.int(), trunc=True)
    asm_code.append( gen_rr_value_test( "sub", src0.int(), src1.int(), dest.int() ) )
  return asm_code
   


