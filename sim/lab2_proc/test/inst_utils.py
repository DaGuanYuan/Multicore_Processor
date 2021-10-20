#=========================================================================
# inst_utils
#=========================================================================
# Includes helper functions to simplify creating assembly tests.

from pymtl import *

#-------------------------------------------------------------------------
# print_asm
#-------------------------------------------------------------------------
# Pretty print a generated assembly syntax

def print_asm( asm_code ):

  # If asm_code is a single string, then put it in a list to simplify the
  # rest of the logic.

  asm_code_list = asm_code
  if isinstance( asm_code, str ):
    asm_code_list = [ asm_code ]

  # Create a single list of lines

  asm_list = []
  for asm_seq in asm_code_list:
    asm_list.extend( asm_seq.splitlines() )

  # Print the assembly. Remove duplicate blank lines.

  prev_blank_line = False
  for asm in asm_list:
    if asm.strip() == "":
      if not prev_blank_line:
        print asm
        prev_blank_line = True
    else:
      prev_blank_line = False
      print asm

#-------------------------------------------------------------------------
# gen_nops
#-------------------------------------------------------------------------

def gen_nops( num_nops ):
  if num_nops > 0:
    return "nop\n" + ("    nop\n"*(num_nops-1))
  else:
    return ""

#-------------------------------------------------------------------------
# gen_word_data
#-------------------------------------------------------------------------

def gen_word_data( data_list ):

  data_str = ".data\n"
  for data in data_list:
    data_str += ".word {}\n".format(data)

  return data_str

#-------------------------------------------------------------------------
# gen_hword_data
#-------------------------------------------------------------------------

def gen_hword_data( data_list ):

  data_str = ".data\n"
  for data in data_list:
    data_str += ".hword {}\n".format(data)

  return data_str

#-------------------------------------------------------------------------
# gen_byte_data
#-------------------------------------------------------------------------

def gen_byte_data( data_list ):

  data_str = ".data\n"
  for data in data_list:
    data_str += ".byte {}\n".format(data)

  return data_str

#-------------------------------------------------------------------------
# gen_rr_src01_template
#-------------------------------------------------------------------------
# Template for register-register instructions. We first write src0
# register and then write the src1 register before executing the
# instruction under test. We parameterize the number of nops after
# writing both src registers and the instruction under test to enable
# using this template for testing various bypass paths. We also
# parameterize the register specifiers to enable using this template to
# test situations where the srce registers are equal and/or equal the
# destination register.

def gen_rr_src01_template(
  num_nops_src0, num_nops_src1, num_nops_dest,
  reg_src0, reg_src1,
  inst, src0, src1, result
):
  return """

    # Move src0 value into register
    csrr {reg_src0}, mngr2proc < {src0}
    {nops_src0}

    # Move src1 value into register
    csrr {reg_src1}, mngr2proc < {src1}
    {nops_src1}

    # Instruction under test
    {inst} x3, {reg_src0}, {reg_src1}
    {nops_dest}

    # Check the result
    csrw proc2mngr, x3 > {result}

  """.format(
    nops_src0 = gen_nops(num_nops_src0),
    nops_src1 = gen_nops(num_nops_src1),
    nops_dest = gen_nops(num_nops_dest),
    **locals()
  )

#-------------------------------------------------------------------------
# gen_rr_src10_template
#-------------------------------------------------------------------------
# Similar to the above template, except that we reverse the order in
# which we write the two src registers.

def gen_rr_src10_template(
  num_nops_src0, num_nops_src1, num_nops_dest,
  reg_src0, reg_src1,
  inst, src0, src1, result
):
  return """

    # Move src1 value into register
    csrr {reg_src1}, mngr2proc < {src1}
    {nops_src1}

    # Move src0 value into register
    csrr {reg_src0}, mngr2proc < {src0}
    {nops_src0}

    # Instruction under test
    {inst} x3, {reg_src0}, {reg_src1}
    {nops_dest}

    # Check the result
    csrw proc2mngr, x3 > {result}

  """.format(
    nops_src0 = gen_nops(num_nops_src0),
    nops_src1 = gen_nops(num_nops_src1),
    nops_dest = gen_nops(num_nops_dest),
    **locals()
  )

#-------------------------------------------------------------------------
# gen_rr_dest_dep_test
#-------------------------------------------------------------------------
# Test the destination bypass path by varying how many nops are
# inserted between the instruction under test and reading the destination
# register with a csrr instruction.

def gen_rr_dest_dep_test( num_nops, inst, src0, src1, result ):
  return gen_rr_src01_template( 0, 8, num_nops, "x1", "x2",
                                inst, src0, src1, result )

#-------------------------------------------------------------------------
# gen_rr_src1_dep_test
#-------------------------------------------------------------------------
# Test the source 1 bypass paths by varying how many nops are inserted
# between writing the src1 register and reading this register in the
# instruction under test.

def gen_rr_src1_dep_test( num_nops, inst, src0, src1, result ):
  return gen_rr_src01_template( 8-num_nops, num_nops, 0, "x1", "x2",
                                inst, src0, src1, result )

#-------------------------------------------------------------------------
# gen_rr_src0_dep_test
#-------------------------------------------------------------------------
# Test the source 0 bypass paths by varying how many nops are inserted
# between writing the src0 register and reading this register in the
# instruction under test.

def gen_rr_src0_dep_test( num_nops, inst, src0, src1, result ):
  return gen_rr_src10_template( num_nops, 8-num_nops, 0, "x1", "x2",
                                inst, src0, src1, result )

#-------------------------------------------------------------------------
# gen_rr_srcs_dep_test
#-------------------------------------------------------------------------
# Test both source bypass paths at the same time by varying how many nops
# are inserted between writing both src registers and reading both
# registers in the instruction under test.

def gen_rr_srcs_dep_test( num_nops, inst, src0, src1, result ):
  return gen_rr_src01_template( 0, num_nops, 0, "x1", "x2",
                                inst, src0, src1, result )

#-------------------------------------------------------------------------
# gen_rr_src0_eq_dest_test
#-------------------------------------------------------------------------
# Test situation where the src0 register specifier is the same as the
# destination register specifier.

def gen_rr_src0_eq_dest_test( inst, src0, src1, result ):
  return gen_rr_src01_template( 0, 0, 0, "x3", "x2",
                                inst, src0, src1, result )

#-------------------------------------------------------------------------
# gen_rr_src1_eq_dest_test
#-------------------------------------------------------------------------
# Test situation where the src1 register specifier is the same as the
# destination register specifier.

def gen_rr_src1_eq_dest_test( inst, src0, src1, result ):
  return gen_rr_src01_template( 0, 0, 0, "x1", "x3",
                                inst, src0, src1, result )

#-------------------------------------------------------------------------
# gen_rr_src0_eq_src1_test
#-------------------------------------------------------------------------
# Test situation where the src register specifiers are the same.

def gen_rr_src0_eq_src1_test( inst, src, result ):
  return gen_rr_src01_template( 0, 0, 0, "x1", "x1",
                                inst, src, src, result )

#-------------------------------------------------------------------------
# gen_rr_srcs_eq_dest_test
#-------------------------------------------------------------------------
# Test situation where all three register specifiers are the same.

def gen_rr_srcs_eq_dest_test( inst, src, result ):
  return gen_rr_src01_template( 0, 0, 0, "x3", "x3",
                                inst, src, src, result )

#-------------------------------------------------------------------------
# gen_rr_value_test
#-------------------------------------------------------------------------
# Test the actual operation of a register-register instruction under
# test. We assume that bypassing has already been tested.

def gen_rr_value_test( inst, src0, src1, result ):
  return gen_rr_src01_template( 0, 0, 0, "x1", "x2",
                                inst, src0, src1, result )

#-------------------------------------------------------------------------
# gen_rimm_template
#-------------------------------------------------------------------------
# Template for register-immediate instructions. We first write the src
# register before executing the instruction under test. We parameterize
# the number of nops after writing the src register and the instruction
# under test to enable using this template for testing various bypass
# paths. We also parameterize the register specifiers to enable using
# this template to test situations where the srce registers are equal
# and/or equal the destination register.

def gen_rimm_template(
  num_nops_src, num_nops_dest,
  reg_src,
  inst, src, imm, result
):
  return """

    # Move src value into register
    csrr {reg_src}, mngr2proc < {src}
    {nops_src}

    # Instruction under test
    {inst} x3, {reg_src}, {imm}
    {nops_dest}

    # Check the result
    csrw proc2mngr, x3 > {result}

  """.format(
    nops_src  = gen_nops(num_nops_src),
    nops_dest = gen_nops(num_nops_dest),
    **locals()
  )

#-------------------------------------------------------------------------
# gen_rimm_dest_dep_test
#-------------------------------------------------------------------------
# Test the destination bypass path by varying how many nops are
# inserted between the instruction under test and reading the destination
# register with a csrr instruction.

def gen_rimm_dest_dep_test( num_nops, inst, src, imm, result ):
  return gen_rimm_template( 8, num_nops, "x1",
                            inst, src, imm, result )

#-------------------------------------------------------------------------
# gen_rimm_src_dep_test
#-------------------------------------------------------------------------
# Test the source bypass paths by varying how many nops are inserted
# between writing the src register and reading this register in the
# instruction under test.

def gen_rimm_src_dep_test( num_nops, inst, src, imm, result ):
  return gen_rimm_template( num_nops, 0, "x1",
                            inst, src, imm, result )

#-------------------------------------------------------------------------
# gen_rimm_src_eq_dest_test
#-------------------------------------------------------------------------
# Test situation where the src register specifier is the same as the
# destination register specifier.

def gen_rimm_src_eq_dest_test( inst, src, imm, result ):
  return gen_rimm_template( 0, 0, "x3",
                            inst, src, imm, result )

#-------------------------------------------------------------------------
# gen_rimm_value_test
#-------------------------------------------------------------------------
# Test the actual operation of a register-immediate instruction under
# test. We assume that bypassing has already been tested.

def gen_rimm_value_test( inst, src, imm, result ):
  return gen_rimm_template( 0, 0, "x1",
                            inst, src, imm, result )

#-------------------------------------------------------------------------
# gen_imm_template
#-------------------------------------------------------------------------
# Template for immediate instructions. We parameterize the number of nops
# after the instruction under test to enable using this template for
# testing various bypass paths.

def gen_imm_template( num_nops_dest, inst, imm, result ):
  return """

    # Instruction under test
    {inst} x3, {imm}
    {nops_dest}

    # Check the result
    csrw proc2mngr, x3 > {result}

  """.format(
    nops_dest = gen_nops(num_nops_dest),
    **locals()
  )

#-------------------------------------------------------------------------
# gen_imm_dest_dep_test
#-------------------------------------------------------------------------
# Test the destination bypass path by varying how many nops are
# inserted between the instruction under test and reading the destination
# register with a csrr instruction.

def gen_imm_dest_dep_test( num_nops, inst, imm, result ):
  return gen_imm_template( num_nops, inst, imm, result )

#-------------------------------------------------------------------------
# gen_imm_value_test
#-------------------------------------------------------------------------
# Test the actual operation of an immediate instruction under test. We
# assume that bypassing has already been tested.

def gen_imm_value_test( inst, imm, result ):
  return gen_imm_template( 0, inst, imm, result )


#-------------------------------------------------------------------------
# gen_simpleJump_template
#-------------------------------------------------------------------------
# Template for simple instructions with no source.
gen_jal_simple_template_id = 0
def gen_jal_simple_template(
  inst="jal", reg_src0="x1"
):

  global gen_jal_simple_template_id
  id_a = "label_{}".format( gen_jal_simple_template_id + 1 )
  gen_jal_simple_template_id += 1

  return """
  addi x2, x0, 0
  auipc x3, 0
  addi x3, x3, 12
  {inst} {reg_src0}, {id_a}
  addi x2, x2, 0b0001
{id_a}:
  addi x2, x2, 0b0010
sub {reg_src0}, {reg_src0}, x3
csrw proc2mngr, x2 > 0b0010
csrw proc2mngr, {reg_src0} > 0
    
  """.format(**locals())

def gen_jal_simple_test():
  return gen_jal_simple_template()

#-------------------------------------------------------------------------
# gen_jump_template
#-------------------------------------------------------------------------
# Template for jump instructions with no source.
gen_jal_seq_template_id = 0
def gen_jal_seq_template(
  inst="jal", reg_src0="x1"
):

  global gen_jal_seq_template_id
  id_a = "label_{}".format( gen_jal_seq_template_id + 1 )
  id_b = "label_{}".format( gen_jal_seq_template_id + 2 )
  id_c = "label_{}".format( gen_jal_seq_template_id + 3 )
  id_d = "label_{}".format( gen_jal_seq_template_id + 4 )
  gen_jal_seq_template_id += 4

  return """
  # x2 stores execution sequence
  # x1 default to be the rd
  # x3 stores the correct return addr that should in rd
  addi x2, x0, 0
  auipc x3, 0
  addi x3, x3, 12
  {inst} {reg_src0}, {id_a}
  addi x2, x2, 0b0001 #1st
{id_a}:
  addi x2, x2, 0b0010 #2nd
  addi x4, {reg_src0}, 0
  auipc x5, 0
  addi x5, x5, 12
  {inst} {reg_src0}, {id_b}
  addi x2, x2, 0b0100 #3rd
{id_b}:
  addi x2, x2, 0b1000 #4th
  addi x6, {reg_src0}, 0
  auipc x7, 0
  addi x7, x7, 12
  {inst} {reg_src0}, {id_c}
  addi x2, x2, 0b10000 #5th
{id_c}:
  addi x2, x2, 0b100000 #6th
  addi x8, {reg_src0}, 0
  auipc x9, 0
  addi x9, x9, 12
  {inst} {reg_src0}, {id_d}
  addi x2, x2, 0b1000000 #7th
{id_d}:
  addi x2, x2, 0b10000000 #8th
  addi x10, {reg_src0}, 0
  
sub x3, x3, x4
sub x5, x5, x6
sub x7, x7, x8
sub x9, x9, x10
csrw proc2mngr, x2 > 0b10101010
csrw proc2mngr, x3 > 0
csrw proc2mngr, x5 > 0
csrw proc2mngr, x7 > 0
csrw proc2mngr, x9 > 0
    
  """.format(**locals())

def gen_jal_seq_test():
  return gen_jal_seq_template()

#-------------------------------------------------------------------------
# gen_jump_back_template
#-------------------------------------------------------------------------
# Template for jump instructions.
gen_jal_back_template_id = 0
def gen_jal_back_template(
  inst="jal", reg_src0="x1"
):

  global gen_jal_back_template_id
  id_a = "label_{}".format( gen_jal_back_template_id + 1 )
  id_b = "label_{}".format( gen_jal_back_template_id + 2 )
  id_c = "label_{}".format( gen_jal_back_template_id + 3 )
  id_d = "label_{}".format( gen_jal_back_template_id + 4 )
  id_e = "label_{}".format( gen_jal_back_template_id + 5 )
  gen_jal_back_template_id += 5
  return """
  addi x2, x0, 0
  auipc x3, 0
  addi x3, x3, 12
  {inst} {reg_src0}, {id_a}
  addi x2, x2, 0b0001
{id_c}:
  addi x2, x2, 0b100000 #6th
  addi x8, {reg_src0}, 0
  auipc x9, 0
  addi x9, x9, 12
  {inst} {reg_src0}, {id_d}
  addi x2, x2, 0b1000000 #7th
{id_b}:
  addi x2, x2, 0b1000 #4th
  addi x6, {reg_src0}, 0
  auipc x7, 0
  addi x7, x7, 12
  {inst} {reg_src0}, {id_c}
  addi x2, x2, 0b10000 #5th
{id_a}:
  addi x2, x2, 0b0010 #2nd
  addi x4, {reg_src0}, 0
  auipc x5, 0
  addi x5, x5, 12
  {inst} {reg_src0}, {id_b}
  addi x2, x2, 0b0100 #3rd
{id_d}:
  addi x2, x2, 0b10000000 #8th
  addi x10, {reg_src0}, 0
sub x3, x3, x4
sub x5, x5, x6
sub x7, x7, x8
sub x9, x9, x10
csrw proc2mngr, x2 > 0b10101010
csrw proc2mngr, x3 > 0
csrw proc2mngr, x5 > 0
csrw proc2mngr, x7 > 0
csrw proc2mngr, x9 > 0
  
  """.format(**locals())
#-------------------------------------------------------------------------
# gen_jump_template
#-------------------------------------------------------------------------
# Template for jump instructions with no source.

gen_jal_template_id = 0
def gen_jal_template(
  inst="jal", reg_src0="x1"
):

  global gen_jal_template_id
  id_a = "label_{}".format( gen_jal_template_id + 1 )
  id_b = "label_{}".format( gen_jal_template_id + 2 )
  id_c = "label_{}".format( gen_jal_template_id + 3 )
  gen_jal_template_id += 3

  return """
  # Use x3 to track the control flow pattern 
  addi x3, x0, 0                # 0x200
  
  auipc x7, 0                   # 0x204
  addi x7, x7, 12               # 0x208
  {inst}  {reg_src0}, {id_a}    # 0x20c    #jal -----.
  addi x3, x3, 0b000001         # 0x210    #         |
                                           #         |
{id_b}:                                    #    <----|--.
    addi x3, x3, 0b000010       # 0x214    #         |  |
    addi x5, {reg_src0}, 0      # 0x218    #         |  |
    auipc x8, 0                                      |  |
    addi x8, x8, 12                                  |  |
    {inst}  {reg_src0}, {id_c}  # 0x21c    #jal     -|--|---.
    addi x1, x3, 0b000100       # 0x220    #         |  |   |
                                           #         |  |   |
{id_a}:                                    #   <-----'  |   |
    addi x3, x3, 0b001000       # 0x22c    #            |   |
    addi x4, {reg_src0}, 0      # 0x230    #            |   |
    auipc x9, 0                 # 0x234                 |   |
    addi x9, x9, 12             # 0x238                 |   |
    {inst}  {reg_src0}, {id_b}  # 0x23c    #jal --------'   |
    addi x3, x3, 0b010000       # 0x240    #                |
                                           #                |
{id_c}:                                    #          <-----'
    addi x3, x3, 0b100000       # 0x244
    addi x6, {reg_src0}, 0      # 0x248
  csrw proc2mngr, x3 > 0b101010
  sub x4, x4, x7
  sub x5, x5, x9
  sub x6, x6, x8
  csrw proc2mngr, x4 > 0
  csrw proc2mngr, x5 > 0
  csrw proc2mngr, x6 > 0
  
  """.format(**locals())

def gen_jal_test():
  return gen_jal_template("jal","x1")

#-------------------------------------------------------------------------
# gen_jal_random_template
#-------------------------------------------------------------------------
gen_jal_random_template_id = 0
def gen_jal_random_template(
  inst="jal", reg_src0="x1", target="label_1"
):

  target_numb = int(target.replace("label_", ""), 0)


  global gen_jal_random_template_id
  ctrl_seq_val = 0

  if target_numb == 1:
    ctrl_seq_val = 0xfffff800 + 0b10
    target = "label_{}".format(gen_jal_random_template_id + 1)
  elif target_numb == 2:
    ctrl_seq_val = 0xfffff800 + 0b1000
    target = "label_{}".format(gen_jal_random_template_id + 2)
  elif target_numb == 3:
    ctrl_seq_val = 0xfffff800 + 0b100000
    target = "label_{}".format(gen_jal_random_template_id + 3)
  elif target_numb == 4:
    ctrl_seq_val = 0xfffff800 + 0b10000000
    target = "label_{}".format(gen_jal_random_template_id + 4)
  elif target_numb == 5:
    ctrl_seq_val = 0xfffff800 + 0b1000000000
    target = "label_{}".format(gen_jal_random_template_id + 5)

  id_a = "label_{}".format( gen_jal_random_template_id + 1 )
  id_b = "label_{}".format( gen_jal_random_template_id + 2 )
  id_c = "label_{}".format( gen_jal_random_template_id + 3 )
  id_d = "label_{}".format( gen_jal_random_template_id + 4 )
  id_e = "label_{}".format( gen_jal_random_template_id + 5 )
  id_f = "label_{}".format( gen_jal_random_template_id + 6 )
  gen_jal_random_template_id += 6
  
  return """
  addi x2, x0, 0
  auipc x3, 0
  addi x3, x3, 12
  {inst} {reg_src0}, {target}
  addi x2, x2, 0b1
{id_a}:
  addi x2, x2, 0b10
  addi x4, {reg_src0}, 0
  auipc x5, 0
  addi x5, x5, 12
  {inst} {reg_src0}, {id_f}
  addi x2, x2, 0b100
{id_b}:
  addi x2, x2, 0b1000
  addi x4, {reg_src0}, 0
  auipc x5, 0
  addi x5, x5, 12
  {inst} {reg_src0}, {id_f}
  addi x2, x2, 0b10000
{id_c}:
  addi x2, x2, 0b100000
  addi x4, {reg_src0}, 0
  auipc x5, 0
  addi x5, x5, 12
  {inst} {reg_src0}, {id_f}
  addi x2, x2, 0b1000000
{id_d}:
  addi x2, x2, 0b10000000
  addi x4, {reg_src0}, 0
  auipc x5, 0
  addi x5, x5, 12
  {inst} {reg_src0}, {id_f}
  addi x2, x2, 0b100000000
{id_e}:
  addi x2, x2, 0b1000000000
  addi x4, {reg_src0}, 0
  auipc x5, 0
  addi x5, x5, 12
  {inst} {reg_src0}, {id_f}
  addi x2, x2, 0b10000000000
{id_f}:
  addi x2, x2, 0b100000000000
  addi x6, {reg_src0}, 0
  
  sub x3, x3, x4
  sub x5, x5, x6
  csrw   proc2mngr, x2 > {ctrl_seq_val}
  csrw   proc2mngr, x3 > 0
  csrw   proc2mngr, x5 > 0
  """.format(**locals())

def gen_jal_value_test (inst, target):
  return gen_jal_random_template(inst=inst, target=target)

#-------------------------------------------------------------------------
# gen_simpleJump_template
#-------------------------------------------------------------------------
# Template for simple instructions with no source.
gen_jalr_simple_template_id = 0
def gen_jalr_simple_template(
  inst="jalr", reg_src0="x1", reg_src1="x2"
):

  global gen_jalr_simple_template_id
  id_a = "label_{}".format( gen_jalr_simple_template_id + 1 )
  gen_jalr_simple_template_id += 1

  return """
  lui  {reg_src1},     %hi[{id_a}]
  addi {reg_src1}, {reg_src1}, %lo[{id_a}]
  addi x3, x0, 0
  auipc x4, 0
  addi x4, x4, 12
  {inst} {reg_src0}, {reg_src1}, 0
  addi x3, x3, 0b0001
{id_a}:
  addi x3, x3, 0b0010
  sub {reg_src0}, {reg_src0}, x4
  csrw proc2mngr, x3 > 0b0010
  csrw proc2mngr, {reg_src0} > 0
    
  """.format(**locals())

def gen_jalr_simple_test():
  return gen_jalr_simple_template()

#-------------------------------------------------------------------------
# gen_jump_back_template
#-------------------------------------------------------------------------
# Template for jump instructions.
gen_jalr_random_template_id = 0
def gen_jalr_random_template(
  inst="jalr", reg_src0="x1", reg_src1="x10",  imm=0
):

  imm = imm - imm % 24

  global gen_jalr_random_template_id

  ctrl_seq_val = 0
  if imm == 0:
    ctrl_seq_val = 0xfffff800 + 0b10
  elif imm == 24:
    ctrl_seq_val = 0xfffff800 + 0b1000
  elif imm == 48:
    ctrl_seq_val = 0xfffff800 + 0b100000
  elif imm == 72:
    ctrl_seq_val = 0xfffff800 + 0b10000000
  elif imm == 96:
    ctrl_seq_val = 0xfffff800 + 0b1000000000

  id_a = "label_{}".format( gen_jalr_random_template_id + 1 )
  id_b = "label_{}".format( gen_jalr_random_template_id + 2 )
  id_c = "label_{}".format( gen_jalr_random_template_id + 3 )
  id_d = "label_{}".format( gen_jalr_random_template_id + 4 )
  id_e = "label_{}".format( gen_jalr_random_template_id + 5 )
  id_f = "label_{}".format( gen_jalr_random_template_id + 6 )
  gen_jalr_random_template_id += 6
  
  return """
  addi x2, x0, 0
  lui x10,              %hi[{id_a}]
  addi x10, x10,        %lo[{id_a}]
  auipc x3, 0
  addi x3, x3, 12
  jalr x1, x10, {imm}
{id_a}:
  addi x2, x2, 0b10
  addi x4, {reg_src0}, 0
  auipc x5, 0
  addi x5, x5, 12
  jal {reg_src0}, {id_f}
  addi x2, x2, 0b100
{id_b}:
  addi x2, x2, 0b1000
  addi x4, {reg_src0}, 0
  auipc x5, 0
  addi x5, x5, 12
  jal {reg_src0}, {id_f}
  addi x2, x2, 0b10000
{id_c}:
  addi x2, x2, 0b100000
  addi x4, {reg_src0}, 0
  auipc x5, 0
  addi x5, x5, 12
  jal {reg_src0}, {id_f}
  addi x2, x2, 0b1000000
{id_d}:
  addi x2, x2, 0b10000000
  addi x4, {reg_src0}, 0
  auipc x5, 0
  addi x5, x5, 12
  jal {reg_src0}, {id_f}
  addi x2, x2, 0b100000000
{id_e}:
  addi x2, x2, 0b1000000000
  addi x4, {reg_src0}, 0
  auipc x5, 0
  addi x5, x5, 12
  jal {reg_src0}, {id_f}
  addi x2, x2, 0b10000000000
{id_f}:
  addi x2, x2, 0b100000000000
  addi x6, {reg_src0}, 0
  
  sub x3, x3, x4
  sub x5, x5, x6
  csrw   proc2mngr, x2 > {ctrl_seq_val}
  csrw   proc2mngr, x3 > 0
  csrw   proc2mngr, x5 > 0
  """.format(**locals())

def gen_jalr_value_test (inst, imm):
  return gen_jalr_random_template(inst=inst, imm=imm)


#-------------------------------------------------------------------------
# gen_br2_template
#-------------------------------------------------------------------------
# Template for branch instructions with two sources. We test two forward
# branches and one backwards branch. The way we actually do the test is
# we update a register to reflect the control flow; certain bits in this
# register are set at different points in the program. Then we can check
# the control flow bits at the end to see if only the bits we expect are
# set (i.e., the program only executed those points that we expect). Note
# that test also makes sure that the instruction in the branch delay slot
# is _not_ executed.

# We currently need the id to create labels unique to this test. We might
# eventually allow local labels (e.g., 1f, 1b) as in gas.

gen_br2_template_id = 0

def gen_br2_template(
  num_nops_src0, num_nops_src1,
  reg_src0, reg_src1,
  inst, src0, src1, taken
):

  # Determine the expected control flow pattern

  if taken:
    control_flow_pattern = 0b101010
  else:
    control_flow_pattern = 0b111111

  # Create unique labels

  global gen_br2_template_id
  id_a = "label_{}".format( gen_br2_template_id + 1 )
  id_b = "label_{}".format( gen_br2_template_id + 2 )
  id_c = "label_{}".format( gen_br2_template_id + 3 )
  gen_br2_template_id += 3

  return """

    # x3 will track the control flow pattern
    addi   x3, x0, 0

    # Move src0 value into register
    csrr   {reg_src0}, mngr2proc < {src0}
    {nops_src0}

    # Move src1 value into register
    csrr   {reg_src1}, mngr2proc < {src1}
    {nops_src1}

    {inst} {reg_src0}, {reg_src1}, {id_a}  # br -.
    addi   x3, x3, 0b000001                #     |
                                           #     |
{id_b}:                                    # <---+-.
    addi   x3, x3, 0b000010                #     | |
                                           #     | |
    {inst} {reg_src0}, {reg_src1}, {id_c}  # br -+-+-.
    addi   x3, x3, 0b000100                #     | | |
                                           #     | | |
{id_a}:                                    # <---' | |
    addi   x3, x3, 0b001000                #       | |
                                           #       | |
    {inst} {reg_src0}, {reg_src1}, {id_b}  # br ---' |
    addi   x3, x3, 0b010000                #         |
                                           #         |
{id_c}:                                    # <-------'
    addi   x3, x3, 0b100000                #

    # Check the control flow pattern
    csrw   proc2mngr, x3 > {control_flow_pattern}

  """.format(
    nops_src0 = gen_nops(num_nops_src0),
    nops_src1 = gen_nops(num_nops_src1),
    **locals()
  )

#-------------------------------------------------------------------------
# gen_br2_src1_dep_test
#-------------------------------------------------------------------------
# Test the source 1 bypass paths by varying how many nops are inserted
# between writing the src1 register and reading this register in the
# instruction under test.

def gen_br2_src1_dep_test( num_nops, inst, src0, src1, taken ):
  return gen_br2_template( 8-num_nops, num_nops, "x1", "x2",
                           inst, src0, src1, taken )

#-------------------------------------------------------------------------
# gen_br2_src0_dep_test
#-------------------------------------------------------------------------
# Test the source 0 bypass paths by varying how many nops are inserted
# between writing the src0 register and reading this register in the
# instruction under test.

def gen_br2_src0_dep_test( num_nops, inst, src0, src1, result ):
  return gen_br2_template( num_nops, 0, "x1", "x2",
                           inst, src0, src1, result )

#-------------------------------------------------------------------------
# gen_br2_srcs_dep_test
#-------------------------------------------------------------------------
# Test both source bypass paths at the same time by varying how many nops
# are inserted between writing both src registers and reading both
# registers in the instruction under test.

def gen_br2_srcs_dep_test( num_nops, inst, src0, src1, result ):
  return gen_br2_template( 0, num_nops, "x1", "x2",
                           inst, src0, src1, result )

#-------------------------------------------------------------------------
# gen_br2_src0_eq_src1_test
#-------------------------------------------------------------------------
# Test situation where the src register specifiers are the same.

def gen_br2_src0_eq_src1_test( inst, src, result ):
  return gen_br2_template( 0, 0, "x1", "x1",
                                 inst, src, src, result )

#-------------------------------------------------------------------------
# gen_br2_value_test
#-------------------------------------------------------------------------
# Test the correct branch resolution based on various source values.

def gen_br2_value_test( inst, src0, src1, taken ):
  return gen_br2_template( 0, 0, "x1", "x2", inst, src0, src1, taken )

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

#-------------------------------------------------------------------------
# gen_ld_template
#-------------------------------------------------------------------------
# Template for load instructions. We first write the base register before
# executing the instruction under test. We parameterize the number of
# nops after writing the base register and the instruction under test to
# enable using this template for testing various bypass paths. We also
# parameterize the register specifiers to enable using this template to
# test situations where the base register is equal to the destination
# register.

def gen_ld_template(
  num_nops_base, num_nops_dest,
  reg_base,
  inst, offset, base, result
):
  return """

    # Move base value into register
    csrr {reg_base}, mngr2proc < {base}
    {nops_base}

    # Instruction under test
    {inst} x3, {offset}({reg_base})
    {nops_dest}

    # Check the result
    csrw proc2mngr, x3 > {result}

  """.format(
    nops_base = gen_nops(num_nops_base),
    nops_dest = gen_nops(num_nops_dest),
    **locals()
  )

#-------------------------------------------------------------------------
# gen_ld_dest_dep_test
#-------------------------------------------------------------------------
# Test the destination bypass path by varying how many nops are
# inserted between the instruction under test and reading the destination
# register with a csrr instruction.

def gen_ld_dest_dep_test( num_nops, inst, base, result ):
  return gen_ld_template( 8, num_nops, "x1", inst, 0, base, result )

#-------------------------------------------------------------------------
# gen_ld_base_dep_test
#-------------------------------------------------------------------------
# Test the base register bypass paths by varying how many nops are
# inserted between writing the base register and reading this register in
# the instruction under test.

def gen_ld_base_dep_test( num_nops, inst, base, result ):
  return gen_ld_template( num_nops, 0, "x1", inst, 0, base, result )

#-------------------------------------------------------------------------
# gen_ld_base_eq_dest_test
#-------------------------------------------------------------------------
# Test situation where the base register specifier is the same as the
# destination register specifier.

def gen_ld_base_eq_dest_test( inst, base, result ):
  return gen_ld_template( 0, 0, "x3", inst, 0, base, result )

#-------------------------------------------------------------------------
# gen_ld_value_test
#-------------------------------------------------------------------------
# Test the actual operation of a register-register instruction under
# test. We assume that bypassing has already been tested.

def gen_ld_value_test( inst, offset, base, result ):
  return gen_ld_template( 0, 0, "x1", inst, offset, base, result )

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

#-------------------------------------------------------------------------
# gen_st_baseSrc_template (self_defined)
#-------------------------------------------------------------------------
# Template for store instructions. We first write the base and src 
# registers before executing the instruction under test. We parameterized
# number of nops after writing the base register and the src register as
# well as the instruction under test to enable using this template for
# testing various bypass paths. We also parameterize the register 
# specifiers to enable using this template to test situations where
# the base register is equal to the destination register.
# Since we have test bypass paths/stalling for lw, we don't need 
# to add nops between lw and csrw.

def gen_st_baseSrc_template(
  num_nops_base, num_nops_src, num_nops_dest,
  reg_base, reg_src,
  inst, offset, base, src, result
):
  return """

    # Move base value into register
    csrr {reg_base}, mngr2proc < {base}
    {nops_base}

    # Move src value into register
    csrr {reg_src}, mngr2proc < {src}
    {nops_src}

    # Instruction under test
    {inst} {reg_src}, {offset}({reg_base})
    {nops_dest}

    # Check the result
    lw x3, {offset}({reg_base})
    csrw proc2mngr, x3 > {result}

  """.format(
    nops_base = gen_nops(num_nops_base),
    nops_src  = gen_nops(num_nops_src),
    nops_dest = gen_nops(num_nops_dest),
    **locals()
  )

#-------------------------------------------------------------------------
# gen_st_srcBase_template (self_defined)
#-------------------------------------------------------------------------
# Similar to the above template, except that we reverse the order in
# which we write the base and src register

def gen_st_srcBase_template(
  num_nops_base, num_nops_src, num_nops_dest,
  reg_base, reg_src,
  inst, offset, base, src, result
):
  return """

    # Move src value into register
    csrr {reg_src}, mngr2proc < {src}
    {nops_src}

    # Move base value into register
    csrr {reg_base}, mngr2proc < {base}
    {nops_base}

    # Instruction under test
    {inst} {reg_src}, {offset}({reg_base})
    {nops_dest}

    # Check the result
    lw x3, {offset}({reg_base})
    csrw proc2mngr, x3 > {result}

  """.format(
    nops_base = gen_nops(num_nops_base),
    nops_src  = gen_nops(num_nops_src),
    nops_dest = gen_nops(num_nops_dest),
    **locals()
  )

#-------------------------------------------------------------------------
# gen_st_dest_dep_test
#-------------------------------------------------------------------------
# Test the destination bypass path by varying how many nops are
# inserted between the instruction under test and reading the destination
# register. Note that the vaue of src is the result that we want.
# So we set the result argument to src

def gen_st_dest_dep_test( num_nops, inst, base, src ):
  return gen_st_baseSrc_template( 0, 8, num_nops, "x1", "x2",
                                inst, 0, base, src, src )

#-------------------------------------------------------------------------
# gen_st_base_dep_test
#-------------------------------------------------------------------------
# Test the base bypass paths by varying how many nops are inserted
# between writing the base register and reading this register in the
# instruction under test.

def gen_st_base_dep_test( num_nops, inst, base, src ):
  return gen_st_baseSrc_template( 8-num_nops, num_nops, 0, "x1", "x2",
                                inst, 0, base, src, src )

#-------------------------------------------------------------------------
# gen_st_src_dep_test
#-------------------------------------------------------------------------
# Test the src bypass paths by varying how many nops are inserted
# between writing the src register and reading this register in the
# instruction under test.

def gen_st_src_dep_test( num_nops, inst, base, src):
  return gen_st_srcBase_template( num_nops, 8-num_nops, 0, "x1", "x2",
                                inst, 0, base, src, src )

#-------------------------------------------------------------------------
# gen_st_baseAndSrc_dep_test
#-------------------------------------------------------------------------
# Test both bypass paths by varying how many nops are inserted
# between writing the base and src register and reading both register in the
# instruction under test.

def gen_st_baseAndSrc_dep_test( num_nops, inst, base, src ):
  return gen_st_baseSrc_template( 0, num_nops, 0, "x1", "x2",
                                inst, 0, base, src, src )

#-------------------------------------------------------------------------
# gen_st_base_eq_dest_test
#-------------------------------------------------------------------------
# Test situation where the base register specifier is the same as the
# destination register specifier.

def gen_st_base_eq_dest_test( inst, base, src ):
  return gen_st_baseSrc_template( 0, 0, 0, "x3", "x2",
                                inst, 0, base, src, src )

#-------------------------------------------------------------------------
# gen_st_src_eq_dest_test
#-------------------------------------------------------------------------
# Test situation where the src1 register specifier is the same as the
# destination register specifier.

def gen_st_src_eq_dest_test( inst, base, src ):
  return gen_st_baseSrc_template( 0, 0, 0, "x1", "x3",
                                inst, 0, base, src, src )

#-------------------------------------------------------------------------
# gen_st_base_eq_src_test
#-------------------------------------------------------------------------
# Test situation where the base register specifier is the same as the
# src register specifier.

def gen_st_base_eq_src_test( inst, base, src ):
  return gen_st_baseSrc_template( 0, 0, 0, "x1", "x1",
                                inst, 0, base, src, src )

#-------------------------------------------------------------------------
# gen_st_baseAndSrc_eq_dest_test
#-------------------------------------------------------------------------
# Test situation where all three register specifiers are the same.

def gen_st_baseAndSrc_eq_dest_test( inst, base, src ):
  return gen_st_baseSrc_template( 0, 0, 0, "x3", "x3",
                                inst, 0, base, src, src )

#-------------------------------------------------------------------------
# gen_st_value_test
#-------------------------------------------------------------------------
# Test the actual operation of a store word instruction under
# test. We assume that bypassing has already been tested.

def gen_st_value_test( inst, offset, base, src ):
  return gen_st_baseSrc_template( 0, 0, 0, "x1", "x2",
                                inst, offset, base, src, src )

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


#=========================================================================
# TestHarness
#=========================================================================

class TestHarness (Model):

  #-----------------------------------------------------------------------
  # constructor
  #-----------------------------------------------------------------------

  def __init__( s, ProcModel, src_delay, sink_delay,
                              mem_stall_prob, mem_latency ):

    s.src    = TestSource    ( 32, [], src_delay  )
    s.sink   = TestSink      ( 32, [], sink_delay )
    s.proc   = ProcModel     ()
    s.mem    = TestMemory    ( MemMsg4B(), 2, mem_stall_prob, mem_latency )

    # Processor <-> Proc/Mngr

    s.connect( s.proc.mngr2proc, s.src.out         )
    s.connect( s.proc.proc2mngr, s.sink.in_        )

    # Processor <-> Memory

    s.connect( s.proc.imemreq,   s.mem.reqs[0]     )
    s.connect( s.proc.imemresp,  s.mem.resps[0]    )
    s.connect( s.proc.dmemreq,   s.mem.reqs[1]     )
    s.connect( s.proc.dmemresp,  s.mem.resps[1]    )

  #-----------------------------------------------------------------------
  # load
  #-----------------------------------------------------------------------

  def load( self, mem_image ):

    # Iterate over the sections

    sections = mem_image.get_sections()
    for section in sections:

      # For .mngr2proc sections, copy section into mngr2proc src

      if section.name == ".mngr2proc":
        for i in xrange(0,len(section.data),4):
          bits = struct.unpack_from("<I",buffer(section.data,i,4))[0]
          self.src.src.msgs.append( Bits(32,bits) )

      # For .proc2mngr sections, copy section into proc2mngr_ref src

      elif section.name == ".proc2mngr":
        for i in xrange(0,len(section.data),4):
          bits = struct.unpack_from("<I",buffer(section.data,i,4))[0]
          self.sink.sink.msgs.append( Bits(32,bits) )

      # For all other sections, simply copy them into the memory

      else:
        start_addr = section.addr
        stop_addr  = section.addr + len(section.data)
        self.mem.mem[start_addr:stop_addr] = section.data

  #-----------------------------------------------------------------------
  # cleanup
  #-----------------------------------------------------------------------

  def cleanup( s ):
    del s.mem.mem[:]

  #-----------------------------------------------------------------------
  # done
  #-----------------------------------------------------------------------

  def done( s ):
    return s.src.done and s.sink.done

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return s.src.line_trace()  + " > " + \
           s.proc.line_trace() + "|" + \
           s.mem.line_trace()  + " > " + \
           s.sink.line_trace()

#=========================================================================
# run_test
#=========================================================================

def run_test( ProcModel, gen_test, src_delay=0, sink_delay=0,
                                   mem_stall_prob=0, mem_latency=0,
                                   max_cycles=5000 ):

  # Instantiate and elaborate the model

  model = TestHarness( ProcModel, src_delay, sink_delay,
                                  mem_stall_prob, mem_latency  )
  model.elaborate()

  # Assemble the test program

  mem_image = assemble( gen_test() )

  # Load the program into the model

  model.load( mem_image )

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Run the simulation

  print()

  sim.reset()
  while not model.done() and sim.ncycles < max_cycles:
    sim.print_line_trace()
    sim.cycle()

  # Force a test failure if we timed out

  assert sim.ncycles < max_cycles

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

  model.cleanup()

