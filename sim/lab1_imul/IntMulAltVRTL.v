//=========================================================================
// Integer Multiplier Variable-Latency Implementation
//=========================================================================

`ifndef LAB1_IMUL_INT_MUL_ALT_V
`define LAB1_IMUL_INT_MUL_ALT_V

`include "vc/trace.v"
`include "vc/muxes.v"
`include "vc/counters.v"
`include "vc/regs.v"
`include "vc/arithmetic.v"

// Macro definition of the granularity of jumping over '0's
//`define N_ZERO_TO_JUMP 2
//`define N_ZERO_TO_JUMP 3
`define N_ZERO_TO_JUMP 4
//`define N_ZERO_TO_JUMP 5
//`define N_ZERO_TO_JUMP 6
//`define N_ZERO_TO_JUMP 7

//========================================================================
// IntMulAlt Unit Dpath
//========================================================================

module IntMulAlt_UnitDpath
(
  input  logic        clk,
  input  logic        reset,

  // Data signals

  input  logic [63:0] req_msg,
  output logic [31:0] resp_msg,

  // Control signals

  input  logic        result_en,              // Enable for result register
  input  logic        a_mux_sel,              // Sel for mux in front of A reg
  input  logic        b_mux_sel,              // sel for mux in front of B reg
  input  logic        result_mux_sel,         // sel for mux in front of result reg
  input  logic        add_mux_sel,            // sel for mux in front of result

  input  logic [2:0]  shamt,                  // shift amount

  // Status signals

  output logic        b_lsb,                  // least significant bit of b

  output logic        is_b_lnsb_0             // is least n significant bits of b zero
);

  localparam c_nbits = 32;

  // Split out the a and b operands

  logic [c_nbits-1:0] req_msg_a = req_msg[ 2*c_nbits-1:c_nbits ];
  logic [c_nbits-1:0] req_msg_b = req_msg[     c_nbits-1:0     ];

  // A Mux

  logic [c_nbits-1:0] a_shift_out;
  logic [c_nbits-1:0] a_mux_out;

  vc_Mux2#(c_nbits) a_mux
  (
    .sel   (a_mux_sel),
    .in0   (req_msg_a),
    .in1   (a_shift_out),
    .out   (a_mux_out)
  );

  // A register

  logic [c_nbits-1:0] a_reg_out;

  vc_Reg#(c_nbits) a_reg
  (
    .clk   (clk),
    .d     (a_mux_out),
    .q     (a_reg_out)
  );

  // A left shifter

  vc_LeftLogicalShifter#(c_nbits, 3) a_shifter
  (
    .in    (a_reg_out),
    .out   (a_shift_out),
    .shamt (shamt)
  );

  // B Mux

  logic [c_nbits-1:0] b_shift_out;
  logic [c_nbits-1:0] b_mux_out;

  vc_Mux2#(c_nbits) b_mux
  (
    .sel   (b_mux_sel),
    .in0   (req_msg_b),
    .in1   (b_shift_out),
    .out   (b_mux_out)
  );

  // B register

  logic [c_nbits-1:0] b_reg_out;
  assign b_lsb = b_reg_out[0];
  
  // Are there n consecutive '0's?
  assign is_b_lnsb_0 = ( b_reg_out[`N_ZERO_TO_JUMP-1:0] == `N_ZERO_TO_JUMP'b0 );       // whether the four bits are all zero

  vc_Reg#(c_nbits) b_reg
  (
    .clk   (clk),
    .d     (b_mux_out),
    .q     (b_reg_out)
  );

  // B left shifter

  vc_RightLogicalShifter#(c_nbits, 3) b_shifter
  (
    .in    (b_reg_out),
    .out   (b_shift_out),
    .shamt (shamt)
  );

  // Result Mux

  logic [c_nbits-1:0] result_mux_out;
  logic [c_nbits-1:0] add_mux_out;

  vc_Mux2#(c_nbits) result_mux
  (
    .sel   (result_mux_sel),
    .in0   (add_mux_out),
    .in1   (0),
    .out   (result_mux_out)
  );

  // Result register

  logic [c_nbits-1:0] result_reg_out;

  vc_EnReg#(c_nbits) result_reg
  (
    .clk   (clk),
    .reset (reset),
    .en    (result_en),
    .d     (result_mux_out),
    .q     (result_reg_out)
  );
  
  // Adder
  logic [c_nbits-1:0] adder_out;

  vc_SimpleAdder#(c_nbits) a_result_adder
  (
    .in0(a_reg_out),
    .in1(result_reg_out),
    .out(adder_out)
  );
  
  // Adder Mux

  vc_Mux2#(c_nbits) adder_mux
  (
    .sel   (add_mux_sel),
    .in0   (result_reg_out),
    .in1   (adder_out),
    .out   (add_mux_out)
  );

  assign resp_msg = result_reg_out;

endmodule

//========================================================================
// IntMulAlt Unit Control
//========================================================================

module IntMulAlt_UnitCtrl
(
  input  logic        clk,
  input  logic        reset,

  // Dataflow signals

  input  logic        req_val,
  output logic        req_rdy,
  output logic        resp_val,
  input  logic        resp_rdy,

  // Control signals

  output  logic        result_en,             // Enable for result register
  output  logic        a_mux_sel,             // Sel for mux in front of A reg
  output  logic        b_mux_sel,             // sel for mux in front of B reg
  output  logic        result_mux_sel,        // sel for mux in front of result reg
  output  logic        add_mux_sel,           // sel for mux in front of result

  output  logic [2:0]  shamt,                 // shift amount

  // Status signals

  input   logic         b_lsb,                // least significant bit of b

  input   logic         is_b_lnsb_0           // is least n significant bits of b zero
);

  //----------------------------------------------------------------------
  // State Definitions
  //----------------------------------------------------------------------

  localparam STATE_IDLE = 2'd0;
  localparam STATE_CALC = 2'd1;
  localparam STATE_DONE = 2'd2;

  localparam INCREMENT_1      = 2'd1;
  localparam INCREMENT_CUSTOM = 3'd`N_ZERO_TO_JUMP;

  //----------------------------------------------------------------------
  // State
  //----------------------------------------------------------------------

  logic [1:0] state_reg;
  logic [1:0] state_next;

  always_ff @( posedge clk ) begin
    if ( reset ) begin
      state_reg <= STATE_IDLE;
    end
    else begin
      state_reg <= state_next;
    end
  end

  //----------------------------------------------------------------------
  // State Transitions
  //----------------------------------------------------------------------

  logic req_go;
  logic resp_go;
  logic is_calc_done;

  // Counting to 32
  logic [4:0] count;
  
  // Counting to 32
  logic is_counter_32;

  // Jumping over the '0's
  logic [2:0] increment_value;

  vc_CustomIncrementCounter#(5,0,31,3) counter
  (
    .clk(clk),
    .reset(reset),
    // Operations
    .clear(state_reg!=STATE_CALC),
    .increment(1),
    .increment_value(increment_value),
    .decrement(0),
    // Outputs
    .count(count),
    .count_is_zero(),
    .count_is_max(is_counter_32)
  );

  assign req_go       = req_val  && req_rdy;
  assign resp_go      = resp_val && resp_rdy;

  always_comb begin

    state_next = state_reg;

    case ( state_reg )

      STATE_IDLE: if ( req_go           )    state_next = STATE_CALC;
      STATE_CALC: if ( is_counter_32    )    state_next = STATE_DONE;
      STATE_DONE: if ( resp_go          )    state_next = STATE_IDLE;
      default:    state_next = 'x;

    endcase

  end

  //----------------------------------------------------------------------
  // State Outputs
  //----------------------------------------------------------------------

  // Signals for muxes

  localparam a_x          = 1'dx;
  localparam a_ld         = 1'd0;
  localparam a_shift      = 1'd1;

  localparam b_x          = 1'dx;
  localparam b_ld         = 1'd0;
  localparam b_shift      = 1'd1;

  localparam result_x     = 1'dx;
  localparam result_add   = 1'd0;
  localparam result_0     = 1'd1;

  localparam add_mux_x    = 1'dx;
  localparam add_mux_reg  = 1'd0;
  localparam add_mux_add  = 1'd1;

  localparam increment_1  = 3'd1;
  localparam increment_n  = 3'd`N_ZERO_TO_JUMP;

  localparam shift_1      = 3'd1;
  localparam shift_n      = 3'd`N_ZERO_TO_JUMP;

  task cs
  (
    input logic       cs_req_rdy,
    input logic       cs_resp_val,
    input logic       cs_a_mux_sel,
    input logic       cs_b_mux_sel,
    input logic       cs_result_mux_sel,
    input logic       cs_result_en,
    input logic       cs_add_mux_sel,

    input logic [2:0] cs_increment_value,
    input logic [2:0] cs_shamt          
  );
  begin
    req_rdy         = cs_req_rdy;
    resp_val        = cs_resp_val;
    a_mux_sel       = cs_a_mux_sel;        // Sel for mux in front of A reg
    b_mux_sel       = cs_b_mux_sel;        // sel for mux in front of B reg
    result_mux_sel  = cs_result_mux_sel;   // sel for mux in front of result reg
    result_en       = cs_result_en;        // Enable for result register
    add_mux_sel     = cs_add_mux_sel;      // sel for mux in front of result

    increment_value = cs_increment_value;
    shamt           = cs_shamt;
  end
  endtask

  // Labels for Mealy transistions

  logic do_jump;
  logic do_add;
  logic do_nothing;

  assign do_jump     =  is_b_lnsb_0 && ( count < ( 31 - (`N_ZERO_TO_JUMP - 1) ) );
  assign do_add      =  b_lsb;
  assign do_nothing  = !b_lsb;

  // Set outputs using a control signal "table"

  always_comb begin

    cs( 0, 0, a_x, b_x, result_x, 0, add_mux_x, increment_1, shift_1);
    case ( state_reg )
      //                                 req resp a mux     b mux    result      result  add mux       increment    shift
      //                                 rdy val  sel       sel      mux sel     en      sel           value        amount
      STATE_IDLE:                    cs( 1,  0,   a_ld,     b_ld,    result_0,   1,      add_mux_x,    increment_1, shift_1);
      STATE_CALC: if ( do_jump     ) cs( 0,  0,   a_shift,  b_shift, result_add, 1,      add_mux_reg,  increment_n, shift_n);
             else if ( do_add      ) cs( 0,  0,   a_shift,  b_shift, result_add, 1,      add_mux_add,  increment_1, shift_1);
             else if ( do_nothing  ) cs( 0,  0,   a_shift,  b_shift, result_add, 1,      add_mux_reg,  increment_1, shift_1);
      STATE_DONE:                    cs( 0,  1,   a_x,      b_x,     result_add, 1,      add_mux_reg,  increment_1, shift_1);
      default                        cs('x, 'x,   a_x,      b_x,     result_x,  'x,     'x,            increment_1, shift_1);

    endcase

  end

endmodule

//=========================================================================
// Integer Multiplier Variable-Latency Implementation
//=========================================================================

module lab1_imul_IntMulAltVRTL
(
  input  logic        clk,
  input  logic        reset,

  input  logic        req_val,
  output logic        req_rdy,
  input  logic [63:0] req_msg,

  output logic        resp_val,
  input  logic        resp_rdy,
  output logic [31:0] resp_msg
);

  //----------------------------------------------------------------------
  // Connect Control Unit and Datapath
  //----------------------------------------------------------------------

  // Control signals

  logic        result_en;                   // Enable for result register
  logic        a_mux_sel;                   // sel for mux in front of A reg
  logic        b_mux_sel;                   // sel for mux in front of B reg
  logic        result_mux_sel;              // sel for mux in front of result reg
  logic        add_mux_sel;                 // sel for mux in front of result
  
  logic [2:0]  shamt;                       // shift amount

  // Data signals

  logic        b_lsb;                       // least significant bit of b
  logic        is_b_lnsb_0;                 // is least n significant bits of b zero

  // Control unit

  IntMulAlt_UnitCtrl ctrl
  (
    .*
  );

  // Datapath

  IntMulAlt_UnitDpath dpath
  (
    .*
  );

  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    $sformat( str, "%x", req_msg );
    vc_trace.append_val_rdy_str( trace_str, req_val, req_rdy, str );

    vc_trace.append_str( trace_str, "(" );

    $sformat( str, "%x", dpath.a_reg_out );
    vc_trace.append_str( trace_str, str );
    vc_trace.append_str( trace_str, " " );

    $sformat( str, "%x", dpath.b_reg_out );
    vc_trace.append_str( trace_str, str );
    vc_trace.append_str( trace_str, " " );

    $sformat( str, "%x", dpath.is_b_lnsb_0 );
    vc_trace.append_str( trace_str, str );
    vc_trace.append_str( trace_str, " " );

    $sformat( str, "%x", ctrl.increment_value );
    vc_trace.append_str( trace_str, str );
    vc_trace.append_str( trace_str, " " );

    $sformat( str, "%x", ctrl.count     );
    vc_trace.append_str( trace_str, str );
    vc_trace.append_str( trace_str, " " );

    vc_trace.append_str( trace_str, ")" );

    $sformat( str, "%x", resp_msg );
    vc_trace.append_val_rdy_str( trace_str, resp_val, resp_rdy, str );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* LAB1_IMUL_INT_MUL_ALT_V */
