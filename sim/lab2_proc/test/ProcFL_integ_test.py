#=========================================================================
# ProcFL_test.py
#=========================================================================

import pytest
import random

from pymtl   import *
from harness import *
from lab2_proc.ProcFL import ProcFL


import integ_test
@pytest.mark.parametrize( "name,test", [
  asm_test( integ_test.gen_integ_test_mz588                        ) ,
  asm_test( integ_test.gen_integ_test_estimating_execution_time    ) ,
  asm_test( integ_test.gen_integ_test_3_regs_raw_data_hazards      ) ,
  asm_test( integ_test.gen_integ_test_2_regs_raw_data_hazards      ) ,
  asm_test( integ_test.gen_integ_test_branch_over_jumps            ) ,
  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to test more complicated
  # scenarios.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
])
def test_jal( name, test, dump_vcd ):
  run_test( ProcFL, test, dump_vcd )