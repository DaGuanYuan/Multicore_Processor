//=========================================================================
// Ring-based network
//=========================================================================

`ifndef LAB4_NET_RING_NET_V
`define LAB4_NET_RING_NET_V

`include "vc/net-msgs.v"
`include "lab4_net/RouterVRTL.v"

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Include necessary files
//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
`include "vc/queues.v"

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

// Helper macros to calculate previous and next router ids

`define PREV(i_) ( ( i_ + c_num_ports - 1 ) % c_num_ports )
`define NEXT(i_) i_

module lab4_net_RingNetVRTL
#(
  parameter p_payload_nbits = 32
)
(
  input logic clk,
  input logic reset,

  input  net_hdr_t [c_nports-1:0]                      in_msg_hdr,
  input  logic     [c_nports-1:0][p_payload_nbits-1:0] in_msg_payload,
  input  logic     [c_nports-1:0]                      in_val,
  output logic     [c_nports-1:0]                      in_rdy,

  output net_hdr_t [c_nports-1:0]                      out_msg_hdr,
  output logic     [c_nports-1:0][p_payload_nbits-1:0] out_msg_payload,
  output logic     [c_nports-1:0]                      out_val,
  input  logic     [c_nports-1:0]                      out_rdy
);
  // c_nports included for convenience to avoid having magic numbers, but 
  // your design does not need to support other values of c_nports.
  localparam c_nports = 4;

  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Compose ring network
  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

  // Router-Router connections
  
  // Forward (increasing router id) wires
  logic     [c_nports-1:0]                      forw_out_val;
  logic     [c_nports-1:0]                      forw_out_rdy;
  net_hdr_t [c_nports-1:0]                      forw_out_msg_hdr;
  logic     [c_nports-1:0][p_payload_nbits-1:0] forw_out_msg_payload;

  logic     [c_nports-1:0]                      forw_in_val;
  logic     [c_nports-1:0]                      forw_in_rdy;
  net_hdr_t [c_nports-1:0]                      forw_in_msg_hdr;
  logic     [c_nports-1:0][p_payload_nbits-1:0] forw_in_msg_payload;

  // Backward (decreasing router id) wires
  logic     [c_nports-1:0]                      backw_out_val;
  logic     [c_nports-1:0]                      backw_out_rdy;
  net_hdr_t [c_nports-1:0]                      backw_out_msg_hdr;
  logic     [c_nports-1:0][p_payload_nbits-1:0] backw_out_msg_payload;

  logic     [c_nports-1:0]                      backw_in_val;
  logic     [c_nports-1:0]                      backw_in_rdy;
  net_hdr_t [c_nports-1:0]                      backw_in_msg_hdr;
  logic     [c_nports-1:0][p_payload_nbits-1:0] backw_in_msg_payload;

  genvar i;
  generate
  for (i = 0; i < c_nports; i = i + 1) begin: ROUTER
    // X-th router's #0 connects to (X-1)-th forw/backw channel
    // X-th router's #2 connects to X-th forw/backw channel
    genvar prev;
    assign prev = (i + c_nports - 1) % c_nports;

    lab4_net_RouterVRTL 
    #(
      .p_payload_nbits(p_payload_nbits)
    )
    router
    (
      .clk              (clk),
      .reset            (reset),

      .router_id        (i[1:0]),

      .in0_val          (forw_in_val[prev]),
      .in0_rdy          (forw_in_rdy[prev]),
      .in0_msg_hdr      (forw_in_msg_hdr[prev]),
      .in0_msg_payload  (forw_in_msg_payload[prev]),

      .out0_val         (backw_out_val[prev]),
      .out0_rdy         (backw_out_rdy[prev]),
      .out0_msg_hdr     (backw_out_msg_hdr[prev]),
      .out0_msg_payload (backw_out_msg_payload[prev]),

      .in1_val          (in_val[i]),
      .in1_rdy          (in_rdy[i]),
      .in1_msg_hdr      (in_msg_hdr[i]),
      .in1_msg_payload  (in_msg_payload[i]),

      .out1_val         (out_val[i]),
      .out1_rdy         (out_rdy[i]),
      .out1_msg_hdr     (out_msg_hdr[i]),
      .out1_msg_payload (out_msg_payload[i]),

      .out2_val         (forw_out_val[i]),
      .out2_rdy         (forw_out_rdy[i]),
      .out2_msg_hdr     (forw_out_msg_hdr[i]),
      .out2_msg_payload (forw_out_msg_payload[i]),

      .in2_val          (backw_in_val[i]),
      .in2_rdy          (backw_in_rdy[i]),
      .in2_msg_hdr      (backw_in_msg_hdr[i]),
      .in2_msg_payload  (backw_in_msg_payload[i])
    );
  end
  endgenerate

  generate
  for (i = 0; i < c_nports; i = i + 1) begin: CHANNEL
    vc_Queue
    #(
      .p_type(`VC_QUEUE_NORMAL),
      .p_msg_nbits($bits(net_hdr_t) + p_payload_nbits),
      .p_num_msgs(2)
    )
    forw_channel_queue
    (
      .clk     (clk),
      .reset   (reset),

      .enq_val (forw_out_val[i]),
      .enq_rdy (forw_out_rdy[i]),
      .enq_msg ({forw_out_msg_hdr[i], forw_out_msg_payload[i]}),

      .deq_val (forw_in_val[i]),
      .deq_rdy (forw_in_rdy[i]),
      .deq_msg ({forw_in_msg_hdr[i], forw_in_msg_payload[i]}),

      .num_free_entries ()
    );

    vc_Queue
    #(
      .p_type(`VC_QUEUE_NORMAL),
      .p_msg_nbits($bits(net_hdr_t) + p_payload_nbits),
      .p_num_msgs(2)
    )
    backw_channel_queue
    (
      .clk     (clk),
      .reset   (reset),

      .enq_val (backw_out_val[i]),
      .enq_rdy (backw_out_rdy[i]),
      .enq_msg ({backw_out_msg_hdr[i], backw_out_msg_payload[i]}),

      .deq_val (backw_in_val[i]),
      .deq_rdy (backw_in_rdy[i]),
      .deq_msg ({backw_in_msg_hdr[i], backw_in_msg_payload[i]}),

      .num_free_entries ()
    );
  end
  endgenerate

  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

  //----------------------------------------------------------------------
  // Line tracing
  //----------------------------------------------------------------------
  generate
  for (i = 0; i < c_nports; i = i + 1) begin: HEADER
    vc_NetHdrTrace in_hdr_trace
    (
      .clk   (clk),
      .reset (reset),
      .val   (in_val[i]),
      .rdy   (in_rdy[i]),
      .hdr   (in_msg_hdr[i])
    );

    vc_NetHdrTrace out_hdr_trace
    (
      .clk   (clk),
      .reset (reset),
      .val   (out_val[i]),
      .rdy   (out_rdy[i]),
      .hdr   (out_msg_hdr[i])
    );
  end
  endgenerate

  logic [6*8-1:0] in_str;
  logic [6*8-1:0] out_str;

  `VC_TRACE_BEGIN
  begin
    ROUTER[0].router.line_trace( trace_str );
    ROUTER[1].router.line_trace( trace_str );
    ROUTER[2].router.line_trace( trace_str );
    ROUTER[3].router.line_trace( trace_str );
  end
  `VC_TRACE_END

endmodule

`endif /* LAB4_NET_RING_NET_V */
