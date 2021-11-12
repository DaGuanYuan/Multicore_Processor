//=========================================================================
// Baseline Blocking Cache Control
//=========================================================================

`ifndef LAB3_MEM_BLOCKING_CACHE_BASE_CTRL_V
`define LAB3_MEM_BLOCKING_CACHE_BASE_CTRL_V

`include "vc/mem-msgs.v"
`include "vc/assert.v"
`include "vc/regfiles.v"

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Include necessary files
//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

module lab3_mem_BlockingCacheBaseCtrlVRTL
#(
  parameter p_idx_shamt    = 0
)
(
  input  logic                        clk,
  input  logic                        reset,

  // Cache Request

  input  logic                        cachereq_val,
  output logic                        cachereq_rdy,

  // Cache Response

  output logic                        cacheresp_val,
  input  logic                        cacheresp_rdy,

  // Memory Request

  output logic                        memreq_val,
  input  logic                        memreq_rdy,

  // Memory Response

  input  logic                        memresp_val,
  output logic                        memresp_rdy,

  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Define additional ports
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // Control Signals (ctrl -> datapath)

  // Tag Array Control Signals

  output logic                        cachereq_en,
  output logic                        tag_array_ren,
  output logic                        tag_array_wen,
  output logic                        evict_addr_reg_en,
  output logic                        memreq_addr_mux_sel,

  // Data Array Control Signals

  output logic                        memresp_en,
  output logic                        write_data_mux_sel,
  output logic                        data_array_ren,
  output logic                        data_array_wen,
  output logic [15:0]                 data_array_wben,
  output logic                        read_data_reg_en,
  output logic [2:0]                  read_word_mux_sel,

  // Output Control Signals

  output logic [2:0]                  cacheresp_type,
  output logic [2:0]                  memreq_type,
  output logic [1:0]                  hit,
  output logic                        val,

  // Status Signals (datapath -> ctrl)

  input  logic [2:0]                  cachereq_type,                 
  input  logic [31:0]                 cachereq_addr,                 
  input  logic                        tag_match
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

  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Implement control unit
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  //----------------------------------------------------------------------
  // State Definitions
  //----------------------------------------------------------------------

  localparam STATE_IDLE              = 4'd0;
  localparam STATE_TAG_CHECK         = 4'd1;
  localparam STATE_INIT_DATA_ACCESS  = 4'd2;
  localparam STATE_READ_DATA_ACCESS  = 4'd3;
  localparam STATE_WRITE_DATA_ACCESS = 4'd4;
  localparam STATE_EVICT_PREPARE     = 4'd5;
  localparam STATE_EVICT_REQUEST     = 4'd6;
  localparam STATE_EVICT_WAIT        = 4'd7;
  localparam STATE_REFILL_REQUEST    = 4'd8;
  localparam STATE_REFILL_WAIT       = 4'd9;
  localparam STATE_REFILL_UPDATE     = 4'd10;
  localparam STATE_WAIT              = 4'd11;

  //----------------------------------------------------------------------
  // State
  //----------------------------------------------------------------------

  logic [3:0] idx;
  logic [3:0] state_reg;
  logic [3:0] state_next;
  assign idx = cachereq_addr[p_idx_shamt + 7: p_idx_shamt + 4];

  always_ff @( posedge clk ) begin
    if ( reset ) begin
      state_reg <= STATE_IDLE;
    end
    else begin
      state_reg <= state_next;
    end
  end

  logic [15:0] valid;
  logic [15:0] dirty;
  logic        regfile_en;

  vc_ResetRegfile_1r1w #(1, 16, 0) valid_Regfile
  (
    .clk                    (clk),
    .reset                  (reset),
    .read_addr              (idx),
    .read_data              (valid[idx]),
    .write_en               (regfile_en),
    .write_addr             (idx),
    .write_data             (valid[idx])
  );

  vc_ResetRegfile_1r1w #(1, 16, 0) dirty_Regfile
  (
    .clk                    (clk),
    .reset                  (reset),
    .read_addr              (idx),
    .read_data              (dirty[idx]),
    .write_en               (regfile_en),
    .write_addr             (idx),
    .write_data             (dirty[idx])
  );

  //----------------------------------------------------------------------
  // State Transitions
  //----------------------------------------------------------------------

  // logic val;
  logic miss;
  logic init_transaction;
  logic rd;
  logic wr;
  logic rd_hit;
  logic wr_hit;
  logic dty;  // dirty bit

  assign val              = valid[idx]; 
  assign init_transaction = cachereq_type == `VC_MEM_REQ_MSG_TYPE_WRITE_INIT;
  assign rd               = cachereq_type == `VC_MEM_REQ_MSG_TYPE_READ;
  assign wr               = cachereq_type == `VC_MEM_REQ_MSG_TYPE_WRITE;
  assign rd_hit           = tag_match && rd;
  assign wr_hit           = tag_match && wr;
  assign miss             = !(rd_hit || wr_hit);
  assign dty              = dirty[idx];

  always_comb begin

    state_next = state_reg;

    case ( state_reg )

      STATE_IDLE:              if ( !cachereq_val )       state_next = STATE_IDLE;
                          else if (  cachereq_val )       state_next = STATE_TAG_CHECK;
      STATE_TAG_CHECK:         if (  init_transaction )   state_next = STATE_INIT_DATA_ACCESS;
                          else if (  rd_hit )             state_next = STATE_READ_DATA_ACCESS;
                          else if (  wr_hit )             state_next = STATE_WRITE_DATA_ACCESS;
                          else if (  miss && dty)         state_next = STATE_EVICT_PREPARE;
                          else if (  miss && !dty )       state_next = STATE_REFILL_REQUEST;      
      STATE_INIT_DATA_ACCESS:                             state_next = STATE_WAIT;
      STATE_READ_DATA_ACCESS:                             state_next = STATE_WAIT;
      STATE_WRITE_DATA_ACCESS:                            state_next = STATE_WAIT;
      STATE_EVICT_PREPARE:                                state_next = STATE_EVICT_REQUEST;
      STATE_EVICT_REQUEST:     if ( !memreq_rdy )         state_next = STATE_EVICT_REQUEST;
                          else if (  memreq_rdy )         state_next = STATE_EVICT_WAIT;      
      STATE_EVICT_WAIT:        if ( !memresp_val )        state_next = STATE_EVICT_WAIT;
                          else if (  memresp_val )        state_next = STATE_REFILL_REQUEST;      
      STATE_REFILL_REQUEST:    if ( !memreq_rdy )         state_next = STATE_REFILL_REQUEST;
                          else if (  memreq_rdy )         state_next = STATE_REFILL_WAIT;            
      STATE_REFILL_WAIT:       if ( !memresp_val )        state_next = STATE_REFILL_WAIT;
                          else if (  memresp_val )        state_next = STATE_REFILL_UPDATE;            
      STATE_REFILL_UPDATE:     if (  rd )                 state_next = STATE_READ_DATA_ACCESS;
                          else if (  wr )                 state_next = STATE_WRITE_DATA_ACCESS;                  
      STATE_WAIT:              if ( !cacheresp_rdy )      state_next = STATE_WAIT;
                          else if (  cacheresp_rdy )      state_next = STATE_IDLE;            
      default:                                            state_next = 'x;

    endcase

  end

  //----------------------------------------------------------------------
  // State Outputs
  //----------------------------------------------------------------------

  // Generic Parameters -- yes or no

  localparam n = 1'd0;
  localparam y = 1'd1;

  // Signals for muxes

  localparam wdm_x          = 1'dx;
  localparam wdm_rpl        = 1'd0;
  localparam wdm_mem        = 1'd1;

  localparam mam_x          = 1'dx;
  localparam mam_evt        = 1'd0;
  localparam mam_cch        = 1'd1;

  localparam rwm_x          = 3'dx;
  localparam rwm_w0         = 3'd0; // 0
  localparam rwm_w1         = 3'd1; // [31:0]
  localparam rwm_w2         = 3'd2; // [63:32]
  localparam rwm_w3         = 3'd3; // [95:64]
  localparam rwm_w4         = 3'd4; // [127:96]

  // Signals for hit (testing)

  localparam cache_x        = 2'bx;
  localparam cache_miss     = 2'b0;
  localparam cache_hit      = 2'b1;

  // Signals for memreq

  localparam memreq_x       = 3'dx;
  localparam memreq_rd      = `VC_MEM_REQ_MSG_TYPE_READ;
  localparam memreq_wr      = `VC_MEM_REQ_MSG_TYPE_WRITE;  
  localparam memreq_wn      = `VC_MEM_REQ_MSG_TYPE_WRITE_INIT; 

  // Signals for tag valid
  localparam t_v            = 1'd1;
  localparam t_i            = 1'd0;

  // Signals for tag dirty
  localparam t_d            = 1'd1;
  localparam t_c            = 1'd0;

  localparam t_x            = 1'dx;

    task cs
  (
    input logic       cs_cachereq_en,
    input logic       cs_tag_array_ren,
    input logic       cs_tag_array_wen,
    input logic       cs_evict_addr_reg_en,
    input logic       cs_memreq_addr_mux_sel,
    input logic       cs_memresp_en,
    input logic       cs_write_data_mux_sel,
    input logic       cs_data_array_ren,
    input logic       cs_data_array_wen,
    input logic       cs_read_data_reg_en,
    input logic [2:0] cs_memreq_type,
    input logic       cs_regfile_en,
    input logic       cs_valid,
    input logic       cs_dirty
  );
  begin
    cachereq_en          = cs_cachereq_en;
    tag_array_ren        = cs_tag_array_ren;
    tag_array_wen        = cs_tag_array_wen;
    evict_addr_reg_en    = cs_evict_addr_reg_en;
    memreq_addr_mux_sel  = cs_memreq_addr_mux_sel;
    memresp_en           = cs_memresp_en;
    write_data_mux_sel   = cs_write_data_mux_sel;
    data_array_ren       = cs_data_array_ren;
    data_array_wen       = cs_data_array_wen;
    read_data_reg_en     = cs_read_data_reg_en;
    memreq_type          = cs_memreq_type;
    regfile_en           = cs_regfile_en;
    valid[idx]           = cs_valid;
    dirty[idx]           = cs_dirty;
  end
  endtask

  // Set outputs using a control signal "table"

  always_comb begin

    // cs( 0, 0, a_x, b_x, result_x, 0, add_mux_x);
    case ( state_reg )
      //                                            creq tag  tag  evt memreq   mresp  wdata   data data rd    mem    reg  tag  tag
      //                                             en  ren  wen  en  muxsel    en    muxsel  ren  wen  en    type   fen  val dirty  
      STATE_IDLE:           if ( !cachereq_val )  cs( n,  n,   n,   n, mam_x  ,  n,   wdm_x  ,  n,   n,  n, memreq_x , n,  val, dty);
                       else if (  cachereq_val )  cs( y,  n,   n,   n, mam_x  ,  n,   wdm_x  ,  n,   n,  n, memreq_x , n,  val, dty);
      STATE_TAG_CHECK:                            cs( n,  y,   n,   n, mam_cch,  n,   wdm_x  ,  n,   n,  n, memreq_x , n,  val, dty);
      STATE_INIT_DATA_ACCESS:                     cs( n,  n,   y,   n, mam_cch,  y,   wdm_rpl,  n,   y,  n, memreq_wn, y,  t_v, t_c);
      STATE_READ_DATA_ACCESS:                     cs( n,  n,   n,   n, mam_x  ,  n,   wdm_x  ,  y,   n,  y, memreq_x , y,  t_v, dty);
      STATE_WRITE_DATA_ACCESS:                    cs( n,  n,   n,   n, mam_x  ,  n,   wdm_rpl,  n,   y,  n, memreq_x , y,  t_v, t_d);
      STATE_EVICT_PREPARE:                        cs( n,  y,   n,   y, mam_x  ,  n,   wdm_x  ,  y,   n,  y, memreq_x , y,  t_v, t_c);
      STATE_EVICT_REQUEST:                        cs( n,  y,   n,   y, mam_evt,  n,   wdm_x  ,  y,   n,  y, memreq_wr, n,  val, dty);
      STATE_EVICT_WAIT:                           cs( n,  n,   n,   n, mam_evt,  n,   wdm_x  ,  n,   n,  y, memreq_wr, n,  val, dty);
      STATE_REFILL_REQUEST:                       cs( n,  n,   n,   n, mam_cch,  n,   wdm_x  ,  n,   n,  n, memreq_rd, n,  val, dty);
      STATE_REFILL_WAIT:                          cs( n,  n,   n,   n, mam_cch,  y,   wdm_x  ,  n,   n,  n, memreq_rd, n,  val, dty);
      STATE_REFILL_UPDATE:                        cs( n,  n,   y,   n, mam_x  ,  n,   wdm_mem,  n,   y,  n, memreq_x , y,  t_v, t_c);
      STATE_WAIT:                                 cs( n,  n,   n,   n, mam_x  ,  n,   wdm_x  ,  n,   n,  n, memreq_x , n,  val, dty);
      default:                                    cs( n,  n,   n,   n, mam_x  ,  n,   wdm_x  ,  n,   n,  n, memreq_x , n,  val, dty);

    endcase

  end


  logic [1:0] offset; 
  assign cacheresp_type = cachereq_type;
  assign cachereq_rdy   = state_reg == STATE_IDLE;
  assign cacheresp_val  = state_reg == STATE_WAIT;
  assign memreq_val     = state_reg == STATE_EVICT_REQUEST || state_reg == STATE_REFILL_REQUEST;
  assign memresp_rdy    = state_reg == STATE_EVICT_WAIT || state_reg == STATE_REFILL_WAIT;
  assign offset         = cachereq_addr[3:2];

  always_comb begin
    if ((rd_hit || wr_hit) && state_reg == STATE_TAG_CHECK) begin
      hit = cache_hit;
    end else if (!(rd_hit || wr_hit) && state_reg == STATE_TAG_CHECK)begin
      hit = cache_miss;
    end else begin
      hit = hit;
    end
  end

  always_comb begin
    if (state_reg == STATE_WAIT || state_reg == STATE_READ_DATA_ACCESS) begin
      case ( offset )
        2'd0: read_word_mux_sel = rwm_w1;
        2'd1: read_word_mux_sel = rwm_w2;
        2'd2: read_word_mux_sel = rwm_w3;
        2'd3: read_word_mux_sel = rwm_w4;
        default: read_word_mux_sel = rwm_w0;
      endcase
    end else begin
      read_word_mux_sel = rwm_w0;
    end

  end

  always_comb begin
    if (state_reg == STATE_WRITE_DATA_ACCESS) begin
      case (offset)
          2'd0: data_array_wben = 16'h000f;
          2'd1: data_array_wben = 16'h00f0;
          2'd2: data_array_wben = 16'h0f00;
          2'd3: data_array_wben = 16'hf000; 
        default: data_array_wben = 16'hffff; 
      endcase
    end else begin
      data_array_wben = 16'hffff;
    end
  end
endmodule

`endif
