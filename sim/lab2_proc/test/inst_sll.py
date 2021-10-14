#=========================================================================
# sll
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 0x80008000
    csrr x2, mngr2proc < 0x00000003
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sll x3, x1, x2
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x00040000
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
    gen_rr_dest_dep_test( 5, "sll", 8, 7, 1024),
    gen_rr_dest_dep_test( 4, "sll", 5, 6, 320),
    gen_rr_dest_dep_test( 3, "sll", 6, 2, 24),
    gen_rr_dest_dep_test( 2, "sll", 4, 2, 16),
    gen_rr_dest_dep_test( 1, "sll", 9, 3, 72),
    gen_rr_dest_dep_test( 0, "sll", 0, 7, 0),
  ]


def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "sll", 10, 1, 20),
    gen_rr_src0_dep_test( 4, "sll", 2, 9, 1024),
    gen_rr_src0_dep_test( 3, "sll", 1, 10, 1024),
    gen_rr_src0_dep_test( 2, "sll", 9, 5, 288),
    gen_rr_src0_dep_test( 1, "sll", 7, 0, 7),
    gen_rr_src0_dep_test( 0, "sll", 2, 10, 2048),
  ]


def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "sll", 6, 6, 384),
    gen_rr_src1_dep_test( 4, "sll", 0, 5, 0),
    gen_rr_src1_dep_test( 3, "sll", 7, 1, 14),
    gen_rr_src1_dep_test( 2, "sll", 6, 0, 6),
    gen_rr_src1_dep_test( 1, "sll", 3, 6, 192),
    gen_rr_src1_dep_test( 0, "sll", 7, 5, 224),
  ]


def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "sll", 0, 3, 0),
    gen_rr_srcs_dep_test( 4, "sll", 6, 9, 3072),
    gen_rr_srcs_dep_test( 3, "sll", 0, 4, 0),
    gen_rr_srcs_dep_test( 2, "sll", 0, 7, 0),
    gen_rr_srcs_dep_test( 1, "sll", 6, 5, 192),
    gen_rr_srcs_dep_test( 0, "sll", 10, 10, 10240),
  ]


def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "sll", 8, 3, 64),
    gen_rr_src1_eq_dest_test( "sll", 8, 1, 16),
    gen_rr_src0_eq_src1_test( "sll", 1, 2),
    gen_rr_srcs_eq_dest_test( "sll", 8, 2048),
  ]

def gen_value_test():
  return [
    gen_rr_value_test( "sll", 0x00000000, 0x00000000, 0x00000000),
    gen_rr_value_test( "sll", 0x00000001, 0x00000001, 0x00000002),
    gen_rr_value_test( "sll", 0x00000003, 0x00000001, 0x00000006),
    gen_rr_value_test( "sll", 0x00000000, 0xffff8000, 0x00000000),
    gen_rr_value_test( "sll", 0x80000000, 0x00000000, 0x80000000),
    gen_rr_value_test( "sll", 0x80000000, 0xffff8000, 0x80000000),
    gen_rr_value_test( "sll", 0x80000000, 0xffff8000, 0x80000000),
    gen_rr_value_test( "sll", 0x00000000, 0x00007fff, 0x00000000),
    gen_rr_value_test( "sll", 0x7fffffff, 0x00ffff00, 0x7fffffff),
    gen_rr_value_test( "sll", 0x7fffffff, 0x00007fff, 0x80000000),
    gen_rr_value_test( "sll", 0x80000000, 0x00007fff, 0x00000000),
    gen_rr_value_test( "sll", 0x7fffffff, 0xffff8000, 0x7fffffff),
  ]

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(-1 * (1 << 31), (1 << 31) - 1))
    src1 = Bits( 32, random.randint(-1 * (1 << 31), (1 << 31) - 1))
    dest = Bits( 32, src0 << (src1.uint() & 0x1F), trunc=True)
    asm_code.append( gen_rr_value_test( "sll", src0.int(), src1.int(), dest.int() ) )
  return asm_code
   
