#=========================================================================
# BlockingCacheFL_test.py
#=========================================================================

from __future__ import print_function

import pytest
import random
import struct
import math

random.seed(0xa4e28cc2)

from pymtl      import *
from pclib.test import mk_test_case_table, run_sim
from pclib.test import TestSource
from pclib.test import TestMemory

from pclib.ifcs import MemMsg,    MemReqMsg,    MemRespMsg
from pclib.ifcs import MemMsg4B,  MemReqMsg4B,  MemRespMsg4B
from pclib.ifcs import MemMsg16B, MemReqMsg16B, MemRespMsg16B

from TestCacheSink   import TestCacheSink
from lab3_mem.BlockingCacheFL import BlockingCacheFL

# We define all test cases here. They will be used to test _both_ FL and
# RTL models.
#
# Notice the difference between the TestHarness instances in FL and RTL.
#
# class TestHarness( Model ):
#   def __init__( s, src_msgs, sink_msgs, stall_prob, latency,
#                 src_delay, sink_delay, CacheModel, check_test, dump_vcd )
#
# The last parameter of TestHarness, check_test is whether or not we
# check the test field in the cacheresp. In FL model we don't care about
# test field and we set cehck_test to be False because FL model is just
# passing through cachereq to mem, so all cachereq sent to the FL model
# will be misses, whereas in RTL model we must set check_test to be True
# so that the test sink will know if we hit the cache properly.

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Model ):

  def __init__( s, src_msgs, sink_msgs, stall_prob, latency,
                src_delay, sink_delay, 
                CacheModel, num_banks, check_test, dump_vcd ):

    # Messge type

    cache_msgs = MemMsg4B()
    mem_msgs   = MemMsg16B()

    # Instantiate models

    s.src   = TestSource   ( cache_msgs.req,  src_msgs,  src_delay  )
    s.cache = CacheModel   ( num_banks = num_banks )
    s.mem   = TestMemory   ( mem_msgs, 1, stall_prob, latency )
    s.sink  = TestCacheSink( cache_msgs.resp, sink_msgs, sink_delay, check_test )

    # Dump VCD

    if dump_vcd:
      s.cache.vcd_file = dump_vcd

    # Connect

    s.connect( s.src.out,       s.cache.cachereq  )
    s.connect( s.sink.in_,      s.cache.cacheresp )

    s.connect( s.cache.memreq,  s.mem.reqs[0]     )
    s.connect( s.cache.memresp, s.mem.resps[0]    )

  def load( s, addrs, data_ints ):
    for addr, data_int in zip( addrs, data_ints ):
      data_bytes_a = bytearray()
      data_bytes_a.extend( struct.pack("<I",data_int) )
      s.mem.write_mem( addr, data_bytes_a )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace() + " " + s.cache.line_trace() + " " \
         + s.mem.line_trace() + " " + s.sink.line_trace()

#-------------------------------------------------------------------------
# make messages
#-------------------------------------------------------------------------

def req( type_, opaque, addr, len, data ):
  msg = MemReqMsg4B()

  if   type_ == 'rd': msg.type_ = MemReqMsg.TYPE_READ
  elif type_ == 'wr': msg.type_ = MemReqMsg.TYPE_WRITE
  elif type_ == 'in': msg.type_ = MemReqMsg.TYPE_WRITE_INIT

  msg.addr   = addr
  msg.opaque = opaque
  msg.len    = len
  msg.data   = data
  return msg

def resp( type_, opaque, test, len, data ):
  msg = MemRespMsg4B()

  if   type_ == 'rd': msg.type_ = MemRespMsg.TYPE_READ
  elif type_ == 'wr': msg.type_ = MemRespMsg.TYPE_WRITE
  elif type_ == 'in': msg.type_ = MemRespMsg.TYPE_WRITE_INIT

  msg.opaque = opaque
  msg.len    = len
  msg.test   = test
  msg.data   = data
  return msg

#----------------------------------------------------------------------
# Test Case: read hit path
#----------------------------------------------------------------------
# The test field in the response message: 0 == MISS, 1 == HIT

def read_hit_1word_clean( base_addr ):
  return [
    #    type  opq  addr      len data                type  opq  test len data
    req( 'in', 0x0, base_addr, 0, 0xdeadbeef ), resp( 'in', 0x0, 0,   0,  0          ),
    req( 'rd', 0x1, base_addr, 0, 0          ), resp( 'rd', 0x1, 1,   0,  0xdeadbeef ),
  ]

# Only one init transcation at the beginning
# def read_hit_2word_clean( base_addr ):
#   return [
#     #    type  opq  addr       len data                type  opq  test len data
#     req( 'in', 0x0, 0x00000000, 0, 0xdeadbeef ), resp( 'in', 0x0, 0,   0,  0          ),
    
#     req( 'in', 0x2, 0x00001000, 0, 0x00c0ffee ), resp( 'in', 0x2, 0,   0,  0          ),
#     req( 'rd', 0x1, 0x00000000, 0, 0          ), resp( 'rd', 0x1, 0,   0,  0x00000000 ),
#     req( 'rd', 0x3, 0x00001000, 0, 0          ), resp( 'rd', 0x3, 0,   0,  0x00c0ffee ),
#   ]

#----------------------------------------------------------------------
# Test Case: read hit path -- for set-associative cache
#----------------------------------------------------------------------
# This set of tests designed only for alternative design
# The test field in the response message: 0 == MISS, 1 == HIT

def read_hit_asso( base_addr ):
  return [
    #    type  opq  addr       len data                type  opq  test len data
    req( 'wr', 0x0, 0x00000000, 0, 0xdeadbeef ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'wr', 0x1, 0x00001000, 0, 0x00c0ffee ), resp( 'wr', 0x1, 0,   0,  0          ),
    req( 'rd', 0x2, 0x00000000, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0xdeadbeef ),
    req( 'rd', 0x3, 0x00001000, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x00c0ffee ),
  ]

#----------------------------------------------------------------------
# Test Case: read hit path -- for direct-mapped cache
#----------------------------------------------------------------------
# This set of tests designed only for baseline design

def read_hit_dmap( base_addr ):
  return [
    #    type  opq  addr       len data                type  opq  test len data
    req( 'wr', 0x0, 0x00000000, 0, 0xdeadbeef ), resp( 'wr', 0x0, 0,   0,  0          ),
    req( 'wr', 0x1, 0x00000080, 0, 0x00c0ffee ), resp( 'wr', 0x1, 0,   0,  0          ),
    req( 'rd', 0x2, 0x00000000, 0, 0          ), resp( 'rd', 0x2, 1,   0,  0xdeadbeef ),
    req( 'rd', 0x3, 0x00000080, 0, 0          ), resp( 'rd', 0x3, 1,   0,  0x00c0ffee ),
  ]

#-------------------------------------------------------------------------
# Test Case: write hit path
#-------------------------------------------------------------------------

def write_hit_1word_clean( base_addr ):
  return [
    #    type  opq   addr      len data               type  opq   test len data
    req( 'in', 0x00, base_addr, 0, 0x0a0b0c0d ), resp('in', 0x00, 0,   0,  0          ), # write word  0x00000000
    req( 'wr', 0x01, base_addr, 0, 0xbeefbeeb ), resp('wr', 0x01, 1,   0,  0          ), # write word  0x00000000
    req( 'rd', 0x02, base_addr, 0, 0          ), resp('rd', 0x02, 1,   0,  0xbeefbeeb ), # read  word  0x00000000
  ]

def write_hit_2word_clean( base_addr ):
  return [
    #    type  opq   addr      len data               type  opq   test len data
    req( 'in', 0x00, base_addr, 0, 0x0a0b0c0d ), resp('in', 0x00, 0,   0,  0          ), # write word  0x00000000
    req( 'wr', 0x01, base_addr, 0, 0xbeefbeeb ), resp('wr', 0x01, 1,   0,  0          ), # write word  0x00000000
    req( 'rd', 0x02, base_addr, 0, 0          ), resp('rd', 0x02, 1,   0,  0xbeefbeeb ), # read  word  0x00000000
    req( 'in', 0x03, 0x00001000, 0, 0x00c0ffee ), resp('in', 0x03, 0,   0,  0          ), # write word  0x00001000
    req( 'wr', 0x04, 0x00001000, 0, 0xbeefdead ), resp('wr', 0x04, 1,   0,  0          ), # write word  0x00001000
    req( 'rd', 0x05, 0x00001000, 0, 0          ), resp('rd', 0x05, 1,   0,  0xbeefdead ), # read  word  0x00001000
  ]

#----------------------------------------------------------------------
# Test Case: read hit path for dirty lines
#----------------------------------------------------------------------
# The test field in the response message: 0 == MISS, 1 == HIT

def read_hit_1word_dirty( base_addr ):
  return [
    #    type  opq  addr      len data                type  opq  test len data
    req( 'in', 0x00, base_addr, 0, 0x0a0b0c0d ), resp('in', 0x00, 0,   0,  0          ), # write word  0x00000000
    req( 'wr', 0x01, base_addr, 0, 0x00c0ffee ), resp('wr', 0x01, 1,   0,  0          ), # write word  0x00000000   set dirty bit
    req( 'rd', 0x02, base_addr, 0, 0          ), resp('rd', 0x02, 1,   0,  0x00c0ffee ), # read  word  0x00000000   hit dirty line
  ]

#----------------------------------------------------------------------
# Test Case: write hit path for dirty lines
#----------------------------------------------------------------------
# The test field in the response message: 0 == MISS, 1 == HIT

def write_hit_1word_dirty( base_addr ):
  return [
    #    type  opq  addr      len data                type  opq  test len data
    req( 'in', 0x00, base_addr, 0, 0x0a0b0c0d ), resp('in', 0x00, 0,   0,  0          ), # write word  0x00000000
    req( 'wr', 0x01, base_addr, 0, 0x00c0ffee ), resp('wr', 0x01, 1,   0,  0          ), # write word  0x00000000   set dirty bit
    req( 'wr', 0x02, base_addr, 0, 0xdeadbeef ), resp('wr', 0x02, 1,   0,  0          ), # write word  0x00000000   hit dirty line
    req( 'rd', 0x03, base_addr, 0, 0          ), resp('rd', 0x03, 1,   0,  0xdeadbeef ), # read  word  0x00000000   hit updated line
  ]
  
#-------------------------------------------------------------------------
# Test Case: read miss path
#-------------------------------------------------------------------------

def read_miss_1word_msg( base_addr ):
  return [
    #    type  opq   addr      len  data               type  opq test len  data
    req( 'rd', 0x00, 0x00000000, 0, 0          ), resp('rd', 0x00, 0, 0, 0xdeadbeef ), # read word  0x00000000
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ), # read word  0x00000004
  ]

# Data to be loaded into memory before running the test

def read_miss_1word_mem( base_addr ):
  return [
    # addr      data (in int)
    0x00000000, 0xdeadbeef,
    0x00000004, 0x00c0ffee,
  ]

#-------------------------------------------------------------------------
# Test Case: write miss path
#-------------------------------------------------------------------------

def write_miss_1word_msg( base_addr ):
  return [
    #    type  opq   addr       len  data              type  opq  test len data
    req( 'wr', 0x00, 0x00000000, 0, 0x005a5a5a ), resp('wr', 0x00, 0,   0, 0          ), # write word 0x00000000   set dirty bit
    req( 'rd', 0x01, 0x00000000, 0, 0          ), resp('rd', 0x01, 1,   0, 0x005a5a5a ), # read word  0x00000000
    req( 'rd', 0x02, 0x00000004, 0, 0          ), resp('rd', 0x02, 1,   0, 0x00c0ffee ), # read word  0x00000004
  ]

# Data to be loaded into memory before running the test

def write_miss_1word_mem( base_addr ):
  return [
    # addr      data (in int)
    0x00000000, 0xdeadbeef,
    0x00000004, 0x00c0ffee,
  ]

#-------------------------------------------------------------------------
# Test Case: read miss path with refill and eviction
#-------------------------------------------------------------------------

def read_miss_evict_msg( base_addr ):
  return [
    #    type  opq   addr      len  data               type  opq test  len data
    req( 'wr', 0x00, 0x00000000, 0, 0x3b3b3b3b ), resp('wr', 0x00, 0,   0, 0          ), # write word 0x00000000   set dirty bit
    req( 'rd', 0x01, 0x00000100, 0, 0          ), resp('rd', 0x01, 0,   0, 0xa5a5a5a5 ), # read word  0x00000100   evict first and then refill
    req( 'rd', 0x02, 0x00000104, 0, 0          ), resp('rd', 0x02, 1,   0, 0xf1f1f1f1 ), # read word  0x00000104   check cache line brought back from memory
    req( 'rd', 0x03, 0x00000000, 0, 0          ), resp('rd', 0x03, 0,   0, 0x3b3b3b3b ), # read word  0x00000000   check cache line brought back from memory
    req( 'rd', 0x04, 0x00000004, 0, 0          ), resp('rd', 0x04, 1,   0, 0x00c0ffee ), # read word  0x00000004   check cache line brought back from memory
  ]

# Data to be loaded into memory before running the test

def read_miss_evict_mem( base_addr ):
  return [
    # addr      data (in int)
    0x00000000, 0xdeadbeef,
    0x00000004, 0x00c0ffee,
    0x00000100, 0xa5a5a5a5,
    0x00000104, 0xf1f1f1f1,
  ]

#-------------------------------------------------------------------------
# Test Case: write miss path with refill and eviction
#-------------------------------------------------------------------------

def write_miss_evict_msg( base_addr ):
  return [
    #    type  opq   addr      len  data               type  opq test  len data
    req( 'rd', 0x00, 0x00000000, 0, 0          ), resp('rd', 0x00, 0,   0, 0xdeadbeef ), # read word  0x00000000   read with refill, fetch cache line 0 into set 0, still clean
    req( 'wr', 0x01, 0x00000004, 0, 0x3b3b3b3b ), resp('wr', 0x01, 1,   0, 0          ), # write word 0x00000004   write hit, set dirty bit
    req( 'wr', 0x02, 0x00000108, 0, 0x49494949 ), resp('wr', 0x02, 0,   0, 0          ), # write word 0x00000108   write miss, evict and then refill another block from memory
    req( 'rd', 0x03, 0x00000100, 0, 0          ), resp('rd', 0x03, 1,   0, 0x00000000 ), # read word  0x00000100   check cache line brought back from memory
    req( 'rd', 0x04, 0x00000104, 0, 0          ), resp('rd', 0x04, 1,   0, 0x00000000 ), # read word  0x00000104   check cache line brought back from memory
    req( 'rd', 0x05, 0x00000108, 0, 0          ), resp('rd', 0x05, 1,   0, 0x49494949 ), # read word  0x00000108   check cache line brought back from memory
  ]

# Data to be loaded into memory before running the test

def write_miss_evict_mem( base_addr ):
  return [
    # addr      data (in int)
    0x00000000, 0xdeadbeef,
    0x00000004, 0x00c0ffee,
    0x00000008, 0xa5a5a5a5,
    0x0000000c, 0xf1f1f1f1,
  ]

#-------------------------------------------------------------------------
# Test Case: Stressing entire cache, not just a few cache lines
#-------------------------------------------------------------------------

def entire_cache_read_msg( base_addr ):
  return [
    #    type  opq   addr      len  data               type  opq test len  data
    req( 'rd', 0x00, 0x00000000, 0, 0          ), resp('rd', 0x00, 0, 0, 0x00000000 ), # read word  0x00000000
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00000001 ), # read word  0x00000004
    req( 'rd', 0x02, 0x00000008, 0, 0          ), resp('rd', 0x02, 1, 0, 0x00000002 ), # read word  0x00000000
    req( 'rd', 0x03, 0x0000000c, 0, 0          ), resp('rd', 0x03, 1, 0, 0x00000003 ), # read word  0x00000004
    req( 'rd', 0x04, 0x00000010, 0, 0          ), resp('rd', 0x04, 0, 0, 0x00000004 ), # read word  0x00000000
    req( 'rd', 0x05, 0x00000014, 0, 0          ), resp('rd', 0x05, 1, 0, 0x00000005 ), # read word  0x00000004
    req( 'rd', 0x06, 0x00000018, 0, 0          ), resp('rd', 0x06, 1, 0, 0x00000006 ), # read word  0x00000000
    req( 'rd', 0x07, 0x0000001c, 0, 0          ), resp('rd', 0x07, 1, 0, 0x00000007 ), # read word  0x00000004
    req( 'rd', 0x08, 0x00000020, 0, 0          ), resp('rd', 0x08, 0, 0, 0x00000008 ), # read word  0x00000000
    req( 'rd', 0x09, 0x00000024, 0, 0          ), resp('rd', 0x09, 1, 0, 0x00000009 ), # read word  0x00000004
    req( 'rd', 0x10, 0x00000028, 0, 0          ), resp('rd', 0x10, 1, 0, 0x0000000a ), # read word  0x00000000
    req( 'rd', 0x11, 0x0000002c, 0, 0          ), resp('rd', 0x11, 1, 0, 0x0000000b ), # read word  0x00000004
    req( 'rd', 0x12, 0x00000030, 0, 0          ), resp('rd', 0x12, 0, 0, 0x0000000c ), # read word  0x00000000
    req( 'rd', 0x13, 0x00000034, 0, 0          ), resp('rd', 0x13, 1, 0, 0x0000000d ), # read word  0x00000004
    req( 'rd', 0x14, 0x00000038, 0, 0          ), resp('rd', 0x14, 1, 0, 0x0000000e ), # read word  0x00000000
    req( 'rd', 0x15, 0x0000003c, 0, 0          ), resp('rd', 0x15, 1, 0, 0x0000000f ), # read word  0x00000004
    req( 'rd', 0x16, 0x00000040, 0, 0          ), resp('rd', 0x16, 0, 0, 0x00000010 ), # read word  0x00000000
    req( 'rd', 0x17, 0x00000044, 0, 0          ), resp('rd', 0x17, 1, 0, 0x00000011 ), # read word  0x00000004
    req( 'rd', 0x18, 0x00000048, 0, 0          ), resp('rd', 0x18, 1, 0, 0x00000012 ), # read word  0x00000000
    req( 'rd', 0x19, 0x0000004c, 0, 0          ), resp('rd', 0x19, 1, 0, 0x00000013 ), # read word  0x00000004
    req( 'rd', 0x20, 0x00000050, 0, 0          ), resp('rd', 0x20, 0, 0, 0x00000014 ), # read word  0x00000000
    req( 'rd', 0x21, 0x00000054, 0, 0          ), resp('rd', 0x21, 1, 0, 0x00000015 ), # read word  0x00000004
    req( 'rd', 0x22, 0x00000058, 0, 0          ), resp('rd', 0x22, 1, 0, 0x00000016 ), # read word  0x00000000
    req( 'rd', 0x23, 0x0000005c, 0, 0          ), resp('rd', 0x23, 1, 0, 0x00000017 ), # read word  0x00000004
    req( 'rd', 0x24, 0x00000060, 0, 0          ), resp('rd', 0x24, 0, 0, 0x00000018 ), # read word  0x00000000
    req( 'rd', 0x25, 0x00000064, 0, 0          ), resp('rd', 0x25, 1, 0, 0x00000019 ), # read word  0x00000004
    req( 'rd', 0x26, 0x00000068, 0, 0          ), resp('rd', 0x26, 1, 0, 0x0000001a ), # read word  0x00000000
    req( 'rd', 0x27, 0x0000006c, 0, 0          ), resp('rd', 0x27, 1, 0, 0x0000001b ), # read word  0x00000004
    req( 'rd', 0x28, 0x00000070, 0, 0          ), resp('rd', 0x28, 0, 0, 0x0000001c ), # read word  0x00000000
    req( 'rd', 0x29, 0x00000074, 0, 0          ), resp('rd', 0x29, 1, 0, 0x0000001d ), # read word  0x00000004
    req( 'rd', 0x30, 0x00000078, 0, 0          ), resp('rd', 0x30, 1, 0, 0x0000001e ), # read word  0x00000000
    req( 'rd', 0x31, 0x0000007c, 0, 0          ), resp('rd', 0x31, 1, 0, 0x0000001f ), # read word  0x00000004
    req( 'rd', 0x32, 0x00000080, 0, 0          ), resp('rd', 0x32, 0, 0, 0x00000020 ), # read word  0x00000000
    req( 'rd', 0x33, 0x00000084, 0, 0          ), resp('rd', 0x33, 1, 0, 0x00000021 ), # read word  0x00000004
    req( 'rd', 0x34, 0x00000088, 0, 0          ), resp('rd', 0x34, 1, 0, 0x00000022 ), # read word  0x00000000
    req( 'rd', 0x35, 0x0000008c, 0, 0          ), resp('rd', 0x35, 1, 0, 0x00000023 ), # read word  0x00000004
    req( 'rd', 0x36, 0x00000090, 0, 0          ), resp('rd', 0x36, 0, 0, 0x00000024 ), # read word  0x00000000
    req( 'rd', 0x37, 0x00000094, 0, 0          ), resp('rd', 0x37, 1, 0, 0x00000025 ), # read word  0x00000004
    req( 'rd', 0x38, 0x00000098, 0, 0          ), resp('rd', 0x38, 1, 0, 0x00000026 ), # read word  0x00000000
    req( 'rd', 0x39, 0x0000009c, 0, 0          ), resp('rd', 0x39, 1, 0, 0x00000027 ), # read word  0x00000004
    req( 'rd', 0x40, 0x000000a0, 0, 0          ), resp('rd', 0x40, 0, 0, 0x00000028 ), # read word  0x00000000
    req( 'rd', 0x41, 0x000000a4, 0, 0          ), resp('rd', 0x41, 1, 0, 0x00000029 ), # read word  0x00000004
    req( 'rd', 0x42, 0x000000a8, 0, 0          ), resp('rd', 0x42, 1, 0, 0x0000002a ), # read word  0x00000000
    req( 'rd', 0x43, 0x000000ac, 0, 0          ), resp('rd', 0x43, 1, 0, 0x0000002b ), # read word  0x00000004
    req( 'rd', 0x44, 0x000000b0, 0, 0          ), resp('rd', 0x44, 0, 0, 0x0000002c ), # read word  0x00000000
    req( 'rd', 0x45, 0x000000b4, 0, 0          ), resp('rd', 0x45, 1, 0, 0x0000002d ), # read word  0x00000004
    req( 'rd', 0x46, 0x000000b8, 0, 0          ), resp('rd', 0x46, 1, 0, 0x0000002e ), # read word  0x00000000
    req( 'rd', 0x47, 0x000000bc, 0, 0          ), resp('rd', 0x47, 1, 0, 0x0000002f ), # read word  0x00000004
    req( 'rd', 0x48, 0x000000c0, 0, 0          ), resp('rd', 0x48, 0, 0, 0x00000030 ), # read word  0x00000000
    req( 'rd', 0x49, 0x000000c4, 0, 0          ), resp('rd', 0x49, 1, 0, 0x00000031 ), # read word  0x00000004
    req( 'rd', 0x50, 0x000000c8, 0, 0          ), resp('rd', 0x50, 1, 0, 0x00000032 ), # read word  0x00000000
    req( 'rd', 0x51, 0x000000cc, 0, 0          ), resp('rd', 0x51, 1, 0, 0x00000033 ), # read word  0x00000000
    req( 'rd', 0x52, 0x000000d0, 0, 0          ), resp('rd', 0x52, 0, 0, 0x00000034 ), # read word  0x00000000
    req( 'rd', 0x53, 0x000000d4, 0, 0          ), resp('rd', 0x53, 1, 0, 0x00000035 ), # read word  0x00000004
    req( 'rd', 0x54, 0x000000d8, 0, 0          ), resp('rd', 0x54, 1, 0, 0x00000036 ), # read word  0x00000000
    req( 'rd', 0x55, 0x000000dc, 0, 0          ), resp('rd', 0x55, 1, 0, 0x00000037 ), # read word  0x00000004
    req( 'rd', 0x56, 0x000000e0, 0, 0          ), resp('rd', 0x56, 0, 0, 0x00000038 ), # read word  0x00000000
    req( 'rd', 0x57, 0x000000e4, 0, 0          ), resp('rd', 0x57, 1, 0, 0x00000039 ), # read word  0x00000004
    req( 'rd', 0x58, 0x000000e8, 0, 0          ), resp('rd', 0x58, 1, 0, 0x0000003a ), # read word  0x00000000
    req( 'rd', 0x59, 0x000000ec, 0, 0          ), resp('rd', 0x59, 1, 0, 0x0000003b ), # read word  0x00000004
    req( 'rd', 0x60, 0x000000f0, 0, 0          ), resp('rd', 0x60, 0, 0, 0x0000003c ), # read word  0x00000000
    req( 'rd', 0x61, 0x000000f4, 0, 0          ), resp('rd', 0x61, 1, 0, 0x0000003d ), # read word  0x00000004
    req( 'rd', 0x62, 0x000000f8, 0, 0          ), resp('rd', 0x62, 1, 0, 0x0000003e ), # read word  0x00000000
    req( 'rd', 0x63, 0x000000fc, 0, 0          ), resp('rd', 0x63, 1, 0, 0x0000003f ), # read word  0x00000004

    req( 'rd', 0x64, 0x00000004, 0, 0          ), resp('rd', 0x64, 1, 0, 0x00000001 ), # read word  0x00000000
  ]

# Data to be loaded into memory before running the test

def entire_cache_read_mem( base_addr ):
  return [
    # addr      data (in int)
    0x00000000, 0x00000000,
    0x00000004, 0x00000001,
    0x00000008, 0x00000002,
    0x0000000c, 0x00000003,
    0x00000010, 0x00000004,
    0x00000014, 0x00000005,
    0x00000018, 0x00000006,
    0x0000001c, 0x00000007,
    0x00000020, 0x00000008,
    0x00000024, 0x00000009,
    0x00000028, 0x0000000a,
    0x0000002c, 0x0000000b,
    0x00000030, 0x0000000c,
    0x00000034, 0x0000000d,
    0x00000038, 0x0000000e,
    0x0000003c, 0x0000000f,
    0x00000040, 0x00000010,
    0x00000044, 0x00000011,
    0x00000048, 0x00000012,
    0x0000004c, 0x00000013,
    0x00000050, 0x00000014,
    0x00000054, 0x00000015,
    0x00000058, 0x00000016,
    0x0000005c, 0x00000017,
    0x00000060, 0x00000018,
    0x00000064, 0x00000019,
    0x00000068, 0x0000001a,
    0x0000006c, 0x0000001b,
    0x00000070, 0x0000001c,
    0x00000074, 0x0000001d,
    0x00000078, 0x0000001e,
    0x0000007c, 0x0000001f,
    0x00000080, 0x00000020,
    0x00000084, 0x00000021,
    0x00000088, 0x00000022,
    0x0000008c, 0x00000023,
    0x00000090, 0x00000024,
    0x00000094, 0x00000025,
    0x00000098, 0x00000026,
    0x0000009c, 0x00000027,
    0x000000a0, 0x00000028,
    0x000000a4, 0x00000029,
    0x000000a8, 0x0000002a,
    0x000000ac, 0x0000002b,
    0x000000b0, 0x0000002c,
    0x000000b4, 0x0000002d,
    0x000000b8, 0x0000002e,
    0x000000bc, 0x0000002f,
    0x000000c0, 0x00000030,
    0x000000c4, 0x00000031,
    0x000000c8, 0x00000032,
    0x000000cc, 0x00000033,
    0x000000d0, 0x00000034,
    0x000000d4, 0x00000035,
    0x000000d8, 0x00000036,
    0x000000dc, 0x00000037,
    0x000000e0, 0x00000038,
    0x000000e4, 0x00000039,
    0x000000e8, 0x0000003a,
    0x000000ec, 0x0000003b,
    0x000000f0, 0x0000003c,
    0x000000f4, 0x0000003d,
    0x000000f8, 0x0000003e,
    0x000000fc, 0x0000003f,
  ]

#-------------------------------------------------------------------------
# Test Case: conflict misses that should pass in alternative design and fail in baseline design
#-------------------------------------------------------------------------

def conflict_misses_msg( base_addr ):
  return [
    #    type  opq   addr      len  data               type  opq test  len data
    req( 'rd', 0x00, 0x00000000, 0, 0          ), resp('rd', 0x00, 0,   0, 0xdeadbeef ), # read word  0x00000000   bring back first cache line
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1,   0, 0x00c0ffee ), # read word  0x00000004   hit because this word is brought back already
    # same offset & index but different tag
    req( 'rd', 0x02, 0x00000100, 0, 0          ), resp('rd', 0x02, 0,   0, 0xa5a5a5a5 ), # read word  0x00000100   compulsory miss, and replaces the cache line just brought back from memory
    # reread the first word but it's replaced from cache
    req( 'rd', 0x03, 0x00000000, 0, 0          ), resp('rd', 0x03, 0,   0, 0xdeadbeef ), # read word  0x00000000   conflict miss
  ]

# Data to be loaded into memory before running the test

def conflict_misses_mem( base_addr ):
  return [
    # addr      data (in int)
    0x00000000, 0xdeadbeef,
    0x00000004, 0x00c0ffee,
    0x00000100, 0xa5a5a5a5,
    0x00000104, 0xf1f1f1f1,
  ]

#-------------------------------------------------------------------------
# Test Case: capacity misses -- should happen in both designs
#-------------------------------------------------------------------------

def capacity_misses_msg( base_addr ):
  return [
    # Fill up all the cache lines first
    #    type  opq   addr      len  data               type  opq test  len data
    req( 'rd', 0x00, 0x00000000, 0, 0          ), resp('rd', 0x00, 0, 0, 0x00000000 ), # read word  0x00000000
    req( 'rd', 0x04, 0x00000010, 0, 0          ), resp('rd', 0x04, 0, 0, 0x00000004 ), # read word  0x00000010
    req( 'rd', 0x08, 0x00000020, 0, 0          ), resp('rd', 0x08, 0, 0, 0x00000008 ), # read word  0x00000020
    req( 'rd', 0x12, 0x00000030, 0, 0          ), resp('rd', 0x12, 0, 0, 0x0000000c ), # read word  0x00000030
    req( 'rd', 0x16, 0x00000040, 0, 0          ), resp('rd', 0x16, 0, 0, 0x00000010 ), # read word  0x00000040
    req( 'rd', 0x20, 0x00000050, 0, 0          ), resp('rd', 0x20, 0, 0, 0x00000014 ), # read word  0x00000050
    req( 'rd', 0x24, 0x00000060, 0, 0          ), resp('rd', 0x24, 0, 0, 0x00000018 ), # read word  0x00000060
    req( 'rd', 0x28, 0x00000070, 0, 0          ), resp('rd', 0x28, 0, 0, 0x0000001c ), # read word  0x00000070
    req( 'rd', 0x32, 0x00000080, 0, 0          ), resp('rd', 0x32, 0, 0, 0x00000020 ), # read word  0x00000080
    req( 'rd', 0x36, 0x00000090, 0, 0          ), resp('rd', 0x36, 0, 0, 0x00000024 ), # read word  0x00000090
    req( 'rd', 0x40, 0x000000a0, 0, 0          ), resp('rd', 0x40, 0, 0, 0x00000028 ), # read word  0x000000a0
    req( 'rd', 0x44, 0x000000b0, 0, 0          ), resp('rd', 0x44, 0, 0, 0x0000002c ), # read word  0x000000b0
    req( 'rd', 0x48, 0x000000c0, 0, 0          ), resp('rd', 0x48, 0, 0, 0x00000030 ), # read word  0x000000c0
    req( 'rd', 0x52, 0x000000d0, 0, 0          ), resp('rd', 0x52, 0, 0, 0x00000034 ), # read word  0x000000d0
    req( 'rd', 0x56, 0x000000e0, 0, 0          ), resp('rd', 0x56, 0, 0, 0x00000038 ), # read word  0x000000e0
    req( 'rd', 0x60, 0x000000f0, 0, 0          ), resp('rd', 0x60, 0, 0, 0x0000003c ), # read word  0x000000f0

    # Read with a tag that never showed up before -- leads to a capacity miss
    req( 'rd', 0x00, 0x00000100, 0, 0          ), resp('rd', 0x00, 0, 0, 0xefefefef ), # read word  0x00000100

  ]

# Data to be loaded into memory before running the test

def capacity_misses_mem( base_addr ):
  return [
    # addr      data (in int)
    0x00000000, 0x00000000,
    0x00000010, 0x00000004,
    0x00000020, 0x00000008,
    0x00000030, 0x0000000c,
    0x00000040, 0x00000010,
    0x00000050, 0x00000014,
    0x00000060, 0x00000018,
    0x00000070, 0x0000001c,
    0x00000080, 0x00000020,
    0x00000090, 0x00000024,
    0x000000a0, 0x00000028,
    0x000000b0, 0x0000002c,
    0x000000c0, 0x00000030,
    0x000000d0, 0x00000034,
    0x000000e0, 0x00000038,
    0x000000f0, 0x0000003c,

    # Data for capacity miss
    0x00000100, 0xefefefef,
  ]

#-------------------------------------------------------------------------
# Test Case: LRU replacement policy by filling up a way
#-------------------------------------------------------------------------

def LRU_msg( base_addr ):
  return [
    #    type  opq   addr      len  data               type  opq test  len data

    # same offset & index but different tag -- filling up the two ways
    req( 'rd', 0x00, 0x00000000, 0, 0          ), resp('rd', 0x00, 0,   0, 0xaaaaaaaa ),
    req( 'rd', 0x01, 0x00000080, 0, 0          ), resp('rd', 0x01, 0,   0, 0xeeeeeeee ),
    # check out whether the first way is filled up -- this read should hit
    # in the meanwhile, Way 0 becomes the Most Recently Used cache line
    req( 'rd', 0x02, 0x00000004, 0, 0          ), resp('rd', 0x02, 1,   0, 0xbbbbbbbb ),
    # read a new tag to trigger a replacement -- Way 1 (holding tag 0b0) should be replaced
    req( 'rd', 0x03, 0x00000108, 0, 0          ), resp('rd', 0x03, 0,   0, 0xffffffff ),
    # check whether Way 0 (holding tag 0b0) is replaced -- this read should hit
    req( 'rd', 0x04, 0x0000000c, 0, 0          ), resp('rd', 0x04, 1,   0, 0xdddddddd ),
  ]

# Data to be loaded into memory before running the test

def LRU_mem( base_addr ):
  return [
    # addr      data (in int)
    0x00000000, 0xaaaaaaaa,
    0x00000004, 0xbbbbbbbb,
    0x00000008, 0xcccccccc,
    0x0000000c, 0xdddddddd,

    0x00000080, 0xeeeeeeee,

    0x00000108, 0xffffffff,
  ]

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# LAB TASK: Add more test cases
#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

#----------------------------------------------------------------------
# Banked cache test
#----------------------------------------------------------------------
# The test field in the response message: 0 == MISS, 1 == HIT

# This test case is to test if the bank offset is implemented correctly.
#
# The idea behind this test case is to differentiate between a cache
# with no bank bits and a design has one/two bank bits by looking at cache
# request hit/miss status.

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# LAB TASK:
#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# [31    tag 		8|7   idx    4| 3 offset 0]
# [31 tag  10|9 idx 6|5 bank 4| 3 offset 0]
# 0x00000080 -- 1 in 7th bit 
#	--> in original:	idx = 1000 --> 8th  idx
#	--> in banked:		idx = 0010 --> 2nd  idx and bank = 00 --> 0th bank
# 0x00000280 -- 1 in 9th and 7th bits
#	--> in original:	idx = 1000 --> 8th  idx
#	--> in banked:		idx = 1010 --> 10th idx and bank = 00 --> 0th bank
# 0x000003F0 -- 1 in [9:4]
#	--> in original:	idx = 1111 --> 15th idx
#	--> in banked:		idx = 1111 --> 15th idx and bank = 11 --> 3rd bank
# 0x000003E0 -- 1 in [9:5]
#	--> in original:	idx = 1110 --> 14th idx
#	--> in banked:		idx = 1111 --> 15th idx and bank = 10 --> 2nd bank

def NoBank_4WM_2RM_2RH_dmap( base_addr ):
	return[
	#    type  opq  addr       len data                type  opq  test len data
  # same index, tag changes, cache line is replaced
	req( 'wr', 0x0, 0x00000080, 0, 0xdeadbeef ), resp( 'wr', 0x0, 0,   0,  0          ),
  req( 'wr', 0x1, 0x00000280, 0, 0x00c0ffee ), resp( 'wr', 0x1, 0,   0,  0          ),
  # differen index, cache line remains
	req( 'wr', 0x2, 0x000003F0, 0, 0x0a0b0c0d ), resp( 'wr', 0x2, 0,   0,  0          ),
	req( 'wr', 0x3, 0x000003E0, 0, 0x09876543 ), resp( 'wr', 0x3, 0,   0,  0          ),

  req( 'rd', 0x4, 0x00000080, 0, 0          ), resp( 'rd', 0x4, 0,   0,  0xdeadbeef ),
  req( 'rd', 0x5, 0x00000280, 0, 0          ), resp( 'rd', 0x5, 0,   0,  0x00c0ffee ),
  req( 'rd', 0x6, 0x000003F0, 0, 0          ), resp( 'rd', 0x6, 1,   0,  0x0a0b0c0d ),
	req( 'rd', 0x7, 0x000003E0, 0, 0          ), resp( 'rd', 0x7, 1,   0,  0x09876543 ),
	]

def W4Bank_4WM_4RM_dmap( base_addr ):
	return[
	#    type  opq  addr       len data                type  opq  test len data
  # same bank, different index, cache line remains
	req( 'wr', 0x0, 0x00000080, 0, 0xdeadbeef ), resp( 'wr', 0x0, 0,   0,  0          ),
  req( 'wr', 0x1, 0x00000280, 0, 0x00c0ffee ), resp( 'wr', 0x1, 0,   0,  0          ),
	# different bank, same index
  req( 'wr', 0x2, 0x000003F0, 0, 0x0a0b0c0d ), resp( 'wr', 0x2, 0,   0,  0          ),
	req( 'wr', 0x3, 0x000003E0, 0, 0x09876543 ), resp( 'wr', 0x3, 0,   0,  0          ),
	
	req( 'rd', 0x4, 0x00000080, 0, 0          ), resp( 'rd', 0x4, 1,   0,  0xdeadbeef ),
	req( 'rd', 0x5, 0x00000280, 0, 0          ), resp( 'rd', 0x5, 1,   0,  0x00c0ffee ),
	req( 'rd', 0x6, 0x000003F0, 0, 0          ), resp( 'rd', 0x6, 0,   0,  0x0a0b0c0d ),
	req( 'rd', 0x7, 0x000003E0, 0, 0          ), resp( 'rd', 0x7, 0,   0,  0x09876543 ),
  ]


#-------------------------------------------------------------------------
# Test table for generic test
#-------------------------------------------------------------------------

test_case_table_generic = mk_test_case_table([
  (                         "msg_func               mem_data_func         nbank stall lat src sink"),
  [ "read_hit_1word_clean",  read_hit_1word_clean,  None,                 0,    0.0,  0,  0,  0    ],
  [ "write_hit_1word_clean", write_hit_1word_clean, None,                 0,    0.0,  0,  0,  0    ],
  [ "write_hit_2word_clean", write_hit_2word_clean, None,                 0,    0.0,  0,  0,  0    ],
  [ "read_hit_1word_dirty",  read_hit_1word_dirty,  None,                 0,    0.0,  0,  0,  0    ],
  [ "write_hit_1word_dirty", write_hit_1word_dirty, None,                 0,    0.0,  0,  0,  0    ],
  [ "read_miss_1word",       read_miss_1word_msg,   read_miss_1word_mem,  0,    0.0,  0,  0,  0    ],
  [ "write_miss_1word",      write_miss_1word_msg,  write_miss_1word_mem, 0,    0.0,  0,  0,  0    ],
  [ "read_miss_evict",       read_miss_evict_msg,   read_miss_evict_mem,  0,    0.0,  0,  0,  0    ],
  [ "write_miss_evict",      write_miss_evict_msg,  write_miss_evict_mem, 0,    0.0,  0,  0,  0    ],
  [ "entire_cache_read",     entire_cache_read_msg, entire_cache_read_mem,0,    0.0,  0,  0,  0    ],
  [ "conflict_misses",       conflict_misses_msg,   conflict_misses_mem,  0,    0.0,  0,  0,  0    ],
  [ "capacity_misses",       capacity_misses_msg,   capacity_misses_mem,  0,    0.0,  0,  0,  0    ],
  [ "read_hit_1word_4bank",  read_hit_1word_clean,  None,                 4,    0.0,  0,  0,  0    ],

  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # LAB TASK: Add test cases to this table
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

])

@pytest.mark.parametrize( **test_case_table_generic )
def test_generic( test_params, dump_vcd ):
  msgs = test_params.msg_func( 0 )
  if test_params.mem_data_func != None:
    mem = test_params.mem_data_func( 0 )
  # Instantiate testharness
  harness = TestHarness( msgs[::2], msgs[1::2],
                         test_params.stall, test_params.lat,
                         test_params.src, test_params.sink,
                         BlockingCacheFL, test_params.nbank,
                         False, dump_vcd )
  # Load memory before the test
  if test_params.mem_data_func != None:
    harness.load( mem[::2], mem[1::2] )
  # Run the test
  run_sim( harness, dump_vcd )

#-------------------------------------------------------------------------
# Test table for generic test with delays
#-------------------------------------------------------------------------

test_case_table_generic_with_delays = mk_test_case_table([
  (                         "msg_func               mem_data_func         nbank stall            lat                   src                   sink                "),
  [ "read_hit_1word_clean",  read_hit_1word_clean,  None,                 0,    random.random(), random.randint(0,10), random.randint(0,10), random.randint(0,10) ],
  [ "write_hit_1word_clean", write_hit_1word_clean, None,                 0,    random.random(), random.randint(0,10), random.randint(0,10), random.randint(0,10) ],
  [ "write_hit_2word_clean", write_hit_2word_clean, None,                 0,    random.random(), random.randint(0,10), random.randint(0,10), random.randint(0,10) ],
  [ "read_hit_1word_dirty",  read_hit_1word_dirty,  None,                 0,    random.random(), random.randint(0,10), random.randint(0,10), random.randint(0,10) ],
  [ "write_hit_1word_dirty", write_hit_1word_dirty, None,                 0,    random.random(), random.randint(0,10), random.randint(0,10), random.randint(0,10) ],
  [ "read_miss_1word",       read_miss_1word_msg,   read_miss_1word_mem,  0,    random.random(), random.randint(0,10), random.randint(0,10), random.randint(0,10) ],
  [ "write_miss_1word",      write_miss_1word_msg,  write_miss_1word_mem, 0,    random.random(), random.randint(0,10), random.randint(0,10), random.randint(0,10) ],
  [ "read_miss_evict",       read_miss_evict_msg,   read_miss_evict_mem,  0,    random.random(), random.randint(0,10), random.randint(0,10), random.randint(0,10) ],
  [ "write_miss_evict",      write_miss_evict_msg,  write_miss_evict_mem, 0,    random.random(), random.randint(0,10), random.randint(0,10), random.randint(0,10) ],
  [ "entire_cache_read",     entire_cache_read_msg, entire_cache_read_mem,0,    random.random(), random.randint(0,10), random.randint(0,10), random.randint(0,10) ],
  [ "conflict_misses",       conflict_misses_msg,   conflict_misses_mem,  0,    random.random(), random.randint(0,10), random.randint(0,10), random.randint(0,10) ],
  [ "capacity_misses",       capacity_misses_msg,   capacity_misses_mem,  0,    random.random(), random.randint(0,10), random.randint(0,10), random.randint(0,10) ],
  [ "read_hit_1word_4bank",  read_hit_1word_clean,  None,                 4,    random.random(), random.randint(0,10), random.randint(0,10), random.randint(0,10) ],

  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # LAB TASK: Add test cases to this table
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

])

@pytest.mark.parametrize( **test_case_table_generic_with_delays )
def test_generic_with_delays( test_params, dump_vcd ):
  msgs = test_params.msg_func( 0 )
  if test_params.mem_data_func != None:
    mem = test_params.mem_data_func( 0 )
  # Instantiate testharness
  harness = TestHarness( msgs[::2], msgs[1::2],
                         test_params.stall, test_params.lat,
                         test_params.src, test_params.sink,
                         BlockingCacheFL, test_params.nbank,
                         False, dump_vcd )
  # Load memory before the test
  if test_params.mem_data_func != None:
    harness.load( mem[::2], mem[1::2] )
  # Run the test
  run_sim( harness, dump_vcd )

#-------------------------------------------------------------------------
# Random tests
#-------------------------------------------------------------------------
# 1.Simple address patterns, single request type, with random data
# 2.Simple address patterns, random request type and data
# 3.Random address patterns, request types, and data
# 4.Unit stride with random data
# 5.Stride with random data
# 6.Unit stride (high spatial locality) mixed with shared (high temporal locality)

def mk_req( type_, addr, len_, data ):
  # print('\n'+'req( '+type_+', 0, '+str(addr)+', '+str(len_)+', '+str(data)+' )')
  #           type    opq addr  len   data
  return req( type_,  0,  addr, len_, data )

def mk_resp( type_, len_, data ):
  # print('\n'+'resq( '+type_+', 0, 0, '+str(len_)+', '+str(data)+' )')
  #            type   opq test  len   data
  return resp( type_, 0,  0,    len_, data )

#-------------------------------------------------------------------
# 1.Simple address patterns, single request type, with random data
#-------------------------------------------------------------------
class random_tests_1():
  def __init__(self, req_type):
    self.rand_msg  = []
    self.mem_data  = []
    addr_1 = 0
    Num_of_Rand_Tests_1 = 100
    for i in xrange( Num_of_Rand_Tests_1 ):
      addr_1 = i*16
      data_1 = random.randint(0,2147483647)
      if ( req_type is 'rd' ):
        self.rand_msg.append( mk_req ( 'rd', addr_1, 0, 0      ) )
        self.rand_msg.append( mk_resp( 'rd', 0,      data_1    ) )
      elif ( req_type is 'wr' ):
        self.rand_msg.append( mk_req ( 'wr', addr_1, 0, data_1 ) )
        self.rand_msg.append( mk_resp( 'wr', 0,      0         ) )
      self.mem_data.append( addr_1 )
      self.mem_data.append( data_1 )

  def rand_1_msg(self, base_addr):
    return self.rand_msg

  def rand_1_mem(self, base_addr):
    return self.mem_data
  
random_1_rd = random_tests_1('rd')
random_1_wr = random_tests_1('wr')

# print('\n\nHello\n\n')
# print(random_1_rd.rand_1_msg())
# print(random_1_rd.rand_1_mem())
# print(random_1_wr.rand_1_msg())
# print(random_1_wr.rand_1_mem())
# print('\n\nHello\n\n')

#-------------------------------------------------------------------
# 2.Simple address patterns, random request type and data
#-------------------------------------------------------------------
class random_tests_2():
  def __init__(self):
    self.rand_msg  = []
    self.mem_data  = []
    addr_2 = 0
    Num_of_Rand_Tests_2 = 10
    for i in xrange( Num_of_Rand_Tests_2 ):
      addr_2 = i*8
      data_2 = random.randint(0,2147483647)
      if ( random.randint(0,1) is 1 ):
        self.rand_msg.append( mk_req ( 'rd', addr_2, 0, 0      ) )
        self.rand_msg.append( mk_resp( 'rd', 0,      data_2    ) )
      else:
        self.rand_msg.append( mk_req ( 'wr', addr_2, 0, data_2 ) )
        self.rand_msg.append( mk_resp( 'wr', 0,      0         ) )
      self.mem_data.append( addr_2 )
      self.mem_data.append( data_2 )

  def rand_2_msg(self, base_addr):
    return self.rand_msg

  def rand_2_mem(self, base_addr):
    return self.mem_data
  
random_2 = random_tests_2()

#-------------------------------------------------------------------------
# Test table for random test
#-------------------------------------------------------------------------

test_case_table_random = mk_test_case_table([
  (                         "msg_func                   mem_data_func               nbank stall lat src sink"),
  [ "random_test_1_read",    random_1_rd.rand_1_msg,    random_1_rd.rand_1_mem,     0,    0.0,  0,  0,  0    ],
  [ "random_test_1_write",   random_1_wr.rand_1_msg,    random_1_wr.rand_1_mem,     0,    0.0,  0,  0,  0    ],
  [ "random_test_2",         random_2.rand_2_msg,       random_2.rand_2_mem,        0,    0.0,  0,  0,  0    ],
])

@pytest.mark.parametrize( **test_case_table_random )
def test_random( test_params, dump_vcd ):
  msgs = test_params.msg_func( 0 )
  if test_params.mem_data_func != None:
    mem = test_params.mem_data_func( 0 )
  # Instantiate testharness
  harness = TestHarness( msgs[::2], msgs[1::2],
                         test_params.stall, test_params.lat,
                         test_params.src, test_params.sink,
                         BlockingCacheFL, test_params.nbank,
                         False, dump_vcd )
  # Load memory before the test
  if test_params.mem_data_func != None:
    harness.load( mem[::2], mem[1::2] )
  # Run the test
  run_sim( harness, dump_vcd )

#-------------------------------------------------------------------------
# Test table for set-associative cache (alternative design)
#-------------------------------------------------------------------------

test_case_table_set_assoc = mk_test_case_table([
  (                             "msg_func        mem_data_func    nbank stall lat src sink"),
  [ "read_hit_asso",             read_hit_asso,  None,            0,    0.0,  0,  0,  0    ],
  [ "LRU",                       LRU_msg,        LRU_mem,         0,    0.0,  0,  0,  0    ],

  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # LAB TASK: Add test cases to this table
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

])

@pytest.mark.parametrize( **test_case_table_set_assoc )
def test_set_assoc( test_params, dump_vcd ):
  msgs = test_params.msg_func( 0 )
  if test_params.mem_data_func != None:
    mem  = test_params.mem_data_func( 0 )
  # Instantiate testharness
  harness = TestHarness( msgs[::2], msgs[1::2],
                         test_params.stall, test_params.lat,
                         test_params.src, test_params.sink,
                         BlockingCacheFL, test_params.nbank,
                         False, dump_vcd )
  # Load memory before the test
  if test_params.mem_data_func != None:
    harness.load( mem[::2], mem[1::2] )
  # Run the test
  run_sim( harness, dump_vcd )


#-------------------------------------------------------------------------
# Test table for direct-mapped cache (baseline design)
#-------------------------------------------------------------------------

test_case_table_dir_mapped = mk_test_case_table([
  (                                  "msg_func                 mem_data_func          nbank stall lat src sink"),
  [ "read_hit_dmap",                  read_hit_dmap,           None,                  0,    0.0,  0,  0,  0    ],
  [ "NoBank_4WM_2RM_2RH_dmap",        NoBank_4WM_2RM_2RH_dmap, None,                  0,    0.0,  0,  0,  0    ],
  [ "W4Bank_4WM_4RM_dmap",            W4Bank_4WM_4RM_dmap,     None,                  4,    0.0,  0,  0,  0    ],

  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # LAB TASK: Add test cases to this table
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

])

@pytest.mark.parametrize( **test_case_table_dir_mapped )
def test_dir_mapped( test_params, dump_vcd ):
  msgs = test_params.msg_func( 0 )
  if test_params.mem_data_func != None:
    mem  = test_params.mem_data_func( 0 )
  # Instantiate testharness
  harness = TestHarness( msgs[::2], msgs[1::2],
                         test_params.stall, test_params.lat,
                         test_params.src, test_params.sink,
                         BlockingCacheFL, test_params.nbank,
                         False, dump_vcd )
  # Load memory before the test
  if test_params.mem_data_func != None:
    harness.load( mem[::2], mem[1::2] )
  # Run the test
  run_sim( harness, dump_vcd )
