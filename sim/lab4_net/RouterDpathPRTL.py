#=========================================================================
# RouterDpathPRTL.py
#=========================================================================
# This model implements a 3-port router

from pymtl         import *
from pclib.ifcs    import NetMsg, InValRdyBundle

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# LAB TASK: Include necessary components
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

from pclib.rtl     import NormalQueue, Crossbar

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

class RouterDpathPRTL( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, payload_nbits = 32 ):

    # Parameters
    # Your design does not need to support other values

    nrouters     = 4
    opaque_nbits = 8

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    msg_type = NetMsg( nrouters, 2**opaque_nbits, payload_nbits)

    s.in0 = InValRdyBundle( msg_type )
    s.in1 = InValRdyBundle( msg_type )
    s.in2 = InValRdyBundle( msg_type )

    s.out0_msg  = OutPort( msg_type )
    s.out1_msg  = OutPort( msg_type )
    s.out2_msg  = OutPort( msg_type )

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # LAB TASK: Other interfaces/additional ports
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

    s.inq0_val  = OutPort( 1 )
    s.inq0_rdy  = InPort ( 1 )
    s.inq0_dest = OutPort( clog2(nrouters) )

    s.inq1_val  = OutPort( 1 )
    s.inq1_rdy  = InPort ( 1 )
    s.inq1_dest = OutPort( clog2(nrouters) )

    s.inq2_val  = OutPort( 1 )
    s.inq2_rdy  = InPort ( 1 )
    s.inq2_dest = OutPort( clog2(nrouters) )

    s.xbar_sel0 = InPort( 2 )
    s.xbar_sel1 = InPort( 2 )
    s.xbar_sel2 = InPort( 2 )

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # LAB TASK: Dpath components
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

    #---------------------------------------------------------------------
    # Components
    #---------------------------------------------------------------------

    # Crossbar

    s.xbar = m = Crossbar( 3, msg_type )

    s.connect_pairs(
      s.xbar_sel0, m.sel[0],
      s.xbar_sel1, m.sel[1],
      s.xbar_sel2, m.sel[2],

      s.out0_msg,  m.out[0],
      s.out1_msg,  m.out[1],
      s.out2_msg,  m.out[2],
    )

    # Queue for port 0

    s.in0_queue = m = NormalQueue( 2, msg_type )

    s.connect_pairs(
      s.in0, m.enq,

      s.inq0_val,    m.deq.val,
      s.inq0_rdy,    m.deq.rdy,
      s.inq0_dest,   m.deq.msg.dest,
      s.xbar.in_[0], m.deq.msg,
    )

    # Queue for port 1

    s.in1_queue = m = NormalQueue( 2, msg_type )

    s.connect_pairs(
      s.in1, m.enq,

      s.inq1_val,    m.deq.val,
      s.inq1_rdy,    m.deq.rdy,
      s.inq1_dest,   m.deq.msg.dest,
      s.xbar.in_[1], m.deq.msg,
    )

    # Queue for port 2

    s.in2_queue = m = NormalQueue( 2, msg_type )

    s.connect_pairs(
      s.in2, m.enq,

      s.inq2_val,    m.deq.val,
      s.inq2_rdy,    m.deq.rdy,
      s.inq2_dest,   m.deq.msg.dest,
      s.xbar.in_[2], m.deq.msg,
    )

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
