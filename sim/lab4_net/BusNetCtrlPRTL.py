#=========================================================================
# BusNetCtrlPRTL.py
#=========================================================================
# This model implements 4-port (configurable) simple bus network.

from pymtl     import *

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# LAB TASK: Include necessary components
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

from pclib.rtl import RoundRobinArbiterEn

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

class BusNetCtrlPRTL( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s ):

    # Parameters
    # Your design does not need to support other values

    num_ports = 4

    # Interface

    s.out_val  = OutPort[num_ports]( 1 )
    s.out_rdy  = InPort [num_ports]( 1 )

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # LAB TASK: Define additional ports
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

    s.inq_val  = InPort [num_ports]( 1 )
    s.inq_rdy  = OutPort[num_ports]( 1 )
    s.inq_dest = InPort [num_ports]( clog2(num_ports) )

    s.bus_sel  = OutPort( clog2(num_ports) )

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # LAB TASK: Implement control unit
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

    # input request -> arbiter input

    s.arb_reqs = Wire( num_ports )

    for i in range( num_ports ):
      s.connect( s.inq_val[i], s.arb_reqs[i] )

    # The above implementation doesn't take the ready status of the
    # destination port into account, so resource waste is possible in the
    # sense that the inport is granted but the output port is not ready.
    #
    # To optimize performance, you not only need to AND the one-hot
    # destination signal of each inport with a concatenated ready status
    # of all ports, but also need to ADD A BYPASS QUEUE between the
    # arbiter output valrdybundle and the actual out valrdy bundle.
    #
    # This is because when we take rdy signal into arbitration, the output
    # val signal now depends on the output rdy signal which might create
    # trouble when the other end calculate the rdy signal based on the
    # valid signal. We have to avoid this loop and the simplest way is to
    # add a bypass queue.

    # @s.combinational
    # def comb_in_reqs():
    #   s.arb_reqs.value = 0
    #   for i in range( num_ports ):
    #     if s.inq_val[i]:
    #       s.arb_reqs[i].value = s.out_rdy[ s.inq_dest[i] ]

    # The arbiter arbitrates over the on-board signal of each port
    # and generates an one-hot signal out_grant
    # We provide the output ready signal arb_out_rdy as a feedback signal
    # to stop the arbitration when the destination of the arbitrated input
    # port is not ready.

    s.out_grant   = Wire( num_ports )
    s.arb_out_rdy = Wire( 1 )

    s.arbiter = RoundRobinArbiterEn( num_ports )
    s.connect_pairs(
      s.arbiter.reqs,   s.arb_reqs,
      s.arbiter.grants, s.out_grant,
      s.arbiter.en,     s.arb_out_rdy,
    )

    # granted: the arbitrated input port
    # dest: the destination of the granted input port

    s.granted = Wire( clog2(num_ports) )
    s.dest    = Wire( clog2(num_ports) )

    s.connect( s.granted, s.bus_sel )

    # Model an one-hot encoder to encode the arbitration -> "granted"
    # Set the valid bit of the destination outport of the granted inport

    @s.combinational
    def comb_calc_granted():
      s.granted.value = 0
      for i in range( num_ports ):
        s.out_val[i].value = 0

      for i in range( num_ports ):
        if s.out_grant[i]:
          s.granted.value = i
          s.dest.value    = s.inq_dest[i]
          s.out_val[ s.dest ].value = 1

    # Dequeue a message for i-th port when the request is granted and
    # the destination outport is ready 
    # Also provide the feedback rdy signal to the arbiter

    @s.combinational
    def comb_set_rdy():
      s.arb_out_rdy.value = 0
      for i in range( num_ports ):
        s.inq_rdy[i].value = 0

      if (s.out_grant != 0) & s.out_rdy[ s.dest ]:
        s.inq_rdy[ s.granted ].value = 1
        s.arb_out_rdy.value          = 1

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
