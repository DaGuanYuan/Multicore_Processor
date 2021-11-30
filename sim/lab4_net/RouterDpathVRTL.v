//=========================================================================
// Router datapath
//=========================================================================

`ifndef LAB4_NET_ROUTER_DPATH_V
`define LAB4_NET_ROUTER_DPATH_V

`include "vc/net-msgs.v"

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Include necessary files
//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
`include "vc/queues.v"
`include "vc/crossbars.v"

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

module lab4_net_RouterDpathVRTL
#(
  parameter p_payload_nbits = 32
)
(
  input  logic                           clk,
  input  logic                           reset,

  input  net_hdr_t                       in0_msg_hdr,
  input  logic     [p_payload_nbits-1:0] in0_msg_payload,
  input  logic                           in0_val,
  output logic                           in0_rdy,

  input  net_hdr_t                       in1_msg_hdr,
  input  logic     [p_payload_nbits-1:0] in1_msg_payload,
  input  logic                           in1_val,
  output logic                           in1_rdy,

  input  net_hdr_t                       in2_msg_hdr,
  input  logic     [p_payload_nbits-1:0] in2_msg_payload,
  input  logic                           in2_val,
  output logic                           in2_rdy,

  output net_hdr_t                       out0_msg_hdr,
  output logic     [p_payload_nbits-1:0] out0_msg_payload,

  output net_hdr_t                       out1_msg_hdr,
  output logic     [p_payload_nbits-1:0] out1_msg_payload,

  output net_hdr_t                       out2_msg_hdr,
  output logic     [p_payload_nbits-1:0] out2_msg_payload,

  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Define additional ports
  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
  output logic                           inq0_val,
  input  logic                           inq0_rdy,
  output logic     [1:0]                 inq0_dest,

  output logic                           inq1_val,
  input  logic                           inq1_rdy,
  output logic     [1:0]                 inq1_dest,

  output logic                           inq2_val,
  input  logic                           inq2_rdy,
  output logic     [1:0]                 inq2_dest,

  input  logic     [1:0]                 xbar_sel0,
  input  logic     [1:0]                 xbar_sel1,
  input  logic     [1:0]                 xbar_sel2
  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
);

  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Implement datapath
  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
  net_hdr_t inq0_msg_hdr;
  net_hdr_t inq1_msg_hdr;
  net_hdr_t inq2_msg_hdr;

  logic [p_payload_nbits-1:0] inq0_msg_payload;
  logic [p_payload_nbits-1:0] inq1_msg_payload;
  logic [p_payload_nbits-1:0] inq2_msg_payload;

  // Crossbar for the headers
  vc_Crossbar3
  #(
    .p_nbits($bits(net_hdr_t))
  )
  xbar_hdr
  (
    .in0  (inq0_msg_hdr),
    .in1  (inq1_msg_hdr),
    .in2  (inq2_msg_hdr),

    .out0 (out0_msg_hdr),
    .out1 (out1_msg_hdr),
    .out2 (out2_msg_hdr),

    .sel0 (xbar_sel0),
    .sel1 (xbar_sel1),
    .sel2 (xbar_sel2)
  );

  // Crossbar for the payloads
  vc_Crossbar3
  #(
    .p_nbits(p_payload_nbits)
  )
  xbar_payload
  (
    .in0  (inq0_msg_payload),
    .in1  (inq1_msg_payload),
    .in2  (inq2_msg_payload),

    .out0 (out0_msg_payload),
    .out1 (out1_msg_payload),
    .out2 (out2_msg_payload),

    .sel0 (xbar_sel0),
    .sel1 (xbar_sel1),
    .sel2 (xbar_sel2)
  );

  // Input queue for port 0
  vc_Queue
  #(
    .p_type(`VC_QUEUE_NORMAL),
    .p_msg_nbits($bits(net_hdr_t) + p_payload_nbits),
    .p_num_msgs(2)
  )
  in0_queue
  (
    .clk     (clk),
    .reset   (reset),

    .enq_val (in0_val),
    .enq_rdy (in0_rdy),
    .enq_msg ({in0_msg_hdr, in0_msg_payload}),

    .deq_val (inq0_val),
    .deq_rdy (inq0_rdy),
    .deq_msg ({inq0_msg_hdr, inq0_msg_payload}),

    .num_free_entries ()
  );

  assign inq0_dest = inq0_msg_hdr.dest;

  // Input queue for port 1
  vc_Queue
  #(
    .p_type(`VC_QUEUE_NORMAL),
    .p_msg_nbits($bits(net_hdr_t) + p_payload_nbits),
    .p_num_msgs(2)
  )
  in1_queue
  (
    .clk     (clk),
    .reset   (reset),

    .enq_val (in1_val),
    .enq_rdy (in1_rdy),
    .enq_msg ({in1_msg_hdr, in1_msg_payload}),

    .deq_val (inq1_val),
    .deq_rdy (inq1_rdy),
    .deq_msg ({inq1_msg_hdr, inq1_msg_payload}),

    .num_free_entries ()
  );

  assign inq1_dest = inq1_msg_hdr.dest;

  // Input Queue for port 2
  vc_Queue
  #(
    .p_type(`VC_QUEUE_NORMAL),
    .p_msg_nbits($bits(net_hdr_t) + p_payload_nbits),
    .p_num_msgs(2)
  )
  in2_queue
  (
    .clk     (clk),
    .reset   (reset),

    .enq_val (in2_val),
    .enq_rdy (in2_rdy),
    .enq_msg ({in2_msg_hdr, in2_msg_payload}),

    .deq_val (inq2_val),
    .deq_rdy (inq2_rdy),
    .deq_msg ({inq2_msg_hdr, inq2_msg_payload}),

    .num_free_entries ()
  );

  assign inq2_dest = inq2_msg_hdr.dest;

  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

endmodule

`endif /* LAB4_NET_ROUTER_DPATH_V */
