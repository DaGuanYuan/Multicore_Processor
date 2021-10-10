#=========================================================================
# srl
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
    srl x3, x1, x2
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
    gen_rr_dest_dep_test( 5, "srl", 9, 2, 2),
    gen_rr_dest_dep_test( 4, "srl", 7, 2, 1),
    gen_rr_dest_dep_test( 3, "srl", 5, 3, 0),
    gen_rr_dest_dep_test( 2, "srl", 8, 9, 0),
    gen_rr_dest_dep_test( 1, "srl", 2, 1, 1),
    gen_rr_dest_dep_test( 0, "srl", 4, 7, 0),
  ]


def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "srl", 2, 3, 0),
    gen_rr_src0_dep_test( 4, "srl", 5, 5, 0),
    gen_rr_src0_dep_test( 3, "srl", 0, 0, 0),
    gen_rr_src0_dep_test( 2, "srl", 7, 10, 0),
    gen_rr_src0_dep_test( 1, "srl", 7, 3, 0),
    gen_rr_src0_dep_test( 0, "srl", 8, 8, 0),
  ]


def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "srl", 7, 8, 0),
    gen_rr_src1_dep_test( 4, "srl", 2, 10, 0),
    gen_rr_src1_dep_test( 3, "srl", 1, 3, 0),
    gen_rr_src1_dep_test( 2, "srl", 4, 7, 0),
    gen_rr_src1_dep_test( 1, "srl", 5, 4, 0),
    gen_rr_src1_dep_test( 0, "srl", 0, 0, 0),
  ]


def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "srl", 6, 7, 0),
    gen_rr_srcs_dep_test( 4, "srl", 6, 0, 6),
    gen_rr_srcs_dep_test( 3, "srl", 6, 2, 1),
    gen_rr_srcs_dep_test( 2, "srl", 0, 1, 0),
    gen_rr_srcs_dep_test( 1, "srl", 2, 8, 0),
    gen_rr_srcs_dep_test( 0, "srl", 3, 4, 0),
  ]


def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "srl", 7, 2, 1),
    gen_rr_src1_eq_dest_test( "srl", 0, 0, 0),
    gen_rr_src0_eq_src1_test( "srl", 1, 0),
    gen_rr_srcs_eq_dest_test( "srl", 8, 0),
  ]

def gen_value_test():
  return [
    gen_rr_value_test( "srl", 0x00000000, 0x00000000, 0x00000000),
    gen_rr_value_test( "srl", 0x00000001, 0x00000001, 0x00000000),
    gen_rr_value_test( "srl", 0x00000003, 0x00000001, 0x00000001),
    gen_rr_value_test( "srl", 0x00000000, 0xffff8000, 0x00000000),
    gen_rr_value_test( "srl", 0x80000000, 0x00000000, 0x80000000),
    gen_rr_value_test( "srl", 0x80000000, 0xffff8000, 0x80000000),
    gen_rr_value_test( "srl", 0x80000000, 0xffff8000, 0x80000000),
    gen_rr_value_test( "srl", 0x00000000, 0x00007fff, 0x00000000),
    gen_rr_value_test( "srl", 0x7fffffff, 0x00ffff00, 0x7fffffff),
    gen_rr_value_test( "srl", 0x7fffffff, 0x00007fff, 0x00000000),
    gen_rr_value_test( "srl", 0x80000000, 0x00007fff, 0x00000001),
    gen_rr_value_test( "srl", 0x7fffffff, 0xffff8000, 0x7fffffff),
  ]

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(-1 * (1 << 31), (1 << 31) - 1))
    src1 = Bits( 32, random.randint(-1 * (1 << 31), (1 << 31) - 1))
    dest = Bits( 32, (src0 >> (src1.uint() & 0x1F)).int(), trunc=True)
    asm_code.append( gen_rr_value_test( "srl", src0.int(), src1.int(), dest.int() ) )
  return asm_code
   

