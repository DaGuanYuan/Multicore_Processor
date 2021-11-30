#=========================================================================
# BusNetDpathPRTL.py
#=========================================================================
# This model implements 4-port (configurable) simple bus network.

from pymtl         import *
from pclib.ifcs    import NetMsg, InValRdyBundle

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# LAB TASK: Include necessary components
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

from pclib.rtl     import NormalQueue, Bus

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

class BusNetDpathPRTL( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, payload_nbits ):

    # Parameters
    # Your design does not need to support other values

    num_ports    = 4
    opaque_nbits = 8

    # Interface

    msg_type = NetMsg( num_ports, 2**opaque_nbits, payload_nbits )

    s.in_    = InValRdyBundle[num_ports]( msg_type )

    s.out_msg  = OutPort[num_ports]( msg_type )

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # LAB TASK: Define additional ports
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

    s.inq_val  = OutPort[num_ports]( 1 )
    s.inq_rdy  = InPort [num_ports]( 1 )
    s.inq_dest = OutPort[num_ports]( clog2(num_ports) )

    s.bus_sel  = InPort( clog2(num_ports) )

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # LAB TASK: Implement datapath
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

    # Dpath components

    s.in_queue = NormalQueue[num_ports]( num_ports, msg_type )
    s.bus      = Bus                   ( num_ports, msg_type )

    for i in xrange( num_ports ):
      s.connect_pairs(
        s.in_[i],  s.in_queue[i].enq,

        s.in_queue[i].deq.val, s.inq_val[i],
        s.in_queue[i].deq.rdy, s.inq_rdy[i],
        s.in_queue[i].deq.msg, s.bus.in_[i],

        s.in_queue[i].deq.msg.dest, s.inq_dest[i],

        s.out_msg[i], s.bus.out[i],
      )

    s.connect( s.bus_sel, s.bus.sel )

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
