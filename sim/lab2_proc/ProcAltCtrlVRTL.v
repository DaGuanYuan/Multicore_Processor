//=========================================================================
// 5-Stage Bypassing Pipelined Processor Control
//=========================================================================

`ifndef LAB2_PROC_PIPELINED_PROC_ALT_CTRL_V
`define LAB2_PROC_PIPELINED_PROC_ALT_CTRL_V

`include "vc/trace.v"

`include "lab2_proc/TinyRV2InstVRTL.v"

module lab2_proc_ProcAltCtrlVRTL
(
  input  logic        clk,
  input  logic        reset,

  // Instruction Memory Port

  output logic        imemreq_val,
  input  logic        imemreq_rdy,

  input  logic        imemresp_val,
  output logic        imemresp_rdy,

  output logic        imemresp_drop,

  // Data Memory Port

  output logic [2:0]  dmemreq_type,

  output logic        dmemreq_val,
  input  logic        dmemreq_rdy,

  input  logic        dmemresp_val,
  output logic        dmemresp_rdy,

  // mngr communication port

  input  logic        mngr2proc_val,
  output logic        mngr2proc_rdy,

  output logic        proc2mngr_val,
  input  logic        proc2mngr_rdy,

  // control signals (ctrl->dpath)

  output logic        reg_en_F,
  output logic [1:0]  pc_sel_F,

  output logic        reg_en_D,
  output logic        op1_sel_D,
  output logic [1:0]  op2_sel_D,
  output logic [1:0]  csrr_sel_D,
  output logic [2:0]  imm_type_D,
  output logic        imul_req_val_D,
  input  logic        imul_req_rdy_D,
  output logic [1:0]  op1_byp_sel_D,
  output logic [1:0]  op2_byp_sel_D,
  input  logic        imul_resp_val_X,
  output logic        imul_resp_rdy_X,

  output logic        reg_en_X,
  output logic [3:0]  alu_fn_X,

  output logic        reg_en_M,
  output logic [1:0]  ex_result_sel_X,
  output logic        wb_result_sel_M,

  output logic        reg_en_W,
  output logic [4:0]  rf_waddr_W,
  output logic        rf_wen_W,

  // status signals (dpath->ctrl)

  input  logic [31:0] inst_D,
  input  logic        br_cond_eq_X,
  input  logic        br_cond_lt_X,
  input  logic        br_cond_ltu_X,

  output logic        stats_en_wen_W,

  output logic        commit_inst

);

  //----------------------------------------------------------------------
  // Notes
  //----------------------------------------------------------------------
  // We follow this principle to organize code for each pipeline stage in
  // the control unit.  Register enable logics should always at the
  // beginning. It followed by pipeline registers. Then logic that is not
  // dependent on stall or squash signals. Then logic that is dependent
  // on stall or squash signals. At the end there should be signals meant
  // to be passed to the next stage in the pipeline.

  //----------------------------------------------------------------------
  // Valid, stall, and squash signals
  // ----------------------------------------------------------------------
  // We use valid signal to indicate if the instruction is valid.  An
  // instruction can become invalid because of being squashed or
  // stalled. Notice that invalid instructions are microarchitectural
  // events, they are different from archtectural no-ops. We must be
  // careful about control signals that might change the state of the
  // processor. We should always AND outgoing control signals with valid
  // signal.

  logic val_F;
  logic val_D;
  logic val_X;
  logic val_M;
  logic val_W;

  // Managing the stall and squash signals is one of the most important,
  // yet also one of the most complex, aspects of designing a pipelined
  // processor. We will carefully use four signals per stage to manage
  // stalling and squashing: ostall_A, osquash_A, stall_A, and squash_A.
  //
  // We denote the stall signals _originating_ from stage A as
  // ostall_A. For example, if stage A can stall due to a pipeline
  // harzard, then ostall_A would need to factor in the stalling
  // condition for this pipeline harzard.

  logic ostall_F;  // can ostall due to imemresp_val
  logic ostall_D;  // can ostall due to mngr2proc_val or other hazards
  logic ostall_X;  // can ostall due to dmemreq_rdy
  logic ostall_M;  // can ostall due to dmemresp_val
  logic ostall_W;  // can ostall due to proc2mngr_rdy

  // The stall_A signal should be used to indicate when stage A is indeed
  // stalling. stall_A will be a function of ostall_A and all the ostall
  // signals of stages in front of it in the pipeline.

  logic stall_F;
  logic stall_D;
  logic stall_X;
  logic stall_M;
  logic stall_W;

  // We denote the squash signals _originating_ from stage A as
  // osquash_A. For example, if stage A needs to squash the stages behind
  // A in the pipeline, then osquash_A would need to factor in this
  // squash condition.

  logic osquash_D; // can osquash due to unconditional jumps
  logic osquash_X; // can osquash due to taken branches

  // The squash_A signal should be used to indicate when stage A is being
  // squashed. squash_A will _not_ be a function of osquash_A, since
  // osquash_A means to squash the stages _behind_ A in the pipeline, but
  // not to squash A itself.

  logic squash_F;
  logic squash_D;

  //----------------------------------------------------------------------
  // F stage
  //----------------------------------------------------------------------

  // Register enable logic

  assign reg_en_F = !stall_F || squash_F;

  // Pipeline registers

  always_ff @( posedge clk ) begin
    if ( reset )
      val_F <= 1'b0;
    else if ( reg_en_F )
      val_F <= 1'b1;
  end

  // forward declaration for PC sel

  logic       pc_redirect_X;
  logic [1:0] pc_sel_D;
  logic [1:0] pc_sel_X;

  // PC select logic

  always_comb begin
    if ( pc_redirect_X )       // If a branch is taken in X stage
      pc_sel_F = pc_sel_X;        // Use pc from X
    else if ( pc_redirect_D )            // If instruction in D is jump
      pc_sel_F = pc_sel_D;
    else
      pc_sel_F = 2'b0;         // Use pc+4
  end

  // ostall due to the imem response not valid.

  assign ostall_F = val_F && !imemresp_val;

  // stall and squash in F

  assign stall_F  = val_F && ( ostall_F  || ostall_D || ostall_X || ostall_M || ostall_W );
  assign squash_F = val_F && ( osquash_D || osquash_X );

  // We drop the mem response when we are getting squashed

  assign imemresp_drop = squash_F;

  // imem is very special. Actually imem requests are sent before the F
  // stage. Note that we need to factor in reset to the imemreq_val
  // signal because we don't want to send out imem request when we are
  // resetting.

  assign imemreq_val  = ( !stall_F || squash_F ) && !reset;
  assign imemresp_rdy = !stall_F || squash_F;

  // Valid signal for the next stage (stage D)

  logic  next_val_F;
  assign next_val_F = val_F && !stall_F && !squash_F;

  //----------------------------------------------------------------------
  // D stage
  //----------------------------------------------------------------------

  // Register enable logic

  assign reg_en_D = !stall_D || squash_D;

  // Pipline registers

  always_ff @( posedge clk ) begin
    if ( reset )
      val_D <= 1'b0;
    else if ( reg_en_D )
      val_D <= next_val_F;
  end

  // Handle jump instructions
  logic  pc_redirect_D;
  always_comb begin
    if ( val_D && ( br_type_D == jmp_jal ) ) begin
      pc_redirect_D = 1'b1;
      pc_sel_D      = 2'd2;          // use jal target
    end else begin
      pc_redirect_D = 1'b0;
      pc_sel_D      = 2'b0;          // use pc+4
    end
  end

  // Parse instruction fields

  logic   [4:0] inst_rd_D;
  logic   [4:0] inst_rs1_D;
  logic   [4:0] inst_rs2_D;
  logic   [11:0] inst_csr_D;

  rv2isa_InstUnpack inst_unpack
  (
    .inst     (inst_D),
    .opcode   (),
    .rd       (inst_rd_D),
    .rs1      (inst_rs1_D),
    .rs2      (inst_rs2_D),
    .funct3   (),
    .funct7   (),
    .csr      (inst_csr_D)
  );

  // Generic Parameters -- yes or no

  localparam n = 1'd0;
  localparam y = 1'd1;

  // Register specifiers

  localparam rx = 5'bx;   // don't care
  localparam r0 = 5'd0;   // zero
  localparam rL = 5'd31;  // for jal

  // Branch type

  localparam br_x     = 4'bx; // Don't care
  localparam br_na    = 4'd0; // No branch
  localparam br_bne   = 4'd1; // bne
  localparam br_beq   = 4'd2; // beq
  localparam br_blt   = 4'd3; // blt
  localparam br_bltu  = 4'd4; // bltu
  localparam br_bge   = 4'd5; // bge
  localparam br_bgeu  = 4'd6; // bgeu

  // Jump type
  localparam jmp_jal  = 4'd7; // jal
  localparam jmp_jalr = 4'd8; // jalr

  // Operand 1 Mux Select

  localparam bm_x     = 2'bx; // Don't care
  localparam bm_rf    = 2'd0; // Use data from register file
  localparam bm_imm   = 2'd1; // Use sign-extended immediate
  localparam bm_csr   = 2'd2; // Use from mngr data

  // Operand 0 Mux Select
  localparam am_x     = 1'bx; // Don't care
  localparam am_rf    = 1'b0; // Use data from register file
  localparam am_pc    = 1'b1; // Use PC

  // ALU Function

  localparam alu_x    = 4'bx;
  localparam alu_add  = 4'd0;
  localparam alu_sub  = 4'd1;
  localparam alu_and  = 4'd2;
  localparam alu_or   = 4'd3;
  localparam alu_xor  = 4'd4;
  localparam alu_slt  = 4'd5;
  localparam alu_sltu = 4'd6;
  localparam alu_sra  = 4'd7;
  localparam alu_srl  = 4'd8;
  localparam alu_sll  = 4'd9;
  localparam alu_cp0  = 4'd11;
  localparam alu_cp1  = 4'd12;

  // Immediate Type
  localparam imm_x    = 3'bx;
  localparam imm_i    = 3'd0;
  localparam imm_s    = 3'd1;
  localparam imm_b    = 3'd2;
  localparam imm_u    = 3'd3;
  localparam imm_j    = 3'd4;

  // Memory Request Type

  localparam nr       = 2'd0; // No request
  localparam ld       = 2'd1; // Load
  localparam st       = 2'd2; // Store

  // Execution Result Mux Select
  localparam xm_x     = 2'bx; // Don't care
  localparam xm_pc    = 2'd0; // PC + 4
  localparam xm_alu   = 2'd1; // alu result
  localparam xm_mul   = 2'd2; // imul result

  // Writeback Mux Select

  localparam wm_x     = 1'bx; // Don't care
  localparam wm_ex    = 1'd0; // Use execution result
  localparam wm_m     = 1'd1; // Use data memory response

  // Instruction Decode

  logic       inst_val_D;
  logic [3:0] br_type_D;
  logic       rs1_en_D;
  logic       rs2_en_D;
  logic [3:0] alu_fn_D;
  logic [1:0] dmemreq_type_D;
  logic [1:0] ex_result_sel_D;
  logic       wb_result_sel_D;
  logic       rf_wen_pending_D;
  logic       csrr_D;
  logic       csrw_D;
  logic       proc2mngr_val_D;
  logic       mngr2proc_rdy_D;
  logic       stats_en_wen_D;

  task cs
  (
    input logic       cs_inst_val,
    input logic [3:0] cs_br_type,
    input logic [2:0] cs_imm_type,
    input logic       cs_rs1_en,
    input logic       cs_op1_sel,
    input logic [1:0] cs_op2_sel,
    input logic       cs_rs2_en,
    input logic [3:0] cs_alu_fn,
    input logic [1:0] cs_dmemreq_type,
    input logic [1:0] cs_ex_result_sel_D,
    input logic       cs_wb_result_sel,
    input logic       cs_rf_wen_pending,
    input logic       cs_csrr,
    input logic       cs_csrw
  );
  begin
    inst_val_D            = cs_inst_val;
    br_type_D             = cs_br_type;
    imm_type_D            = cs_imm_type;
    rs1_en_D              = cs_rs1_en;
    op1_sel_D             = cs_op1_sel;
    op2_sel_D             = cs_op2_sel;
    rs2_en_D              = cs_rs2_en;
    alu_fn_D              = cs_alu_fn;
    dmemreq_type_D        = cs_dmemreq_type;
    ex_result_sel_D       = cs_ex_result_sel_D;
    wb_result_sel_D       = cs_wb_result_sel;
    rf_wen_pending_D      = cs_rf_wen_pending;
    csrr_D                = cs_csrr;
    csrw_D                = cs_csrw;
  end
  endtask

  // Control signals table

  always_comb begin

    casez ( inst_D )

      //                           br      imm  rs1  op1      op2    rs2 alu       dmm  exreslt wbmux rf
      //                       val type    type  en  muxsel   muxsel  en fn        typ  sel     sel   wen csrr csrw
      `RV2ISA_INST_NOP     :cs( y, br_na,   imm_x, n, am_x ,   bm_x,   n, alu_x,    nr,  xm_x  , wm_ex, n,  n,   n    );
      `RV2ISA_INST_ADD     :cs( y, br_na,   imm_x, y, am_rf,   bm_rf,  y, alu_add,  nr,  xm_alu, wm_ex, y,  n,   n    );
      `RV2ISA_INST_SUB     :cs( y, br_na,   imm_x, y, am_rf,   bm_rf,  y, alu_sub,  nr,  xm_alu, wm_ex, y,  n,   n    );
      `RV2ISA_INST_AND     :cs( y, br_na,   imm_x, y, am_rf,   bm_rf,  y, alu_and,  nr,  xm_alu, wm_ex, y,  n,   n    );
      `RV2ISA_INST_OR      :cs( y, br_na,   imm_x, y, am_rf,   bm_rf,  y, alu_or ,  nr,  xm_alu, wm_ex, y,  n,   n    );
      `RV2ISA_INST_XOR     :cs( y, br_na,   imm_x, y, am_rf,   bm_rf,  y, alu_xor,  nr,  xm_alu, wm_ex, y,  n,   n    );
      `RV2ISA_INST_SLT     :cs( y, br_na,   imm_x, y, am_rf,   bm_rf,  y, alu_slt,  nr,  xm_alu, wm_ex, y,  n,   n    );    
      `RV2ISA_INST_SLTU    :cs( y, br_na,   imm_x, y, am_rf,   bm_rf,  y, alu_sltu, nr,  xm_alu, wm_ex, y,  n,   n    ); 
      `RV2ISA_INST_SRA     :cs( y, br_na,   imm_x, y, am_rf,   bm_rf,  y, alu_sra,  nr,  xm_alu, wm_ex, y,  n,   n    );    
      `RV2ISA_INST_SRL     :cs( y, br_na,   imm_x, y, am_rf,   bm_rf,  y, alu_srl,  nr,  xm_alu, wm_ex, y,  n,   n    );  
      `RV2ISA_INST_SLL     :cs( y, br_na,   imm_x, y, am_rf,   bm_rf,  y, alu_sll,  nr,  xm_alu, wm_ex, y,  n,   n    );  
      `RV2ISA_INST_MUL     :cs( y, br_na,   imm_x, y, am_rf,   bm_rf,  y, alu_x,    nr,  xm_mul, wm_ex, y,  n,   n    );

      // imm instructions
      `RV2ISA_INST_ADDI    :cs( y, br_na,   imm_i, y, am_rf,   bm_imm, n, alu_add,  nr,  xm_alu, wm_ex,  y,  n,   n    );  
      `RV2ISA_INST_ORI     :cs( y, br_na,   imm_i, y, am_rf,   bm_imm, n, alu_or ,  nr,  xm_alu, wm_ex,  y,  n,   n    );  
      `RV2ISA_INST_ANDI    :cs( y, br_na,   imm_i, y, am_rf,   bm_imm, n, alu_and,  nr,  xm_alu, wm_ex,  y,  n,   n    );  
      `RV2ISA_INST_XORI    :cs( y, br_na,   imm_i, y, am_rf,   bm_imm, n, alu_xor,  nr,  xm_alu, wm_ex,  y,  n,   n    );  
      `RV2ISA_INST_SLTI    :cs( y, br_na,   imm_i, y, am_rf,   bm_imm, n, alu_slt,  nr,  xm_alu, wm_ex,  y,  n,   n    );  
      `RV2ISA_INST_SLTIU   :cs( y, br_na,   imm_i, y, am_rf,   bm_imm, n, alu_sltu, nr,  xm_alu, wm_ex,  y,  n,   n    );  
      `RV2ISA_INST_SRAI    :cs( y, br_na,   imm_i, y, am_rf,   bm_imm, n, alu_sra , nr,  xm_alu, wm_ex,  y,  n,   n    );  
      `RV2ISA_INST_SRLI    :cs( y, br_na,   imm_i, y, am_rf,   bm_imm, n, alu_srl,  nr,  xm_alu, wm_ex,  y,  n,   n    );  
      `RV2ISA_INST_SLLI    :cs( y, br_na,   imm_i, y, am_rf,   bm_imm, n, alu_sll,  nr,  xm_alu, wm_ex,  y,  n,   n    );  
      `RV2ISA_INST_LUI     :cs( y, br_na,   imm_u, n, am_x ,   bm_imm, n, alu_cp1,  nr,  xm_alu, wm_ex,  y,  n,   n    );
      `RV2ISA_INST_AUIPC   :cs( y, br_na,   imm_u, n, am_pc,   bm_imm, n, alu_add,  nr,  xm_alu, wm_ex,  y,  n,   n    );
         
      // Mem instructions
      `RV2ISA_INST_LW      :cs( y, br_na,   imm_i, y, am_rf,   bm_imm, n, alu_add,  ld,  xm_x,   wm_m,   y,  n,   n    );
      `RV2ISA_INST_SW      :cs( y, br_na,   imm_s, y, am_rf,   bm_imm, y, alu_add,  st,  xm_x,   wm_x,   n,  n,   n    );

      // Jump instructions
      `RV2ISA_INST_JAL     :cs( y, jmp_jal, imm_j, n, am_pc,   bm_imm, n, alu_x,    nr,  xm_pc,  wm_ex,  y,  n,   n    );
      `RV2ISA_INST_JALR    :cs( y, jmp_jalr,imm_i, y, am_rf,   bm_imm, n, alu_add,  nr,  xm_pc,  wm_ex,  y,  n,   n    );

      // Branch instructions
      `RV2ISA_INST_BNE     :cs( y, br_bne,  imm_b, y, am_rf,   bm_rf,  y, alu_x,    nr,  xm_x,   wm_x,   n,  n,   n    );
      `RV2ISA_INST_BEQ     :cs( y, br_beq,  imm_b, y, am_rf,   bm_rf,  y, alu_x,    nr,  xm_x,   wm_x,   n,  n,   n    );
      `RV2ISA_INST_BLT     :cs( y, br_blt,  imm_b, y, am_rf,   bm_rf,  y, alu_x,    nr,  xm_x,   wm_x,   n,  n,   n    );
      `RV2ISA_INST_BLTU    :cs( y, br_bltu, imm_b, y, am_rf,   bm_rf,  y, alu_x,    nr,  xm_x,   wm_x,   n,  n,   n    );
      `RV2ISA_INST_BGE     :cs( y, br_bge , imm_b, y, am_rf,   bm_rf,  y, alu_x,    nr,  xm_x,   wm_x,   n,  n,   n    );
      `RV2ISA_INST_BGEU    :cs( y, br_bgeu, imm_b, y, am_rf,   bm_rf,  y, alu_x,    nr,  xm_x,   wm_x,   n,  n,   n    );
      
      `RV2ISA_INST_CSRR    :cs( y, br_na,  imm_i, n, am_x,     bm_csr, n, alu_cp1,   nr,  xm_alu, wm_ex,  y,  y,   n    );
      `RV2ISA_INST_CSRW    :cs( y, br_na,  imm_i, y, am_rf,    bm_rf,  n, alu_cp0,   nr,  xm_alu, wm_ex,  n,  n,   y    );

      //''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''
      // Add more instructions to the control signal table
      //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

      default              :cs( n, br_x,  imm_x, n,   am_x,   bm_x,    n, alu_x,   nr,  xm_x,    wm_x,  n,  n,   n    );

    endcase
  end // always_comb

  logic [4:0] rf_waddr_D;
  assign rf_waddr_D = inst_rd_D;

  // csrr and csrw logic

  always_comb begin
    proc2mngr_val_D  = 1'b0;
    mngr2proc_rdy_D  = 1'b0;
    csrr_sel_D       = 2'h0;
    stats_en_wen_D   = 1'b0;

    if ( csrw_D && inst_csr_D == `RV2ISA_CPR_PROC2MNGR )
      proc2mngr_val_D    = 1'b1;
    if ( csrr_D && inst_csr_D == `RV2ISA_CPR_MNGR2PROC )
      mngr2proc_rdy_D  = 1'b1;
    if ( csrw_D && inst_csr_D == `RV2ISA_CPR_STATS_EN )
      stats_en_wen_D  = 1'b1;
    if ( csrr_D && inst_csr_D == `RV2ISA_CPR_NUMCORES )
      csrr_sel_D       = 2'h1;
    if ( csrr_D && inst_csr_D == `RV2ISA_CPR_COREID )
      csrr_sel_D       = 2'h2;
  end

  // mngr2proc_rdy signal for csrr instruction

  assign mngr2proc_rdy  = val_D && !stall_D && mngr2proc_rdy_D;

  logic  ostall_mngr2proc_D;
  assign ostall_mngr2proc_D = val_D && mngr2proc_rdy_D && !mngr2proc_val;

  // Genertae imul valid signal
  assign imul_req_val_D = val_D && !stall_D && (ex_result_sel_D == xm_mul);
  
  // ostall if mul is not ready
  logic ostall_imul_rdy_D;
  assign ostall_imul_rdy_D = val_D && !imul_req_rdy_D;
  
  // bypass if write address in X matches rs1 in D

  logic  bypass_waddr_X_rs1_D;
  assign bypass_waddr_X_rs1_D
    = val_D && rs1_en_D && val_X && rf_wen_pending_X
      && ( inst_rs1_D == rf_waddr_X ) && ( rf_waddr_X != 5'd0 );

  // bypass if write address in M matches rs1 in D

  logic  bypass_waddr_M_rs1_D;
  assign bypass_waddr_M_rs1_D
    = val_D && rs1_en_D && val_M && rf_wen_pending_M
      && ( inst_rs1_D == rf_waddr_M ) && ( rf_waddr_M != 5'd0 )
      && (dmemreq_type_X != ld);

  // bypass if write address in W matches rs1 in D

  logic  bypass_waddr_W_rs1_D;
  assign bypass_waddr_W_rs1_D
    = val_D && rs1_en_D && val_W && rf_wen_pending_W
      && ( inst_rs1_D == rf_waddr_W ) && ( rf_waddr_W != 5'd0 );

  // bypass if write address in X matches rs2 in D

  logic  bypass_waddr_X_rs2_D;
  assign bypass_waddr_X_rs2_D
    = val_D && rs2_en_D && val_X && rf_wen_pending_X
      && ( inst_rs2_D == rf_waddr_X ) && ( rf_waddr_X != 5'd0 );

  // bypass if write address in M matches rs2 in D

  logic  bypass_waddr_M_rs2_D;
  assign bypass_waddr_M_rs2_D
    = val_D && rs2_en_D && val_M && rf_wen_pending_M
      && ( inst_rs2_D == rf_waddr_M ) && ( rf_waddr_M != 5'd0 );

  // bypass if write address in W matches rs2 in D

  logic  bypass_waddr_W_rs2_D;
  assign bypass_waddr_W_rs2_D
    = val_D && rs2_en_D && val_W && rf_wen_pending_W
      && ( inst_rs2_D == rf_waddr_W ) && ( rf_waddr_W != 5'd0 );

  // need to stall for one cycle for load_use case
  logic ostall_load_use_X_rs1_D;
  assign ostall_load_use_X_rs1_D 
          = val_D && rs1_en_D && val_X && rf_wen_pending_X
            && (inst_rs1_D == rf_waddr_X) && (rf_waddr_X != 5'd0)
            && (dmemreq_type_X == ld);
  
  logic ostall_load_use_X_rs2_D;
  assign ostall_load_use_X_rs2_D 
          = val_D && rs2_en_D && val_X && rf_wen_pending_X
            && (inst_rs2_D == rf_waddr_X) && (rf_waddr_X != 5'd0)
            && (dmemreq_type_X == ld || csrr_X == y);

  // Final ostall signal

  assign ostall_D = val_D && ( ostall_mngr2proc_D || ostall_imul_rdy_D || ostall_load_use_X_rs1_D || ostall_load_use_X_rs2_D);

  // osquash due to jump instruction in D stage

  assign osquash_D = val_D && !stall_D && (br_type_D == jmp_jal);

  // stall and squash in D

  assign stall_D  = val_D && ( ostall_D || ostall_X || ostall_M || ostall_W );
  assign squash_D = val_D && osquash_X;

  // Valid signal for the next stage

  logic  next_val_D;
  assign next_val_D = val_D && !stall_D && !squash_D;

  // Bypass select signal
  always_comb begin
    if (bypass_waddr_X_rs1_D) begin
      op1_byp_sel_D = 2'd1;
    end else if (bypass_waddr_M_rs1_D) begin
      op1_byp_sel_D = 2'd2;
    end else if (bypass_waddr_W_rs1_D) begin
      op1_byp_sel_D = 2'd3;
    end else begin
      op1_byp_sel_D = 2'd0;
    end

    if (bypass_waddr_X_rs2_D) begin
      op2_byp_sel_D = 2'd1;
    end else if (bypass_waddr_M_rs2_D) begin
      op2_byp_sel_D = 2'd2;
    end else if (bypass_waddr_W_rs2_D) begin
      op2_byp_sel_D = 2'd3;
    end else begin
      op2_byp_sel_D = 2'd0;
    end
  end

  //----------------------------------------------------------------------
  // X stage
  //----------------------------------------------------------------------

  // Register enable logic

  assign reg_en_X = !stall_X;

  logic [31:0] inst_X;
  logic [1:0]  dmemreq_type_X;
  logic        wb_result_sel_X;
  logic        rf_wen_pending_X;
  logic [4:0]  rf_waddr_X;
  logic        proc2mngr_val_X;
  logic        stats_en_wen_X;
  logic [3:0]  br_type_X;
  logic        csrr_X;

  // Pipeline registers

  always_ff @( posedge clk )
    if (reset) begin
      val_X           <= 1'b0;
      stats_en_wen_X  <= 1'b0;
    end else if (reg_en_X) begin
      val_X           <= next_val_D;
      rf_wen_pending_X<= rf_wen_pending_D;
      inst_X          <= inst_D;
      alu_fn_X        <= alu_fn_D;
      rf_waddr_X      <= rf_waddr_D;
      proc2mngr_val_X <= proc2mngr_val_D;
      dmemreq_type_X  <= dmemreq_type_D;
      ex_result_sel_X <= ex_result_sel_D;
      wb_result_sel_X <= wb_result_sel_D;
      stats_en_wen_X  <= stats_en_wen_D;
      br_type_X       <= br_type_D;
      csrr_X          <= csrr_D;
    end

  // branch logic, redirect PC in F if branch is taken

  always_comb begin
    if ( val_X && ( br_type_X == br_bne ) ) begin
      pc_redirect_X = !br_cond_eq_X;
      pc_sel_X      = 2'b1;          // use branch target
    end else if (val_X && (br_type_X == br_blt) ) begin
      pc_redirect_X = br_cond_lt_X;
      pc_sel_X      = 2'b1;          // use branch target
    end else if (val_X && (br_type_X == br_bge)) begin
      pc_redirect_X = !br_cond_lt_X;
      pc_sel_X      = 2'b1;          // use branch target
    end else if (val_X && (br_type_X == br_bltu)) begin
      pc_redirect_X = br_cond_ltu_X;
      pc_sel_X      = 2'b1;          // use branch target
    end else if (val_X && (br_type_X == br_bgeu)) begin
      pc_redirect_X = !br_cond_ltu_X;
      pc_sel_X      = 2'b1;          // use branch target
    end else if (val_X && (br_type_X == br_beq) ) begin
      pc_redirect_X = br_cond_eq_X;
      pc_sel_X      = 2'b1;          // use branch target
    end else if (val_X && (br_type_X == jmp_jalr)) begin
      pc_redirect_X = 1'b1;
      pc_sel_X      = 2'd3;          // use R[rs1] + imm
    end else begin
      pc_redirect_X = 1'b0;
      pc_sel_X      = 2'b0;          // use pc+4
    end
  end

  // ostall due to imul resp not ready
  // ostall due to dmemreq not ready.

  assign ostall_X = val_X && ((( dmemreq_type_X != nr ) && !dmemreq_rdy) || (!imul_resp_val_X && !imul_req_rdy_D)) ;

  // osquash due to taken branch, notice we can't osquash if current
  // stage stalls, otherwise we will send osquash twice.

  assign osquash_X = val_X && !stall_X && pc_redirect_X;

  // stall and squash used in X stage

  assign stall_X = val_X && ( ostall_X || ostall_M || ostall_W );

  // set dmemreq_val only if not stalling

  assign dmemreq_val = val_X && !stall_X && ( dmemreq_type_X != nr );

  // Valid signal for the next stage

  logic  next_val_X;
  assign next_val_X = val_X && !stall_X;

  assign dmemreq_type = (dmemreq_type_X == st)? `VC_MEM_REQ_MSG_TYPE_WRITE: `VC_MEM_REQ_MSG_TYPE_READ;

  assign imul_resp_rdy_X = val_X && !stall_X;

  //----------------------------------------------------------------------
  // M stage
  //----------------------------------------------------------------------

  // Register enable logic

  assign reg_en_M  = !stall_M;

  logic [31:0] inst_M;
  logic [1:0]  dmemreq_type_M;
  logic        rf_wen_pending_M;
  logic [4:0]  rf_waddr_M;
  logic        proc2mngr_val_M;
  logic        stats_en_wen_M;

  // Pipeline register

  always_ff @( posedge clk )
    if (reset) begin
      val_M            <= 1'b0;
      stats_en_wen_X   <= 1'b0;
    end else if (reg_en_M) begin
      val_M            <= next_val_X;
      rf_wen_pending_M <= rf_wen_pending_X;
      inst_M           <= inst_X;
      rf_waddr_M       <= rf_waddr_X;
      proc2mngr_val_M  <= proc2mngr_val_X;
      dmemreq_type_M   <= dmemreq_type_X;
      wb_result_sel_M  <= wb_result_sel_X;
      stats_en_wen_M   <= stats_en_wen_X;
    end

  // ostall due to dmemresp not valid

  assign ostall_M = val_M && ( dmemreq_type_M != nr ) && !dmemresp_val;

  // stall M

  assign stall_M = val_M && ( ostall_M || ostall_W );

  // Set dmemresp_rdy if valid and not stalling and this is a lw/sw

  assign dmemresp_rdy = val_M && !stall_M && ( dmemreq_type_M != nr );

  // Valid signal for the next stage

  logic  next_val_M;
  assign next_val_M = val_M && !stall_M;

  //----------------------------------------------------------------------
  // W stage
  //----------------------------------------------------------------------

  // Register enable logic

  assign reg_en_W = !stall_W;

  logic [31:0] inst_W;
  logic        proc2mngr_val_W;
  logic        rf_wen_pending_W;
  logic        stats_en_wen_pending_W;

  // Pipeline registers

  always_ff @( posedge clk ) begin
    if (reset) begin
      val_W            <= 1'b0;
      stats_en_wen_pending_W   <= 1'b0;
    end else if (reg_en_W) begin
      val_W            <= next_val_M;
      rf_wen_pending_W <= rf_wen_pending_M;
      inst_W           <= inst_M;
      rf_waddr_W       <= rf_waddr_M;
      proc2mngr_val_W  <= proc2mngr_val_M;
      stats_en_wen_pending_W   <= stats_en_wen_M;
    end
  end

  // write enable

  assign rf_wen_W       = val_W && rf_wen_pending_W;
  assign stats_en_wen_W = val_W && stats_en_wen_pending_W;

  // ostall due to proc2mngr

  assign ostall_W = val_W && proc2mngr_val_W && !proc2mngr_rdy;

  // stall and squash signal used in W stage

  assign stall_W = val_W && ostall_W;

  // proc2mngr port

  assign proc2mngr_val = val_W && !stall_W && proc2mngr_val_W;

  assign commit_inst = val_W && !stall_W;

endmodule

`endif

