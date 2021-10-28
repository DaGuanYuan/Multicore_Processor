#=========================================================================
# ProcBaseRTL_test.py
#=========================================================================

import pytest
import random

from pymtl   import *
from harness import *
from lab2_proc.ProcBaseRTL import ProcBaseRTL

#-------------------------------------------------------------------------
# jal
#-------------------------------------------------------------------------

import inst_jal

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_jal.gen_basic_test          ) ,
  asm_test( inst_jal.gen_one_jump_test       ) ,
  asm_test( inst_jal.gen_seq_test            ) ,
  asm_test( inst_jal.gen_back_test           ) ,
  asm_test( inst_jal.gen_seq_and_back_test   ) ,
  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to test more complicated
  # scenarios.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
])

def test_jal( name, test, dump_vcd ):
  run_test( ProcBaseRTL, test, dump_vcd )

def test_jal_rand_delays( dump_vcd ):
  run_test( ProcBaseRTL, inst_jal.gen_random_test, dump_vcd,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3)

# ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# random stall and delay
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#-------------------------------------------------------------------------
# jalr
#-------------------------------------------------------------------------

import inst_jalr

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_jalr.gen_basic_test    ) ,
  asm_test( inst_jalr.gen_one_jump_test       ) ,
  asm_test( inst_jalr.gen_seq_test            ) ,
  asm_test( inst_jalr.gen_lsb_test),
  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to test more complicated
  # scenarios.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
])
def test_jalr( name, test, dump_vcd ):
  run_test( ProcBaseRTL, test, dump_vcd )

# ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# random stall and delay
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
def test_jalr_rand_delays( dump_vcd ):
  run_test( ProcBaseRTL, inst_jalr.gen_random_test, dump_vcd,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3)
