#=========================================================================
# ProcBase_test.py
#=========================================================================

import pytest
import random

from pymtl   import *
from harness import *
from lab2_proc.ProcAltRTL import ProcAltRTL


import integ_test
@pytest.mark.parametrize( "name,test", [
  asm_test( integ_test.gen_basic_test          ) ,
  asm_test( integ_test.gen_alg1_test),
  asm_test( integ_test.gen_alg2_test),
  asm_test( integ_test.gen_alg3_test),
  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to test more complicated
  # scenarios.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
])
def test_jal( name, test, dump_vcd ):
  run_test( ProcAltRTL, test, dump_vcd )