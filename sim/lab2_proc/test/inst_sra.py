#=========================================================================
# sra
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
    csrr x2, mngr2proc < 0x00000003
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sra x3, x1, x2
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

def gen_dest_dep_test():
  return [
    gen_rr_dest_dep_test( 5, "sra", 7, 2, 1),
    gen_rr_dest_dep_test( 4, "sra", 3, 0, 3),
    gen_rr_dest_dep_test( 3, "sra", 7, 6, 0),
    gen_rr_dest_dep_test( 2, "sra", 4, 10, 0),
    gen_rr_dest_dep_test( 1, "sra", 8, 10, 0),
    gen_rr_dest_dep_test( 0, "sra", 1, 1, 0),
  ]


def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "sra", 0, 6, 0),
    gen_rr_src0_dep_test( 4, "sra", 3, 8, 0),
    gen_rr_src0_dep_test( 3, "sra", 6, 9, 0),
    gen_rr_src0_dep_test( 2, "sra", 7, 8, 0),
    gen_rr_src0_dep_test( 1, "sra", 6, 7, 0),
    gen_rr_src0_dep_test( 0, "sra", 3, 9, 0),
  ]


def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "sra", 1, 9, 0),
    gen_rr_src1_dep_test( 4, "sra", 7, 10, 0),
    gen_rr_src1_dep_test( 3, "sra", 3, 10, 0),
    gen_rr_src1_dep_test( 2, "sra", 2, 3, 0),
    gen_rr_src1_dep_test( 1, "sra", 2, 7, 0),
    gen_rr_src1_dep_test( 0, "sra", 7, 0, 7),
  ]


def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "sra", 1, 2, 0),
    gen_rr_srcs_dep_test( 4, "sra", 1, 7, 0),
    gen_rr_srcs_dep_test( 3, "sra", 2, 7, 0),
    gen_rr_srcs_dep_test( 2, "sra", 1, 9, 0),
    gen_rr_srcs_dep_test( 1, "sra", 4, 3, 0),
    gen_rr_srcs_dep_test( 0, "sra", 0, 2, 0),
  ]


def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "sra", 1, 2, 0),
    gen_rr_src1_eq_dest_test( "sra", 4, 7, 0),
    gen_rr_src0_eq_src1_test( "sra", 6, 0),
    gen_rr_srcs_eq_dest_test( "sra", 9, 0),
  ]

def gen_value_test():
  return [
    gen_rr_value_test( "sra", 0x00000000, 0x00000000, 0x00000000),
    gen_rr_value_test( "sra", 0x00000001, 0x00000001, 0x00000000),
    gen_rr_value_test( "sra", 0x00000003, 0x00000001, 0x00000001),
    gen_rr_value_test( "sra", 0x00000000, 0xffff8000, 0x00000000),
    gen_rr_value_test( "sra", 0x80000000, 0x00000000, 0x80000000),
    gen_rr_value_test( "sra", 0x80000000, 0xffff8000, 0x80000000),
    gen_rr_value_test( "sra", 0x80000000, 0xffff8000, 0x80000000),
    gen_rr_value_test( "sra", 0x00000000, 0x00007fff, 0x00000000),
    gen_rr_value_test( "sra", 0x7fffffff, 0x00ffff00, 0x7fffffff),
    gen_rr_value_test( "sra", 0x7fffffff, 0x00007fff, 0x00000000),
    gen_rr_value_test( "sra", 0x80000000, 0x00007fff, 0xffffffff),
    gen_rr_value_test( "sra", 0x7fffffff, 0xffff8000, 0x7fffffff),
  ]

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(-1 * (1 << 31), (1 << 31) - 1))
    src1 = Bits( 32, random.randint(-1 * (1 << 31), (1 << 31) - 1))
    dest = Bits( 32, src0.int() >> (src1.uint() & 0x1F) , trunc=True)
    asm_code.append( gen_rr_value_test( "sra", src0.int(), src1.int(), dest.int() ) )
  return asm_code
   