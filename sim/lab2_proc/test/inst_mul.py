#=========================================================================
# mul
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
    csrr x2, mngr2proc < 4
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    mul x3, x1, x2
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 20
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
    gen_rr_dest_dep_test( 5, "mul", 1, 5, 5),
    gen_rr_dest_dep_test( 4, "mul", 1, 5, 5),
    gen_rr_dest_dep_test( 3, "mul", 7, 9, 63),
    gen_rr_dest_dep_test( 2, "mul", 8, -5, -40),
    gen_rr_dest_dep_test( 1, "mul", 4, -7, -28),
    gen_rr_dest_dep_test( 0, "mul", -9, -3, 27),
  ]


def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "mul", 2, 7, 14),
    gen_rr_src0_dep_test( 4, "mul", -3, -9, 27),
    gen_rr_src0_dep_test( 3, "mul", -1, -8, 8),
    gen_rr_src0_dep_test( 2, "mul", -4, -5, 20),
    gen_rr_src0_dep_test( 1, "mul", 9, 1, 9),
    gen_rr_src0_dep_test( 0, "mul", -4, -9, 36),
  ]


def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "mul", -10, 6, -60),
    gen_rr_src1_dep_test( 4, "mul", 5, -9, -45),
    gen_rr_src1_dep_test( 3, "mul", 1, 5, 5),
    gen_rr_src1_dep_test( 2, "mul", 7, 7, 49),
    gen_rr_src1_dep_test( 1, "mul", -8, -10, 80),
    gen_rr_src1_dep_test( 0, "mul", -3, -1, 3),
  ]


def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "mul", -10, 4, -40),
    gen_rr_srcs_dep_test( 4, "mul", -4, -7, 28),
    gen_rr_srcs_dep_test( 3, "mul", 0, -5, 0),
    gen_rr_srcs_dep_test( 2, "mul", -2, -6, 12),
    gen_rr_srcs_dep_test( 1, "mul", 10, -7, -70),
    gen_rr_srcs_dep_test( 0, "mul", -8, -1, 8),
  ]


def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "mul", -10, -1, 10),
    gen_rr_src1_eq_dest_test( "mul", -3, -10, 30),
    gen_rr_src0_eq_src1_test( "mul", 10, 100),
    gen_rr_srcs_eq_dest_test( "mul", -7, 49),
  ]

def gen_value_test():
  return [
    gen_rr_value_test( "mul", 0x00000000, 0x00000000, 0x00000000),
    gen_rr_value_test( "mul", 0x00000001, 0x00000001, 0x00000001),
    gen_rr_value_test( "mul", 0x00000003, 0x00000001, 0x00000003),
    gen_rr_value_test( "mul", 0x00000000, 0xffff8000, 0x00000000),
    gen_rr_value_test( "mul", 0x80000000, 0x00000000, 0x00000000),
    gen_rr_value_test( "mul", 0x80000000, 0xffff8000, 0x00000000),
    gen_rr_value_test( "mul", 0x80000000, 0xffff8000, 0x00000000),
    gen_rr_value_test( "mul", 0x00000000, 0x00007fff, 0x00000000),
    gen_rr_value_test( "mul", 0x7fffffff, 0x00ffff00, 0xff000100),
    gen_rr_value_test( "mul", 0x7fffffff, 0x00007fff, 0x7fff8001),
    gen_rr_value_test( "mul", 0x80000000, 0x00007fff, 0x80000000),
    gen_rr_value_test( "mul", 0x7fffffff, 0xffff8000, 0x00008000),
  ]

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(-1 * (1 << 31), (1 << 31) - 1))
    src1 = Bits( 32, random.randint(-1 * (1 << 31), (1 << 31) - 1))
    dest = Bits( 32, src0.int() * src1.int(), trunc=True)
    asm_code.append( gen_rr_value_test( "mul", src0.int(), src1.int(), dest.int() ) )
  return asm_code
   