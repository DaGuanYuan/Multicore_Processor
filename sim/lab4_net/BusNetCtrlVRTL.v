`ifndef LAB4_NET_BUS_NET_CTRL_V
`define LAB4_NET_BUS_NET_CTRL_V

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Include necessary files
//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
`include "vc/arbiters.v"

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

module lab4_net_BusNetCtrlVRTL
(
  input  logic                                 clk,
  input  logic                                 reset,

  output logic [c_nports-1:0]                  out_val,
  input  logic [c_nports-1:0]                  out_rdy,

  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Define additional ports
  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
  input  logic [c_nports-1:0]                  inq_val,
  output logic [c_nports-1:0]                  inq_rdy,
  input  logic [c_nports-1:0][1:0]             inq_dest,

  output logic [1:0]                           bus_sel
  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
);
  // c_nports included for convenience to avoid having magic numbers, but 
  // your design does not need to support other values of c_nports.
  localparam c_nports = 4;

  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Implement control unit
  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

  logic [c_nports-1:0] arb_reqs;
  assign arb_reqs = inq_val;
  // The above implementation doesn't take the ready status of the
  // destination port into account, so resource waste is possible in the
  // sense that the inport is granted but the output port is not ready.
  //
  // To optimize performance, you not only need to AND the one-hot
  // destination signal of each inport with a concatenated ready status
  // of all ports, but also need to ADD A BYPASS QUEUE between the
  // arbiter output valrdybundle and the actual out valrdy bundle.
  //
  // This is because when we take rdy signal into arbitration, the output
  // val signal now depends on the output rdy signal which might create
  // trouble when the other end calculate the rdy signal based on the
  // valid signal. We have to avoid this loop and the simplest way is to
  // add a bypass queue.

  // The arbiter arbitrates over the on-board signal of each port
  // and generates an one-hot signal out_grant
  // We provide the output ready signal arb_out_rdy as a feedback signal
  // to stop the arbitration when the destination of the arbitrated input
  // port is not ready.
  logic [c_nports-1:0] out_grant;
  logic arb_out_rdy;

  vc_RoundRobinArbEn #(c_nports) arbiter
  (
    .clk(clk),
    .reset(reset),

    .reqs(inq_val),
    .grants(out_grant),
    .en(arb_out_rdy)
  );

  // granted: the arbitrated input port
  // dest: the destination of the granted input port
  logic [1:0] granted;
  logic [1:0] dest;

  // Model an one-hot encoder to encode the arbitration -> "granted"
  // Set the valid bit of the destination outport of the granted inport
  always_comb begin
    if (out_grant[0]) begin
      granted = 2'd0;
      dest = inq_dest[0];
    end else if (out_grant[1]) begin
      granted = 2'd1;
      dest = inq_dest[1];
    end else if (out_grant[2]) begin
      granted = 2'd2;
      dest = inq_dest[2];
    end else if (out_grant[3]) begin
      granted = 2'd3;
      dest = inq_dest[3];
    end else begin
      granted = 2'dx;
      dest = 2'dx;
    end
  end

  assign bus_sel = granted;

  assign out_val[0] = out_grant != 4'b0 && dest == 2'd0;
  assign out_val[1] = out_grant != 4'b0 && dest == 2'd1;
  assign out_val[2] = out_grant != 4'b0 && dest == 2'd2;
  assign out_val[3] = out_grant != 4'b0 && dest == 2'd3;

  // Dequeue a message for i-th port when the request is granted and
  // the destination outport is ready 
  // Also provide the feedback rdy signal to the arbiter
  always_comb begin
    inq_rdy = 4'b0;
    arb_out_rdy = 1'b0;
    if (out_grant != 4'b0 && out_rdy[dest]) begin
      inq_rdy[granted] = 1'b1;
      arb_out_rdy = 1'b1;
    end
  end

  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

endmodule

`endif /* LAB4_NET_BUS_NET_CTRL_V */
