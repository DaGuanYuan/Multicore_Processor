#=========================================================================
# ProcFL_ingr_test.py
#=========================================================================

import pytest
import random

from pymtl   import *
from harness import *
from lab2_proc.ProcFL import ProcFL

import integration

@pytest.mark.parametrize( "name,test", [
  asm_test( integration.gen_basic_test        ) ,
  asm_test( integration.gen_alg1_test    ) ,
  asm_test( integration.gen_alg2_test    ) ,
  asm_test( integration.gen_alg3_test    ) ,
  asm_test( integration.gen_integ_test_estimating_execution_time    ) ,
  asm_test( integration.gen_integ_test_3_regs_raw_data_hazards    ) ,
  asm_test( integration.gen_integ_test_2_regs_raw_data_hazards    ) ,
  asm_test( integration.gen_integ_test_branch_over_jumps    ) ,
])

def test_ingr( name, test, dump_vcd ):
  run_test( ProcFL, test, dump_vcd )

  