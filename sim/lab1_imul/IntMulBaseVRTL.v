//========================================================================
// Integer Multiplier Fixed-Latency Implementation
//========================================================================

`ifndef LAB1_IMUL_INT_MUL_BASE_V
`define LAB1_IMUL_INT_MUL_BASE_V

`include "vc/trace.v"
`include "vc/muxes.v"
`include "vc/counters.v"
`include "vc/regs.v"
`include "vc/arithmetic.v"

// ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// Define datapath and control unit here.
// '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

//========================================================================
// IntMulBase Unit Dpath
//========================================================================

module IntMulBase_UnitDpath
(
  input  logic        clk,
  input  logic        reset,

  // Data signals

  input  logic [63:0] req_msg,
  output logic [31:0] resp_msg,

  // Control signals

  input  logic        result_en,   // Enable for result register
  input  logic        a_mux_sel,  // Sel for mux in front of A reg
  input  logic        b_mux_sel,  // sel for mux in front of B reg
  input  logic        result_mux_sel,  // sel for mux in front of result reg
  input  logic        add_mux_sel,  // sel for mux in front of result

  // Status signals

  output  logic       b_lsb  // least significant bit of b
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

  logic shamt = 1;

  vc_LeftLogicalShifter#(c_nbits, 1) a_shifter
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

  vc_Reg#(c_nbits) b_reg
  (
    .clk   (clk),
    .d     (b_mux_out),
    .q     (b_reg_out)
  );

  // B left shifter

  vc_RightLogicalShifter#(c_nbits, 1) b_shifter
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
// IntMulBase Unit Control
//========================================================================

module IntMulBase_UnitCtrl
(
  input  logic        clk,
  input  logic        reset,

  // Dataflow signals

  input  logic        req_val,
  output logic        req_rdy,
  output logic        resp_val,
  input  logic        resp_rdy,

  // Control signals

  output  logic        result_en,       // Enable for result register
  output  logic        a_mux_sel,       // Sel for mux in front of A reg
  output  logic        b_mux_sel,       // sel for mux in front of B reg
  output  logic        result_mux_sel,  // sel for mux in front of result reg
  output  logic        add_mux_sel,     // sel for mux in front of result

  // Status signals

  input   logic         b_lsb  // least significant bit of b
);

  //----------------------------------------------------------------------
  // State Definitions
  //----------------------------------------------------------------------

  localparam STATE_IDLE = 2'd0;
  localparam STATE_CALC = 2'd1;
  localparam STATE_DONE = 2'd2;

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

  logic is_counter_32;

  vc_BasicCounter#(5,0,31) counter
  (
    .clk(clk),
    .reset(reset),
    // Operations
    .clear(state_reg!=STATE_CALC),
    .increment(1),
    .decrement(0),
    // Outputs
    .count(),
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

  task cs
  (
    input logic       cs_req_rdy,
    input logic       cs_resp_val,
    input logic       cs_a_mux_sel,
    input logic       cs_b_mux_sel,
    input logic       cs_result_mux_sel,
    input logic       cs_result_en,
    input logic       cs_add_mux_sel,
  );
  begin
    req_rdy         = cs_req_rdy;
    resp_val        = cs_resp_val;
    a_mux_sel       = cs_a_mux_sel;       // Sel for mux in front of A reg
    b_mux_sel       = cs_b_mux_sel;       // sel for mux in front of B reg
    result_mux_sel  = cs_result_mux_sel;  // sel for mux in front of result reg
    result_en       = cs_result_en;       // Enable for result register
    add_mux_sel     = cs_add_mux_sel;     // sel for mux in front of result
  end
  endtask

  // Labels for Mealy transistions

  logic do_add;
  logic do_nothing;

  assign do_add      =  b_lsb;
  assign do_nothing  = !b_lsb;

  // Set outputs using a control signal "table"

  always_comb begin

    cs( 0, 0, a_x, b_x, result_x, 0, add_mux_x);
    case ( state_reg )
      //                                 req resp a mux     b mux    result      result  add mux
      //                                 rdy val  sel       sel      mux sel     en      sel
      STATE_IDLE:                    cs( 1,  0,   a_ld,     b_ld,    result_0,   1,      add_mux_x   );
      STATE_CALC: if ( do_add      ) cs( 0,  0,   a_shift,  b_shift, result_add, 1,      add_mux_add );
             else if ( do_nothing  ) cs( 0,  0,   a_shift,  b_shift, result_add, 1,      add_mux_reg );
      STATE_DONE:                    cs( 0,  1,   a_x,      b_x,     result_add, 1,      add_mux_reg );
      default                        cs('x, 'x,   a_x,      b_x,     result_x,  'x,     'x           );

    endcase

  end

endmodule

//========================================================================
// Integer Multiplier Fixed-Latency Implementation
//========================================================================

module lab1_imul_IntMulBaseVRTL
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

  // ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // Instantiate datapath and control models here and then connect them
  // together.
  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  //----------------------------------------------------------------------
  // Connect Control Unit and Datapath
  //----------------------------------------------------------------------

  // Control signals

  logic        result_en;   // Enable for result register
  logic        a_mux_sel;   // sel for mux in front of A reg
  logic        b_mux_sel;   // sel for mux in front of B reg
  logic        result_mux_sel;  // sel for mux in front of result reg
  logic        add_mux_sel;  // sel for mux in front of result

  // Data signals

  logic        b_lsb;    // least significant bit of b

  // Control unit

  IntMulBase_UnitCtrl ctrl
  (
    .*
  );

  // Datapath

  IntMulBase_UnitDpath dpath
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

    // ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''
    // Add additional line tracing using the helper tasks for
    // internal state including the current FSM state.
    // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    $sformat( str, "%x", dpath.a_reg_out );
    vc_trace.append_str( trace_str, str );
    vc_trace.append_str( trace_str, " " );

    $sformat( str, "%x", dpath.b_reg_out );
    vc_trace.append_str( trace_str, str );
    vc_trace.append_str( trace_str, " " );

    vc_trace.append_str( trace_str, ")" );

    $sformat( str, "%x", resp_msg );
    vc_trace.append_val_rdy_str( trace_str, resp_val, resp_rdy, str );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* LAB1_IMUL_INT_MUL_BASE_V */

