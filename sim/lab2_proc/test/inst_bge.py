#=========================================================================
# bge
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """

    # Use x3 to track the control flow pattern
    addi  x3, x0, 0

    csrr  x1, mngr2proc < 2
    csrr  x2, mngr2proc < 2

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

    # This branch should be taken
    bge   x1, x2, label_a
    addi  x3, x3, 0b01

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

  label_a:
    addi  x3, x3, 0b10

    # Only the second bit should be set if branch was taken
    csrw proc2mngr, x3 > 0b10

  """

# ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define additional directed and random test cases.
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

#-------------------------------------------------------------------------
# gen_src0_dep_taken_test
#-------------------------------------------------------------------------

def gen_src0_dep_taken_test():
  return [
    gen_br2_src0_dep_test( 5, "bge", 0, 0, True ),
    gen_br2_src0_dep_test( 4, "bge", 1, 0, True ),
    gen_br2_src0_dep_test( 3, "bge", 2, 0, True ),
    gen_br2_src0_dep_test( 2, "bge", 3, 0, True ),
    gen_br2_src0_dep_test( 1, "bge", 4, 0, True ),
    gen_br2_src0_dep_test( 0, "bge", 5, 0, True ),
  ]

#-------------------------------------------------------------------------
# gen_src0_dep_nottaken_test
#-------------------------------------------------------------------------

def gen_src0_dep_nottaken_test():
  return [
    gen_br2_src0_dep_test( 5, "bge", 0, 1, False ),
    gen_br2_src0_dep_test( 4, "bge", 0, 2, False ),
    gen_br2_src0_dep_test( 3, "bge", 0, 3, False ),
    gen_br2_src0_dep_test( 2, "bge", 0, 4, False ),
    gen_br2_src0_dep_test( 1, "bge", 0, 5, False ),
    gen_br2_src0_dep_test( 0, "bge", 0, 6, False ),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_taken_test
#-------------------------------------------------------------------------

def gen_src1_dep_taken_test():
  return [
    gen_br2_src1_dep_test( 5, "bge", 0, 0, True ),
    gen_br2_src1_dep_test( 4, "bge", 1, 0, True ),
    gen_br2_src1_dep_test( 3, "bge", 2, 0, True ),
    gen_br2_src1_dep_test( 2, "bge", 3, 0, True ),
    gen_br2_src1_dep_test( 1, "bge", 4, 0, True ),
    gen_br2_src1_dep_test( 0, "bge", 5, 0, True ),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_nottaken_test
#-------------------------------------------------------------------------

def gen_src1_dep_nottaken_test():
  return [
    gen_br2_src1_dep_test( 5, "bge", 0, 1, False ),
    gen_br2_src1_dep_test( 4, "bge", 0, 2, False ),
    gen_br2_src1_dep_test( 3, "bge", 0, 3, False ),
    gen_br2_src1_dep_test( 2, "bge", 0, 4, False ),
    gen_br2_src1_dep_test( 1, "bge", 0, 5, False ),
    gen_br2_src1_dep_test( 0, "bge", 0, 6, False ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_taken_test
#-------------------------------------------------------------------------

def gen_srcs_dep_taken_test():
  return [
    gen_br2_srcs_dep_test( 5, "bge", 2, 1, True ),
    gen_br2_srcs_dep_test( 4, "bge", 3, 2, True ),
    gen_br2_srcs_dep_test( 3, "bge", 4, 3, True ),
    gen_br2_srcs_dep_test( 2, "bge", 5, 4, True ),
    gen_br2_srcs_dep_test( 1, "bge", 6, 5, True ),
    gen_br2_srcs_dep_test( 0, "bge", 7, 6, True ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_nottaken_test
#-------------------------------------------------------------------------

def gen_srcs_dep_nottaken_test():
  return [
    gen_br2_srcs_dep_test( 5, "bge", 1, 2, False ),
    gen_br2_srcs_dep_test( 4, "bge", 2, 3, False ),
    gen_br2_srcs_dep_test( 3, "bge", 3, 4, False ),
    gen_br2_srcs_dep_test( 2, "bge", 4, 5, False ),
    gen_br2_srcs_dep_test( 1, "bge", 5, 6, False ),
    gen_br2_srcs_dep_test( 0, "bge", 6, 7, False ),
  ]

#-------------------------------------------------------------------------
# gen_src0_eq_src1_taken_test
#-------------------------------------------------------------------------

def gen_src0_eq_src1_test():
  return [
    gen_br2_src0_eq_src1_test( "bge", 1, True ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_br2_value_test( "bge", -1, -1, True  ),
    gen_br2_value_test( "bge", -1,  0, False ),
    gen_br2_value_test( "bge", -1,  1, False ),

    gen_br2_value_test( "bge",  0, -1, True  ),
    gen_br2_value_test( "bge",  0,  0, True  ),
    gen_br2_value_test( "bge",  0,  1, False ),

    gen_br2_value_test( "bge",  1, -1, True  ),
    gen_br2_value_test( "bge",  1,  0, True  ),
    gen_br2_value_test( "bge",  1,  1, True  ),

    gen_br2_value_test( "bge", 0xfffffff7, 0xfffffff7, True  ),
    gen_br2_value_test( "bge", 0x7fffffff, 0x7fffffff, True  ),
    gen_br2_value_test( "bge", 0xfffffff7, 0x7fffffff, False ),
    gen_br2_value_test( "bge", 0x7fffffff, 0xfffffff7, True  ),

    gen_br2_value_test( "bge", 0xffffffff, -2,         True  ),
    gen_br2_value_test( "bge", 0xffffffff, -1,         True  ),
    gen_br2_value_test( "bge", 0xffffffff, -0,         False ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0  = Bits( 32, random.randint(-1 * (1 << 31), (1 << 31) - 1))
    src1  = Bits( 32, random.randint(-1 * (1 << 31), (1 << 31) - 1))
    taken = src0.int() >= src1.int()
    asm_code.append( gen_br2_value_test( "bge", src0.int(), src1.int(), taken ) )
  return asm_code

  # somthing is wrong with this
  # def gen_random_test():
  # asm_code = []
  # for i in xrange(25):
  #   taken = random.choice([True, False])
  #   src0  = Bits( 32, random.randint(0,0xffffffff) )
  #   if taken:
  #     # Branch taken, OP1 is greater than or equal to OP2
  #     src1 = Bits( 32, random.randint(src0.int(), 0xffffffff) )
  #   else:
  #     # Branch not taken, OP1 is smaller than OP2
  #     src1 = Bits( 32, random.randint(     0,    src0.int() ) )
  #   asm_code.append( gen_br2_value_test( "bge", src0.uint(), src1.uint(), taken ) )
  # return asm_code