//========================================================================
// Integer Multiplier Fixed-Latency Implementation
//========================================================================

`ifndef LAB1_IMUL_INT_MUL_BASE_V
`define LAB1_IMUL_INT_MUL_BASE_V

`include "vc/trace.v"
`include "vc/counters.v"
`include "vc/arithmetic.v"
`include "vc/muxes.v"

//========================================================================
// IntMul Base Unit Datapath
//========================================================================
module lab1_imul_IntMulBaseUnitDpath
(
  input  logic        clk,
  input  logic        reset,

  // Data signals

  input  logic [63:0] req_msg,
  output logic [31:0] resp_msg,

  // Control signals
  input  logic        result_en,        // Enable for result register
  input  logic        b_mux_sel,        // Sel for mux in front of B reg
  input  logic        a_mux_sel,        // Sel for mux in front of A reg
  input  logic        result_mux_sel,   // Sel for mux in front of result reg
  input  logic        add_mux_sel,      // Sel for mux 

  // Status signals
  output logic        b_lsb             // Least significant bit of B (B&0x1)
);

  localparam c_nbits = 32;

  // Split out the a and b operands
  logic [c_nbits-1:0] req_msg_a = req_msg[63:32];
  logic [c_nbits-1:0] req_msg_b = req_msg[31:0];

  // B mux
  logic [c_nbits-1:0] right_shifter_out;
  logic [c_nbits-1:0] b_mux_out;

  vc_Mux2#(c_nbits) b_mux
  (
    .sel    (b_mux_sel),
    .in0    (right_shifter_out),
    .in1    (req_msg_b),
    .out    (b_mux_out)
  );

  // B register
  logic [c_nbits-1:0] b_reg_out;

  vc_EnReg#(c_nbits) b_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (1),
    .d      (b_mux_out),
    .q      (b_reg_out)
  );

  // B data signal

  assign b_lsb = b_reg_out[0:0];

  // B right shifter
  vc_RightLogicalShifter#(c_nbits) right_shifter
  (
    .in     (b_reg_out),
    .shamt  (1),
    .out    (right_shifter_out)
  );

  // A mux
  logic [c_nbits-1:0] left_shifter_out;
  logic [c_nbits-1:0] a_mux_out;

  vc_Mux2#(c_nbits) a_mux
  (
    .sel    (a_mux_sel),
    .in0    (left_shifter_out),
    .in1    (req_msg_a),
    .out    (a_mux_out)
  );

  // A register
  logic [c_nbits-1:0] a_reg_out;

  vc_EnReg#(c_nbits) a_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (1),
    .d      (a_mux_out),
    .q      (a_reg_out)
  );

  // A shifter
  vc_LeftLogicalShifter#(c_nbits) left_shifter
  (
    .in     (a_reg_out),
    .shamt  (1),
    .out    (left_shifter_out)
  );

  // Result mux 
  logic [c_nbits-1:0] result_mux_out;
  logic [c_nbits-1:0] add_mux_out;

  vc_Mux2#(c_nbits) result_mux
  (
    .sel    (result_mux_sel),
    .in0    (add_mux_out),
    .in1    (0),
    .out    (result_mux_out)
  );

  // Result register 
  logic [c_nbits-1:0] result_reg_out;

  vc_EnReg#(c_nbits) result_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (result_en),
    .d      (result_mux_out),
    .q      (result_reg_out)
  );

  // Adder
  logic [c_nbits-1:0] adder_out;

  vc_SimpleAdder#(c_nbits) adder
  (
    .in0    (a_reg_out),
    .in1    (result_reg_out),
    .out    (adder_out)
  );

  // Add mux

  vc_Mux2#(c_nbits) add_mux
  (
    .sel    (add_mux_sel),
    .in0    (adder_out),
    .in1    (result_reg_out),
    .out    (add_mux_out)
  );

  // connect to the output port
  assign resp_msg = result_reg_out;

endmodule

//========================================================================
// IntMul Base Unit Control 
//========================================================================

module lab1_imul_IntMulBaseUnitCtrl
(
  input  logic          clk,
  input  logic          reset,

  // Dataflow signals

  input  logic        req_val,
  output logic        req_rdy,
  output logic        resp_val,
  input  logic        resp_rdy, 

  // Control signals

  output  logic        b_mux_sel,        // Sel for mux in front of B reg
  output  logic        a_mux_sel,        // Sel for mux in front of A reg
  output  logic        result_mux_sel,   // Sel for mux in front of result reg
  output  logic        result_en,        // Enable for result register
  output  logic        add_mux_sel,      // Sel for mux 

  // Data signals
  input  logic         b_lsb       // Sel for mux 
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

  // counter logic
  localparam p_count_nbits = 5;

  logic [p_count_nbits-1:0] count;
  logic                     count_is_zero;
  logic                     count_is_max;

  assign req_go         = req_val && req_rdy;
  assign resp_go        = resp_val && resp_rdy;
  assign is_calc_done   = count_is_max;

  vc_BasicCounter#(p_count_nbits, 0, 31) counter
  (
    .clk            (clk),
    .reset          (reset),

    .clear          (count_is_max),
    .increment      (1),
    .decrement      (0),

    .count          (count),
    .count_is_zero  (count_is_zero),
    .count_is_max   (count_is_max)
  );

  always_comb begin

    state_next = state_reg;
  
    case ( state_reg )

      STATE_IDLE: if ( req_go    )    state_next = STATE_CALC;
      STATE_CALC: if ( is_calc_done ) state_next = STATE_DONE;
      STATE_DONE: if ( resp_go   )    state_next = STATE_IDLE;
      default:    state_next = 'x;

    endcase

  end


  //----------------------------------------------------------------------
  // State Outputs
  //----------------------------------------------------------------------

  // input for B mux
  localparam b_x   = 1'dx;   // initial value
  localparam b_sh  = 1'd0;   // choose input of shifter
  localparam b_ld  = 1'd1;   // choose input of msg

  // input for A mux
  localparam a_x   = 1'dx;   // initial value
  localparam a_sh  = 1'd0;   // choose input of shifter
  localparam a_ld  = 1'd1;   // choose input of msg

  // input for result mux
  localparam r_x   = 1'dx;   // initial
  localparam r_ad  = 1'd0;   // add mux out
  localparam r_ld  = 1'd1;   // 0

  // input for add mux
  localparam ad_x   = 1'dx;  // initial value
  localparam ad_ar  = 1'd0;  // choose adder_out
  localparam ad_re  = 1'd1;  // choose result_reg_out

  task cs
  (    
    input  logic        cs_req_rdy,
    input  logic        cs_resp_val,
    input  logic        cs_b_mux_sel,        
    input  logic        cs_a_mux_sel,        
    input  logic        cs_result_mux_sel,    
    input  logic        cs_result_en,        
    input  logic        cs_add_mux_sel   
  );
  begin 
    req_rdy         =    cs_req_rdy;
    resp_val        =    cs_resp_val;
    b_mux_sel       =    cs_b_mux_sel;        
    a_mux_sel       =    cs_a_mux_sel;        
    result_mux_sel  =    cs_result_mux_sel;  
    result_en       =    cs_result_en;   
    add_mux_sel     =    cs_add_mux_sel;      
  end
  endtask

  // labels for Mealy Transitions
  logic  do_add;

  // assign do_add   = (count <= 5'b11111 && b_lsb == 1);
  assign do_add   =  (b_lsb == 1);

  // set output

  always_comb begin

    cs( 0, 0, b_x, a_x, r_x, 0, ad_x);
    case ( state_reg )
      //                             req resp b mux  a mux  r mux   r  ad mux
      //                             rdy val  sel    sel    sel     en sel   
      STATE_IDLE:                cs( 1,  0,   b_ld,  a_ld,  r_ld,   1, ad_ar);
      STATE_CALC: if ( do_add )  cs( 0,  0,   b_sh,  a_sh,  r_ad,   1, ad_ar);
                  else           cs( 0,  0,   b_sh,  a_sh,  r_ad,   1, ad_re);
      STATE_DONE:                cs( 0,  1,   b_x,   a_x,   r_x,    0, ad_x );
      default                    cs('x, 'x,   b_x,   a_x,   r_x,   'x, ad_x );

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

  //----------------------------------------------------------------------
  // Connect Control Unit and Datapath
  //----------------------------------------------------------------------

  // Control signals

  logic        b_mux_sel;   
  logic        a_mux_sel;        
  logic        result_mux_sel;  
  logic        result_en;        
  logic        add_mux_sel;      

  // Data signals

  logic        b_lsb;

  // Control unit
  lab1_imul_IntMulBaseUnitCtrl ctrl
  (
    .*
  );

  // DataPath
  lab1_imul_IntMulBaseUnitDpath dpath
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

    $sformat( str, "%x", dpath.result_reg_out );
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

