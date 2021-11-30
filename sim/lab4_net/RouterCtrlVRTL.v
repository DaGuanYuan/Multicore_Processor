//=========================================================================
// Router Control Unit
//=========================================================================

`ifndef LAB4_NET_ROUTER_CTRL_V
`define LAB4_NET_ROUTER_CTRL_V

`include "vc/net-msgs.v"

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Include necessary files
//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
`include "vc/arbiters.v"

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

module lab4_net_RouterCtrlVRTL
(
  input  logic       clk,
  input  logic       reset,
  
  input  logic [1:0] router_id,

  output logic       out0_val,
  input  logic       out0_rdy,

  output logic       out1_val,
  input  logic       out1_rdy,

  output logic       out2_val,
  input  logic       out2_rdy,

  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Define additional ports
  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
  input  logic       inq0_val,
  output logic       inq0_rdy,
  input  logic [1:0] inq0_dest,

  input  logic       inq1_val,
  output logic       inq1_rdy,
  input  logic [1:0] inq1_dest,

  input  logic       inq2_val,
  output logic       inq2_rdy,
  input  logic [1:0] inq2_dest,

  output logic [1:0] xbar_sel0,
  output logic [1:0] xbar_sel1,
  output logic [1:0] xbar_sel2
  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
);

  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Implement control unit
  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
  logic [2:0]  in0_reqs;
  logic [2:0]  in1_reqs;
  logic [2:0]  in2_reqs;

  logic [2:0] out0_reqs;
  logic [2:0] out1_reqs;
  logic [2:0] out2_reqs;

  logic [1:0] forw_hops;
  logic [1:0] backw_hops;

  assign backw_hops = router_id - inq1_dest;
  assign forw_hops  = inq1_dest - router_id;

  // Determine the desired output port for each input
  always_comb begin
    in0_reqs = 3'b0;
    in1_reqs = 3'b0;
    in2_reqs = 3'b0;

    // Routing for input 0
    if (inq0_val) begin
      if (inq0_dest == router_id)
        in0_reqs = 3'b010;
      else
        in0_reqs = 3'b100;
    end

    // Routing for input 1
    // Use greedy routing, then odd/even
    if (inq1_val) begin
      // Check if this is the destination
      if (inq1_dest == router_id)
        in1_reqs = 3'b010;
      // Then check if greedy works
      else if (forw_hops < backw_hops)
        in1_reqs = 3'b100;
      else if (forw_hops > backw_hops)
        in1_reqs = 3'b001;
      // If greedy tied, use odd/even routing
      else if (router_id[0])
        in1_reqs = 3'b100;
      else
        in1_reqs = 3'b001;
    end

    // Routing for input 2
    if (inq2_val) begin
      if (inq2_dest == router_id)
        in2_reqs = 3'b010;
      else
        in2_reqs = 3'b001;
    end
  end

  assign out0_reqs = {in2_reqs[0], in1_reqs[0], in0_reqs[0]};
  assign out1_reqs = {in2_reqs[1], in1_reqs[1], in0_reqs[1]};
  assign out2_reqs = {in2_reqs[2], in1_reqs[2], in0_reqs[2]};

  //-----------------------------------------------------------------------
  // arbiter for #0 (channel port)
  //-----------------------------------------------------------------------
  
  logic [2:0] out0_grants;
  vc_RoundRobinArbEn #(3) arbiter_out0
  (
    .clk    (clk),
    .reset  (reset),

    .reqs   (out0_reqs),
    .grants (out0_grants),
    .en     (out0_rdy)     // Only update priority if the port is ready
  );

  // Set the valid bit, and configure the crossbar
  assign out0_val = | out0_grants;
  always_comb begin
    if (out0_grants == 3'b001)
      xbar_sel0 = 2'd0;
    else if (out0_grants == 3'b010)
      xbar_sel0 = 2'd1;
    else
      xbar_sel0 = 2'd2;
  end

  //-----------------------------------------------------------------------
  // arbiter for #1 (terminal port)
  //-----------------------------------------------------------------------
  
  logic [2:0] out1_grants;
  vc_RoundRobinArbEn #(3) arbiter_out1
  (
    .clk    (clk),
    .reset  (reset),

    .reqs   (out1_reqs),
    .grants (out1_grants),
    .en     (out1_rdy)     // Only update priority if the port is ready
  );

  // Set the valid bit, and configure the crossbar
  assign out1_val = | out1_grants;
  always_comb begin
    if (out1_grants == 3'b001)
      xbar_sel1 = 2'd0;
    else if (out1_grants == 3'b010)
      xbar_sel1 = 2'd1;
    else
      xbar_sel1 = 2'd2;
  end

  //-----------------------------------------------------------------------
  // arbiter for #2 (channel port)
  //-----------------------------------------------------------------------
  
  logic [2:0] out2_grants;
  vc_RoundRobinArbEn #(3) arbiter_out2
  (
    .clk    (clk),
    .reset  (reset),

    .reqs   (out2_reqs),
    .grants (out2_grants),
    .en     (out2_rdy)     // Only update priority if the port is ready
  );

  // Set the valid bit, and configure the crossbar
  assign out2_val = | out2_grants;
  always_comb begin
    if (out2_grants == 3'b001)
      xbar_sel2 = 2'd0;
    else if (out2_grants == 3'b010)
      xbar_sel2 = 2'd1;
    else
      xbar_sel2 = 2'd2;
  end

  // Translate the arbiter grant signals back to each input
  // Also propagate the outX.rdy signal back to deq.rdy

  logic [2:0] in0_grants;
  logic [2:0] in1_grants;
  logic [2:0] in2_grants;

  assign in0_grants = {out2_grants[0], out1_grants[0], out0_grants[0]};
  assign in1_grants = {out2_grants[1], out1_grants[1], out0_grants[1]};
  assign in2_grants = {out2_grants[2], out1_grants[2], out0_grants[2]};

  logic [2:0] outs_rdy;
  assign outs_rdy   = {out2_rdy, out1_rdy, out0_rdy};

  assign inq0_rdy = | ( in0_reqs & in0_grants & outs_rdy );
  assign inq1_rdy = | ( in1_reqs & in1_grants & outs_rdy );
  assign inq2_rdy = | ( in2_reqs & in2_grants & outs_rdy );

  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

endmodule

`endif /* LAB4_NET_ROUTER_CTRL_V */
