//=========================================================================
// Alternative Blocking Cache Datapath
//=========================================================================

`ifndef LAB3_MEM_BLOCKING_CACHE_ALT_DPATH_V
`define LAB3_MEM_BLOCKING_CACHE_ALT_DPATH_V

`include "vc/mem-msgs.v"
`include "vc/muxes.v"
`include "vc/arithmetic.v"
`include "vc/srams.v"
`include "vc/regs.v"

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Include necessary files
//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

module lab3_mem_BlockingCacheAltDpathVRTL
#(
  parameter p_idx_shamt    = 0
)
(
  input  logic                        clk,
  input  logic                        reset,

  // Cache Request

  input  mem_req_4B_t                 cachereq_msg,

  // Cache Response

  output mem_resp_4B_t                cacheresp_msg,

  // Memory Request

  output mem_req_16B_t                memreq_msg,

  // Memory Response

  input  mem_resp_16B_t               memresp_msg,

  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Define additional ports
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  // Control Signals (ctrl -> datapath)

  // Tag Array Control Signals

  input  logic                        cachereq_en,
  input  logic                        tag_array_ren,
  input  logic                        tag_array_wen0,
  input  logic                        tag_array_wen1,
  input  logic                        tag_check_reg_en,
  input  logic                        victim_reg_en,
  input  logic                        evict_addr_reg_en,
  input  logic                        victim_mux_sel,
  input  logic                        memreq_addr_mux_sel,

  // Data Array Control Signals

  input  logic                        memresp_en,
  input  logic                        write_data_mux_sel,
  input  logic                        data_array_ren,
  input  logic                        data_array_wen,
  input  logic [15:0]                 data_array_wben,
  input  logic                        read_data_reg_en,
  input  logic [2:0]                  read_word_mux_sel,
  input  logic [3:0]                  idx_data_array,

  // Output Control Signals

  input  logic [2:0]                  cacheresp_type,
  input  logic [2:0]                  memreq_type,
  input  logic [1:0]                  hit,
  input                               val0,
  input                               val1,
  input                               victim,

  // Status Signals (datapath -> ctrl)

  output logic [2:0]                  cachereq_type,                 
  output logic [31:0]                 cachereq_addr,                 
  output logic                        tag_match,
  output logic                        idx_way            

);

  // local parameters not meant to be set from outside
  localparam size = 256;             // Cache size in bytes
  localparam dbw  = 32;              // Short name for data bitwidth
  localparam abw  = 32;              // Short name for addr bitwidth
  localparam o    = 8;               // Short name for opaque bitwidth
  localparam clw  = 128;             // Short name for cacheline bitwidth
  localparam nbl  = size*8/clw;      // Number of blocks in the cache
  localparam nby  = nbl;             // Number of blocks per way
  localparam idw  = $clog2(nby);     // Short name for index bitwidth
  localparam ofw  = $clog2(clw/8);   // Short name for the offset bitwidth
  // In this lab, to simplify things, we always use all bits except for the
  // offset in the tag, rather than storing the "normal" 24 bits. This way,
  // when implementing a multi-banked cache, we don't need to worry about
  // re-inserting the bank id into the address of a cacheline.
  localparam tgw  = abw - ofw;       // Short name for the tag bitwidth

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Implement data-path
//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

//--------------------------------------------------------------------
// Data Path Through "Tag" Array
//--------------------------------------------------------------------
  logic [2:0]  cachereq_msg_type;
  logic [7:0]  cachereq_msg_opaque;
  logic [31:0] cachereq_msg_addr;
  logic [31:0] cachereq_msg_data;
  logic [7:0]  cachereq_opaque;
  logic [31:0] cachereq_data;
  assign cachereq_msg_type   = cachereq_msg.type_;
  assign cachereq_msg_opaque = cachereq_msg.opaque;
  assign cachereq_msg_addr   = cachereq_msg.addr;
  assign cachereq_msg_data   = cachereq_msg.data;

  vc_EnResetReg #(8) cachereq_opaque_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (cachereq_en),
    .d      (cachereq_msg_opaque),
    .q      (cachereq_opaque)
  );

  vc_EnResetReg #(3) cachereq_type_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (cachereq_en),
    .d      (cachereq_msg_type),
    .q      (cachereq_type)
  );

  vc_EnResetReg #(32) cachereq_addr_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (cachereq_en),
    .d      (cachereq_msg_addr),
    .q      (cachereq_addr)
  );

  vc_EnResetReg #(32) cachereq_data_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (cachereq_en),
    .d      (cachereq_msg_data),
    .q      (cachereq_data)
  );

  logic [2:0]  idx;
  logic [27:0] tag;
  logic [27:0] read_tag0;  // read_data output for tag array0
  logic [27:0] read_tag1;  // read_data output for tag array1
  logic        compare_rst0;  // cmp0 rst
  logic        compare_rst1;  // cmp1 rst
  assign idx  = cachereq_addr[p_idx_shamt + 6: p_idx_shamt + 4];
  assign tag  = cachereq_addr[31:4];

  // Tag Array

  vc_CombinationalBitSRAM_1rw #(28,8) tag_array0
  (
    .clk            (clk),
    .reset          (reset),
    .read_en        (tag_array_ren),
    .read_addr      (idx),
    .read_data      (read_tag0),
    .write_en       (tag_array_wen0),
    .write_addr     (idx),
    .write_data     (tag)
  );

  vc_CombinationalBitSRAM_1rw #(28,8) tag_array1
  (
    .clk            (clk),
    .reset          (reset),
    .read_en        (tag_array_ren),
    .read_addr      (idx),
    .read_data      (read_tag1),
    .write_en       (tag_array_wen1),
    .write_addr     (idx),
    .write_data     (tag)
  );

  vc_EqComparator #(28) comparator0
  (
    .in0            (tag),
    .in1            (read_tag0),
    .out            (compare_rst0)
  );

  vc_EqComparator #(28) comparator1
  (
    .in0            (tag),
    .in1            (read_tag1),
    .out            (compare_rst1)
  );
  
  assign tag_match = (compare_rst0 && val0) || (compare_rst1 && val1);

  logic tag_check_reg_out;
  logic victim_reg_out;

  vc_EnResetReg #(1) tag_check_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (tag_check_reg_en),
    .d      (compare_rst1),
    .q      (tag_check_reg_out)
  );  

  vc_EnResetReg #(1) victim_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (victim_reg_en),
    .d      (victim),
    .q      (victim_reg_out)
  );

  vc_Mux2 #(1) victim_mux
  (
    .in0    (victim_reg_out),
    .in1    (tag_check_reg_out),
    .sel    (victim_mux_sel),
    .out    (idx_way)
  );

  logic [31:0] tag_mkaddr;  // {tag, 4'b0000}
  logic [31:0] read_tag0_mkaddr; // {read_tag0, 4'b0000}
  logic [31:0] read_tag1_mkaddr; // {read_tag1, 4'b0000}
  logic [31:0] evict_mux_out;
  logic [31:0] evict_addr;  // output for evict_addr_reg
  logic [31:0] memreq_addr;
  assign tag_mkaddr       = {tag, 4'b0000};
  assign read_tag0_mkaddr  = {read_tag0, 4'b0000};
  assign read_tag1_mkaddr  = {read_tag1, 4'b0000};

  vc_Mux2 #(32) evict_mux
  (
    .in0    (read_tag0_mkaddr),
    .in1    (read_tag1_mkaddr),
    .sel    (victim),
    .out    (evict_mux_out)
  );

  vc_EnResetReg #(32) evict_addr_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (evict_addr_reg_en),
    .d      (evict_mux_out),
    .q      (evict_addr)
  );

  vc_Mux2 #(32) memreq_addr_mux
  (
    .in0    (evict_addr),
    .in1    (tag_mkaddr),
    .sel    (memreq_addr_mux_sel),
    .out    (memreq_addr)
  );

//--------------------------------------------------------------------
// Data Path Through Data Array
//--------------------------------------------------------------------

  logic [127:0] memresp_msg_data;
  logic [127:0] memresp_data; // signal after memresp_data_reg
  assign memresp_msg_data = memresp_msg.data;  

  vc_EnResetReg #(128) memresp_data_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (memresp_en),
    .d      (memresp_msg_data),
    .q      (memresp_data)
  );

  logic [127:0] cachereq_data_replicated;
  logic [127:0] write_data; // signal after write_data_mux_sel
  assign cachereq_data_replicated = {4{cachereq_data}};

  vc_Mux2 #(128) write_data_mux
  (
    .in0    (cachereq_data_replicated),
    .in1    (memresp_data),
    .sel    (write_data_mux_sel),
    .out    (write_data)
  );

  // Data Array

  logic [127:0] read_data_from_data_array; // read_data output for data array
  logic [127:0] read_data; // output for read_data_reg

  vc_CombinationalSRAM_1rw #(128, 16) data_array
  (
    .clk            (clk),
    .reset          (reset),
    .read_en        (data_array_ren),
    .read_addr      (idx_data_array),
    .read_data      (read_data_from_data_array),
    .write_en       (data_array_wen),
    .write_byte_en  (data_array_wben),
    .write_addr     (idx_data_array),
    .write_data     (write_data)    
  );

  vc_EnResetReg #(128) read_data_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (read_data_reg_en),
    .d      (read_data_from_data_array),
    .q      (read_data)
  );

  logic [31:0] cacheresp_data;

  vc_Mux5 #(32) read_word_mux
  (
    .in0    (0),
    .in1    (read_data[31:0]),
    .in2    (read_data[63:32]),
    .in3    (read_data[95:64]),
    .in4    (read_data[127:96]),
    .sel    (read_word_mux_sel),
    .out    (cacheresp_data)
  );

//--------------------------------------------------------------------
// Output of the Cache
//--------------------------------------------------------------------

  assign cacheresp_msg.opaque = cachereq_opaque; 
  assign cacheresp_msg.type_  = cacheresp_type;
  assign cacheresp_msg.len    = 2'b0;
  assign cacheresp_msg.test   = hit;
  assign cacheresp_msg.data   = cacheresp_data;

  assign memreq_msg.type_     = memreq_type;
  assign memreq_msg.len       = 4'd0;
  assign memreq_msg.addr      = memreq_addr;
  assign memreq_msg.data      = read_data;
  assign memreq_msg.opaque    = 8'b0;

endmodule

`endif
