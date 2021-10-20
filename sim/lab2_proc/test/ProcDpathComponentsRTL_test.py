#=========================================================================
# ProcDpathComponentsRTL_test.py
#=========================================================================

import pytest
import random

from pymtl      import *
from harness    import *
from pclib.test import mk_test_case_table, run_sim
from pclib.test import run_test_vector_sim

from lab2_proc.ProcDpathComponentsRTL import ImmGenRTL
from lab2_proc.ProcDpathComponentsRTL import AluRTL

#-------------------------------------------------------------------------
# ImmGenRTL
#-------------------------------------------------------------------------

def test_immgen( test_verilog, dump_vcd ):

  header_str = \
  ( "imm_type", "inst",
    "imm*" )
  
  run_test_vector_sim( ImmGenRTL(), [ header_str,
    # imm_type inst                                imm
    [ 0,       0b11111111111100000000000000000000, 0b11111111111111111111111111111111], # I-imm
    [ 0,       0b00000000000011111111111111111111, 0b00000000000000000000000000000000], # I-imm
    [ 0,       0b01111111111100000000000000000000, 0b00000000000000000000011111111111], # I-imm
    [ 0,       0b11111111111000000000000000000000, 0b11111111111111111111111111111110], # I-imm
    [ 1,       0b11111110000000000000111110000000, 0b11111111111111111111111111111111], # S-imm
    [ 1,       0b00000001111111111111000001111111, 0b00000000000000000000000000000000], # S-imm
    [ 1,       0b01111110000000000000111110000000, 0b00000000000000000000011111111111], # S-imm
    [ 1,       0b11111110000000000000111100000000, 0b11111111111111111111111111111110], # S-imm
    [ 2,       0b11111110000000000000111110000000, 0b11111111111111111111111111111110], # B-imm
    [ 2,       0b00000001111111111111000001111111, 0b00000000000000000000000000000000], # B-imm
    [ 2,       0b11000000000000000000111100000000, 0b11111111111111111111010000011110], # B-imm
    [ 3,       0b11111111111111111111000000000000, 0b11111111111111111111000000000000], # U-imm
    [ 3,       0b00000000000000000000111111111111, 0b00000000000000000000000000000000], # U-imm
    [ 4,       0b11111111111111111111000000000000, 0b11111111111111111111111111111110], # J-imm
    [ 4,       0b00000000000000000001111111111111, 0b00000000000000000001000000000000], # J-imm
    [ 4,       0b01000000000010011001000000000000, 0b00000000000010011001010000000000], # J-imm
  ], dump_vcd, test_verilog )

#-------------------------------------------------------------------------
# AluRTL
#-------------------------------------------------------------------------

def test_alu_add( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,   0,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x0ffaa660,   0x00012304,   0,  0x0ffbc964,   '?',      '?',       '?'      ],
    #pos-neg
    [ 0x00132050,   0xd6620040,   0,  0xd6752090,   '?',      '?',       '?'      ],
    [ 0xfff0a440,   0x00004450,   0,  0xfff0e890,   '?',      '?',       '?'      ],
    # neg-neg
    [ 0xfeeeeaa3,   0xf4650000,   0,  0xf353eaa3,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )


def test_alu_sub( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,   1,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x80000000,   0xffff8000,   1,  0x80008000,   '?',      '?',       '?'      ],
    [ 0x00000000,   0x00007fff,   1,  0xffff8001,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0x00ffff00,   1,  0x7f0000ff,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0xffff8000,   1,  0x80007fff,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )


def test_alu_and( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0xffffffff,   0x0f0f0f0f,   2,  0x0f0f0f0f,   '?',      '?',       '?'      ],
    [ 0xff00ff00,   0x0f0f0f0f,   2,  0x0f000f00,   '?',      '?',       '?'      ],
    [ 0x0ff00ff0,   0xf0f0f0f0,   2,  0x00f000f0,   '?',      '?',       '?'      ],
    [ 0x00ff00ff,   0x0f0f0f0f,   2,  0x000f000f,   '?',      '?',       '?'      ],
    [ 0xf00ff00f,   0xf0f0f0f0,   2,  0xf000f000,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )


def test_alu_or( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0xff00ff00,   0x0f0f0f0f,   3,  0xff0fff0f,   '?',      '?',       '?'      ],
    [ 0x0ff00ff0,   0xf0f0f0f0,   3,  0xfff0fff0,   '?',      '?',       '?'      ],
    [ 0x00ff00ff,   0x0f0f0f0f,   3,  0x0fff0fff,   '?',      '?',       '?'      ],
    [ 0xf00ff00f,   0xf0f0f0f0,   3,  0xf0fff0ff,   '?',      '?',       '?'      ],
    [ 0x00000f0f,   0x000000ff,   3,  0x00000fff,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )

def test_alu_cp_xor( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0xff00ff00,   0x0f0f0f0f,   4,  0xf00ff00f,   '?',      '?',       '?'      ],
    [ 0x0ff00ff0,   0xf0f0f0f0,   4,  0xff00ff00,   '?',      '?',       '?'      ],
    [ 0x00ff00ff,   0x0f0f0f0f,   4,  0x0ff00ff0,   '?',      '?',       '?'      ],
    [ 0xf00ff00f,   0xf0f0f0f0,   4,  0x00ff00ff,   '?',      '?',       '?'      ],
    [ 0x00000f0f,   0x000000ff,   4,  0x00000ff0,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )

def test_alu_slt( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00007fff,   5,  0x00000001,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0x00ffff00,   5,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0x00007fff,   5,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x80000000,   0x00007fff,   5,  0x00000001,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0xffff8000,   5,  0x00000000,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )


def test_alu_sltu( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00007fff,   6,  0x00000001,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0x00ffff00,   6,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0x00007fff,   6,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x80000000,   0x00007fff,   6,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0xffff8000,   6,  0x00000001,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )

def test_alu_sra( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00007fff,   7,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0x00ffff00,   7,  0x7fffffff,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0x00007fff,   7,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x80000000,   0x00007fff,   7,  0xffffffff,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0xffff8000,   7,  0x7fffffff,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )


def test_alu_srl( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00007fff,   8,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0x00ffff00,   8,  0x7fffffff,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0x00007fff,   8,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x80000000,   0x00007fff,   8,  0x00000001,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0xffff8000,   8,  0x7fffffff,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )

def test_alu_sll( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00007fff,   9,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0x00ffff00,   9,  0x7fffffff,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0x00007fff,   9,  0x80000000,   '?',      '?',       '?'      ],
    [ 0x80000000,   0x00007fff,   9,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0xffff8000,   9,  0x7fffffff,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )

def test_alu_cp_op0( dump_vcd, test_verilog  ):
  run_test_vector_sim( AluRTL(), [
      ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
      [ 0x00000000,   0x00000000,  11,  0x00000000,   '?',      '?',       '?'       ],
      [ 0x0ffaa660,   0x00012304,  11,  0x0ffaa660,   '?',      '?',       '?'       ],
      [ 0x00132050,   0xd6620040,  11,  0x00132050,   '?',      '?',       '?'       ],
      [ 0xfff0a440,   0x00004450,  11,  0xfff0a440,   '?',      '?',       '?'       ],
      [ 0xfeeeeaa3,   0xf4650000,  11,  0xfeeeeaa3,   '?',      '?',       '?'       ],
  ], dump_vcd, test_verilog  )

def test_alu_cp_op1( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,  12,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x0ffaa660,   0x00012304,  12,  0x00012304,   '?',      '?',       '?'      ],
    [ 0x00132050,   0xd6620040,  12,  0xd6620040,   '?',      '?',       '?'      ],
    [ 0xfff0a440,   0x00004450,  12,  0x00004450,   '?',      '?',       '?'      ],
    [ 0xfeeeeaa3,   0xf4650000,  12,  0xf4650000,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )

def test_alu_fn_equality( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,  14,  0x00000000,   1,        '?',       '?'      ],
    [ 0x0ffaa660,   0x00012304,  14,  0x00000000,   0,        '?',       '?'      ],
    [ 0x00132050,   0xd6620040,  14,  0x00000000,   0,        '?',       '?'      ],
    [ 0xfff0a440,   0x00004450,  14,  0x00000000,   0,        '?',       '?'      ],
    [ 0xfeeeeaa3,   0xf4650000,  14,  0x00000000,   0,        '?',       '?'      ],
  ], dump_vcd, test_verilog )

def test_alu_fn_lessThanUnsigned( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,  15,  0x00000000,   '?',        '?',       0      ],
    [ 0x0ffaa660,   0x00012304,  15,  0x00000000,   '?',        '?',       0      ],
    [ 0x00132050,   0xd6620040,  15,  0x00000000,   '?',        '?',       1      ],
    [ 0xfff0a440,   0x00004450,  15,  0x00000000,   '?',        '?',       0      ],
    [ 0xf0eeeaa3,   0xf4650000,  15,  0x00000000,   '?',        '?',       1      ],
  ], dump_vcd, test_verilog )

def test_alu_fn_lessThanSigned( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,  13,  0x00000000,   '?',        0,       '?'      ],
    [ 0x0ffaa660,   0x00012304,  13,  0x00000000,   '?',        0,       '?'      ],
    [ 0xf0132050,   0xd6620040,  13,  0x00000000,   '?',        0,       '?'      ],
    [ 0xfff0a440,   0x00004450,  13,  0x00000000,   '?',        1,       '?'      ],
    [ 0xf0eeeaa3,   0xf4650000,  13,  0x00000000,   '?',        1,       '?'      ],
  ], dump_vcd, test_verilog )