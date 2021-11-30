#=========================================================================
# RouterCtrlPRTL.py
#=========================================================================

from pymtl      import *
from pclib.ifcs import NetMsg
from pclib.ifcs import InValRdyBundle, OutValRdyBundle

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# LAB TASK: Include necessary components
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

from pclib.rtl  import RoundRobinArbiterEn

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

class RouterCtrlPRTL( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s ):

    # Parameters
    # Your design does not need to support other values

    nrouters = 4 

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.router_id = InPort( clog2(nrouters) )

    s.out0_val  = OutPort( 1 )
    s.out0_rdy  = InPort ( 1 )

    s.out1_val  = OutPort( 1 )
    s.out1_rdy  = InPort ( 1 )

    s.out2_val  = OutPort( 1 )
    s.out2_rdy  = InPort ( 1 )

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # LAB TASK: Define additional ports
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

    # in0/out0: network channel on one side

    s.inq0_val  = InPort ( 1 )
    s.inq0_rdy  = OutPort( 1 )
    s.inq0_dest = InPort ( clog2(nrouters) )

    s.xbar_sel0 = OutPort( 2 )

    # in1/out1: the inject channel from the input terminal,
    #           the output channel to the output terminal

    s.inq1_val  = InPort ( 1 )
    s.inq1_rdy  = OutPort( 1 )
    s.inq1_dest = InPort ( clog2(nrouters) )

    s.xbar_sel1 = OutPort( 2 )

    # in2/out2: network channel on the other side

    s.inq2_val  = InPort ( 1 )
    s.inq2_rdy  = OutPort( 1 )
    s.inq2_dest = InPort ( clog2(nrouters) )

    s.xbar_sel2 = OutPort( 2 )

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # LAB TASK: Router control logic
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

    #---------------------------------------------------------------------
    # Logics
    #---------------------------------------------------------------------

    # Generate the one-hot request signal inX_reqs for each input and
    # gather outX_reqs for each output port
    # - If the packet is for this port, redirect it to the terminal
    # - Otherwise we just forward it

    s.in0_reqs  = Wire( 3 )
    s.in1_reqs  = Wire( 3 )
    s.in2_reqs  = Wire( 3 )

    s.out0_reqs = Wire( 3 )
    s.out1_reqs = Wire( 3 )
    s.out2_reqs = Wire( 3 )

    @s.combinational
    def comb_in_req_signals():

      s.in0_reqs.value = Bits( 3, 0b000 )
      s.in1_reqs.value = Bits( 3, 0b000 )
      s.in2_reqs.value = Bits( 3, 0b000 )

      if s.inq0_val:
        if s.inq0_dest == s.router_id:
          s.in0_reqs.value = Bits( 3, 0b010 )
        else:
          s.in0_reqs.value = Bits( 3, 0b100 )

      # Greedy routing for input terminal: calculate forward/backward hops

      backw_hops = s.router_id - s.inq1_dest
      forw_hops  = s.inq1_dest - s.router_id

      if s.inq1_val:
        if s.inq1_dest == s.router_id:
          s.in1_reqs.value = Bits( 3, 0b010 )

        # Let's do greedy first
        elif forw_hops < backw_hops:
          s.in1_reqs.value = Bits( 3, 0b100 )
        elif forw_hops > backw_hops:
          s.in1_reqs.value = Bits( 3, 0b001 )

        # If tied, then odd/even
        elif s.router_id[0]: # odd
          s.in1_reqs.value = Bits( 3, 0b100 )
        else:
          s.in1_reqs.value = Bits( 3, 0b001 )

      if s.inq2_val:
        if s.inq2_dest == s.router_id:
          s.in2_reqs.value = Bits( 3, 0b010 )
        else:
          s.in2_reqs.value = Bits( 3, 0b001 )

      s.out0_reqs.value  = concat( s.in2_reqs[0], s.in1_reqs[0], s.in0_reqs[0] )
      s.out1_reqs.value  = concat( s.in2_reqs[1], s.in1_reqs[1], s.in0_reqs[1] )
      s.out2_reqs.value  = concat( s.in2_reqs[2], s.in1_reqs[2], s.in0_reqs[2] )

    s.out0_grants = Wire( 3 )
    s.out1_grants = Wire( 3 )
    s.out2_grants = Wire( 3 )

    #-----------------------------------------------------------------------
    # arbiter for #0 (channel port)
    #-----------------------------------------------------------------------

    s.arbiter_out0 = m = RoundRobinArbiterEn( 3 )

    s.connect_pairs(
      s.out0_reqs,   m.reqs,
      s.out0_grants, m.grants,
      s.out0_rdy,    m.en,    # Update the priority if the port is ready
    )

    @s.combinational
    def comb_out0_grant():

      s.out0_val.value = reduce_or( s.out0_grants )

      if   s.out0_grants == Bits( 3, 0b001 ):
        s.xbar_sel0.value = Bits( 2, 0x0 )
      elif s.out0_grants == Bits( 3, 0b010 ):
        s.xbar_sel0.value = Bits( 2, 0x1 )
      else:
        s.xbar_sel0.value = Bits( 2, 0x2 )

    #-----------------------------------------------------------------------
    # arbiter for #1 (terminal port)
    #-----------------------------------------------------------------------

    s.arbiter_out1 = m = RoundRobinArbiterEn( 3 )

    s.connect_pairs(
      s.out1_reqs,   m.reqs,
      s.out1_grants, m.grants,
      s.out1_rdy,    m.en,    # Update the priority if the port is ready
    )

    @s.combinational
    def comb_out1_grant():

      s.out1_val.value = reduce_or( s.out1_grants )

      if   s.out1_grants == Bits( 3, 0b001 ):
        s.xbar_sel1.value = Bits( 2, 0x0 )
      elif s.out1_grants == Bits( 3, 0b010 ):
        s.xbar_sel1.value = Bits( 2, 0x1 )
      else:
        s.xbar_sel1.value = Bits( 2, 0x2 )

    #-----------------------------------------------------------------------
    # arbiter for #2 (channel port)
    #-----------------------------------------------------------------------

    s.arbiter_out2 = m =  RoundRobinArbiterEn( 3 )

    s.connect_pairs(
      s.out2_reqs,   m.reqs,
      s.out2_grants, m.grants,
      s.out2_rdy,    m.en,    # Update the priority if the port is ready
    )

    @s.combinational
    def comb_out2_grant():

      s.out2_val.value = reduce_or( s.out2_grants )

      if   s.out2_grants == Bits( 3, 0b001 ):
        s.xbar_sel2.value = Bits( 2, 0x0 )
      elif s.out2_grants == Bits( 3, 0b010 ):
        s.xbar_sel2.value = Bits( 2, 0x1 )
      else:
        s.xbar_sel2.value = Bits( 2, 0x2 )

    # Translate the arbiter grant signals back to each input
    # Also propagate the outX.rdy signal back to deq.rdy

    s.in0_grants  = Wire( 3 )
    s.in1_grants  = Wire( 3 )
    s.in2_grants  = Wire( 3 )

    @s.combinational
    def comb_grants_feedback():

      s.in0_grants.value  = concat( s.out2_grants[0], s.out1_grants[0], s.out0_grants[0] )
      s.in1_grants.value  = concat( s.out2_grants[1], s.out1_grants[1], s.out0_grants[1] )
      s.in2_grants.value  = concat( s.out2_grants[2], s.out1_grants[2], s.out0_grants[2] )

      outs_rdy = concat( s.out2_rdy, s.out1_rdy, s.out0_rdy )

      s.inq0_rdy.value = reduce_or( s.in0_reqs & s.in0_grants & outs_rdy )
      s.inq1_rdy.value = reduce_or( s.in1_reqs & s.in1_grants & outs_rdy )
      s.inq2_rdy.value = reduce_or( s.in2_reqs & s.in2_grants & outs_rdy )

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
