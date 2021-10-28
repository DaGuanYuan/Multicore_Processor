#=========================================================================
# ProcBaseRTL_ingr_test.py
#=========================================================================

import pytest
import random

from pymtl   import *
from harness import *
from lab2_proc.ProcBaseRTL import ProcBaseRTL

import integration

@pytest.mark.parametrize( "name,test", [
  asm_test( integration.gen_basic_test     ),
  asm_test( integration.gen_alg1_test    ) ,
  asm_test( integration.gen_alg2_test    ) ,
  asm_test( integration.gen_alg3_test    ) ,
  asm_test( integration.gen_integ_test_estimating_execution_time    ) ,
  asm_test( integration.gen_integ_test_3_regs_raw_data_hazards    ) ,
  asm_test( integration.gen_integ_test_2_regs_raw_data_hazards    ) ,
  asm_test( integration.gen_integ_test_branch_over_jumps    ) ,
  asm_test( integration.temp_test)
])

def test_ingr( name, test, dump_vcd ):
  run_test( ProcBaseRTL, test, dump_vcd )

def test_ingr_rand_delays( dump_vcd ):
  run_test( ProcBaseRTL, integration.gen_basic_test, dump_vcd,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

