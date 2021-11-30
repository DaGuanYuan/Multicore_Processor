`ifndef LAB4_NET_BUS_NET_DPATH_V
`define LAB4_NET_BUS_NET_DPATH_V

`include "vc/net-msgs.v"

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Include necessary files
//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
`include "vc/queues.v"
`include "vc/buses.v"

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

module lab4_net_BusNetDpathVRTL
#(
  parameter p_payload_nbits = 32
)
(
  input  logic                                         clk,
  input  logic                                         reset,

  input  logic     [c_nports-1:0]                      in_val,
  output logic     [c_nports-1:0]                      in_rdy,
  input  net_hdr_t [c_nports-1:0]                      in_msg_hdr,
  input  logic     [c_nports-1:0][p_payload_nbits-1:0] in_msg_payload,

  output net_hdr_t [c_nports-1:0]                      out_msg_hdr,
  output logic     [c_nports-1:0][p_payload_nbits-1:0] out_msg_payload,

  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Define additional ports
  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
  output logic     [c_nports-1:0]                      inq_val,
  input  logic     [c_nports-1:0]                      inq_rdy,
  output logic     [c_nports-1:0][1:0]                 inq_dest,

  input  logic     [1:0]                               bus_sel
  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
);
  // c_nports included for convenience to avoid having magic numbers, but 
  // your design does not need to support other values of c_nports.
  localparam c_nports = 4;

  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Implement datapath
  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
  
  net_hdr_t [c_nports-1:0]                      inq_msg_hdr;
  logic     [c_nports-1:0][p_payload_nbits-1:0] inq_msg_payload;

  genvar i;
  generate
  for (i = 0; i < c_nports; i = i + 1 ) begin: INPUT_QUEUES
    // Since header and payload gets queued together, concatenate them
    // into one queue, and split them up again afterwards
    vc_Queue#(`VC_QUEUE_NORMAL, $bits(net_hdr_t) + p_payload_nbits, 4) in_queue
    (
      .clk(clk),
      .reset(reset),
      
      .num_free_entries(),

      .enq_val(in_val[i]),
      .enq_rdy(in_rdy[i]),
      .enq_msg({in_msg_hdr[i], in_msg_payload[i]}),

      .deq_val(inq_val[i]),
      .deq_rdy(inq_rdy[i]),
      .deq_msg({inq_msg_hdr[i], inq_msg_payload[i]})
    );

    assign inq_dest[i] = inq_msg_hdr[i].dest;
  end
  endgenerate

  vc_Bus #($bits(net_hdr_t), c_nports) hdr_bus
  (
    .sel(bus_sel),
    .in_(inq_msg_hdr),
    .out(out_msg_hdr)
  );

  vc_Bus #(p_payload_nbits, c_nports) payload_bus
  (
    .sel(bus_sel),
    .in_(inq_msg_payload),
    .out(out_msg_payload)
  );

  //'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

endmodule

`endif /* LAB4_NET_BUS_NET_DPATH_V */
