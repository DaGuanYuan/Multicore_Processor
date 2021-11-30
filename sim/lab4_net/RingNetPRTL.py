#=========================================================================
# RingNetPRTL.py
#=========================================================================

from pymtl        import *
from pclib.ifcs   import InValRdyBundle, OutValRdyBundle, ValRdyBundle
from pclib.ifcs   import NetMsg

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# LAB TASK: Include necessary components
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

from pclib.rtl    import NormalQueue

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

from RouterPRTL   import RouterPRTL

class RingNetPRTL( Model ):

  def __init__( s, payload_nbits = 32 ):

    # Parameters
    # Your design does not need to support other values

    num_ports    = 4
    opaque_nbits = 8 

    srcdest_nbits = clog2( num_ports )

    msg_type = NetMsg(num_ports, 2**opaque_nbits, payload_nbits)

    # Interface

    s.in_ = InValRdyBundle [num_ports]( msg_type )
    s.out = OutValRdyBundle[num_ports]( msg_type )

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # LAB TASK: Compose ring network
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

    # Router-Router connections

    # forward (increasing router id) wires

    s.forw_out_val  = Wire[num_ports]( 1 )
    s.forw_out_rdy  = Wire[num_ports]( 1 )
    s.forw_out_msg  = Wire[num_ports]( msg_type )

    s.forw_in_val   = Wire[num_ports]( 1 )
    s.forw_in_rdy   = Wire[num_ports]( 1 )
    s.forw_in_msg   = Wire[num_ports]( msg_type )

    # backward (decreasing router id) wires

    s.backw_out_val = Wire[num_ports]( 1 )
    s.backw_out_rdy = Wire[num_ports]( 1 )
    s.backw_out_msg = Wire[num_ports]( msg_type )

    s.backw_in_val  = Wire[num_ports]( 1 )
    s.backw_in_rdy  = Wire[num_ports]( 1 )
    s.backw_in_msg  = Wire[num_ports]( msg_type )

    # Routers

    s.routers = [ RouterPRTL( payload_nbits ) \
                  for i in xrange(num_ports) ]

    # X-th router's #0 connects to (X-1)-th forw/backw channel
    # X-th router's #2 connects to X-th forw/backw channel

    for i in xrange(num_ports):

      prev = (i+num_ports-1) % num_ports

      s.connect_pairs(
        s.routers[i].router_id, i,

        s.routers[i].in0.val,  s.forw_in_val[prev],
        s.routers[i].in0.rdy,  s.forw_in_rdy[prev],
        s.routers[i].in0.msg,  s.forw_in_msg[prev],

        s.routers[i].out0.val, s.backw_out_val[prev],
        s.routers[i].out0.rdy, s.backw_out_rdy[prev],
        s.routers[i].out0.msg, s.backw_out_msg[prev],

        s.routers[i].in1,      s.in_[i],
        s.routers[i].out1,     s.out[i],

        s.routers[i].out2.val, s.forw_out_val[i],
        s.routers[i].out2.rdy, s.forw_out_rdy[i],
        s.routers[i].out2.msg, s.forw_out_msg[i],

        s.routers[i].in2.val,  s.backw_in_val[i],
        s.routers[i].in2.rdy,  s.backw_in_rdy[i],
        s.routers[i].in2.msg,  s.backw_in_msg[i],
      )

    # Channels

    s.forw_channel_queues  = NormalQueue[num_ports]( 2, msg_type )
    s.backw_channel_queues = NormalQueue[num_ports]( 2, msg_type )

    for i in xrange(num_ports):

      # connect forward channels

      s.connect_pairs(
        s.forw_channel_queues[i].enq.val, s.forw_out_val[i],
        s.forw_channel_queues[i].enq.rdy, s.forw_out_rdy[i],
        s.forw_channel_queues[i].enq.msg, s.forw_out_msg[i],

        s.forw_channel_queues[i].deq.val, s.forw_in_val[i],
        s.forw_channel_queues[i].deq.rdy, s.forw_in_rdy[i],
        s.forw_channel_queues[i].deq.msg, s.forw_in_msg[i],
      )

      # connect backward channels

      s.connect_pairs(
        s.backw_channel_queues[i].enq.val, s.backw_out_val[i],
        s.backw_channel_queues[i].enq.rdy, s.backw_out_rdy[i],
        s.backw_channel_queues[i].enq.msg, s.backw_out_msg[i],

        s.backw_channel_queues[i].deq.val, s.backw_in_val[i],
        s.backw_channel_queues[i].deq.rdy, s.backw_in_rdy[i],
        s.backw_channel_queues[i].deq.msg, s.backw_in_msg[i],
      )

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

  def line_trace( s ):

    return "".join( [ x.line_trace() for x in s.routers] )
