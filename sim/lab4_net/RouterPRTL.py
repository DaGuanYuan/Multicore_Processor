#=========================================================================
# RouterPRTL.py
#=========================================================================

from pymtl      import *
from pclib.ifcs import NetMsg
from pclib.ifcs import InValRdyBundle, OutValRdyBundle

from RouterDpathPRTL import RouterDpathPRTL
from RouterCtrlPRTL  import RouterCtrlPRTL

#-------------------------------------------------------------------------
# Top-level module
#-------------------------------------------------------------------------

class RouterPRTL( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, payload_nbits = 32 ):

    # Parameters
    # Your design does not need to support other values

    nrouters     = 4
    opaque_nbits = 8 

    srcdest_nbits = clog2( nrouters )

    # Interface

    s.router_id = InPort( srcdest_nbits )

    msg_type = NetMsg(nrouters, 2**opaque_nbits, payload_nbits)

    s.in0  = InValRdyBundle ( msg_type )
    s.in1  = InValRdyBundle ( msg_type )
    s.in2  = InValRdyBundle ( msg_type )

    s.out0 = OutValRdyBundle( msg_type )
    s.out1 = OutValRdyBundle( msg_type )
    s.out2 = OutValRdyBundle( msg_type )

    # Components

    s.dpath = RouterDpathPRTL( payload_nbits )
    s.ctrl  = RouterCtrlPRTL ()

    s.connect( s.ctrl.router_id, s.router_id )

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # LAB TASK: Connect datapath with control unit
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # LAB TASK: Connect inputs
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # LAB TASK: Connect outputs
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  #-----------------------------------------------------------------------
  # Line-trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    
    in0_str = s.in0.to_str( "%02s:%1s>%1s" % ( s.in0.msg.opaque, s.in0.msg.src, s.in0.msg.dest ) )
    in1_str = s.in1.to_str( "%02s:%1s>%1s" % ( s.in1.msg.opaque, s.in1.msg.src, s.in1.msg.dest ) )
    in2_str = s.in2.to_str( "%02s:%1s>%1s" % ( s.in2.msg.opaque, s.in2.msg.src, s.in2.msg.dest ) )

    return "({}|{}|{})".format( in0_str, in1_str, in2_str )


