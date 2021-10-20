#=========================================================================
# IntMulFL_test
#=========================================================================

import pytest
import random

random.seed(0xdeadbeef)

from pymtl      import *
from pclib.test import mk_test_case_table, run_sim
from pclib.test import TestSource, TestSink

from lab1_imul.IntMulFL   import IntMulFL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, imul, src_msgs, sink_msgs,
                src_delay, sink_delay,
                dump_vcd=False, test_verilog=False ):

    # Instantiate models

    s.src  = TestSource ( Bits(64), src_msgs,  src_delay  )
    s.imul = imul
    s.sink = TestSink   ( Bits(32), sink_msgs, sink_delay )

    # Dump VCD

    if dump_vcd:
      s.imul.vcd_file = dump_vcd

    # Translation

    if test_verilog:
      s.imul = TranslationTool( s.imul )

    # Connect

    s.connect( s.src.out,  s.imul.req  )
    s.connect( s.imul.resp, s.sink.in_ )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace()  + " > " + \
           s.imul.line_trace()  + " > " + \
           s.sink.line_trace()

#-------------------------------------------------------------------------
# mk_req_msg
#-------------------------------------------------------------------------

def req( a, b ):
  msg = Bits( 64 )
  msg[32:64] = Bits( 32, a, trunc=True )
  msg[ 0:32] = Bits( 32, b, trunc=True )
  return msg

def resp( a ):
  return Bits( 32, a, trunc=True )

toy_test_msgs = [
 req(           2  ,           3  ), resp(                       6  )
]
#----------------------------------------------------------------------
# Test Case: small positive * positive
#----------------------------------------------------------------------

small_small_msgs = [
 req(         -28  ,         -71  ), resp(                    1988  ),
 req(         -12  ,         -91  ), resp(                    1092  ),
 req(          15  ,          34  ), resp(                     510  ),
 req(         -48  ,         -34  ), resp(                    1632  ),
 req(         -17  ,         -90  ), resp(                    1530  ),
 req(         -11  ,          41  ), resp(                    -451  ),
 req(          31  ,         100  ), resp(                    3100  ),
 req(         -22  ,          91  ), resp(                   -2002  ),
 req(         -48  ,          25  ), resp(                   -1200  ),
 req(          62  ,          57  ), resp(                    3534  ),
 req(           0  ,           0  ), resp(                       0  ),
 req(          -1  ,          -1  ), resp(                       1  ),
 req(           1  ,          -1  ), resp(                      -1  ),
 req(           0  ,           0  ), resp(                       0  ),
 req(           0  ,          -1  ), resp(                       0  ),
]


small_large_msgs = [
 req(          86  ,      -28009  ), resp(                -2408774  ),
 req(          28  ,      -12586  ), resp(                 -352408  ),
 req(         -41  ,       -6739  ), resp(                  276299  ),
 req(         -86  ,       19777  ), resp(                -1700822  ),
 req(          33  ,      -24816  ), resp(                 -818928  ),
 req(         -11  ,      -12723  ), resp(                  139953  ),
 req(         -28  ,        8579  ), resp(                 -240212  ),
 req(         -63  ,       19917  ), resp(                -1254771  ),
 req(         -50  ,       23469  ), resp(                -1173450  ),
 req(           7  ,      -17393  ), resp(                 -121751  ),
]


small_edge_msgs = [
 req(          91  , -2147483585  ), resp(           -195421006235  ),
 req(          57  , -2147483627  ), resp(           -122406566739  ),
 req(         -51  , -2147483642  ), resp(            109521665742  ),
 req(          31  , -2147483563  ), resp(            -66571990453  ),
 req(          20  ,  2147483598  ), resp(             42949671960  ),
 req(          64  ,  2147483606  ), resp(            137438950784  ),
 req(         -54  , -2147483558  ), resp(            115964112132  ),
 req(         -53  , -2147483581  ), resp(            113816629793  ),
 req(          13  ,  2147483619  ), resp(             27917287047  ),
 req(         -64  , -2147483601  ), resp(            137438950464  ),
 req(          -1  ,  2147483648  ), resp(             -2147483648  ),
]


small_random_msgs = [
 req(          -5  ,  1909113235  ), resp(             -9545566175  ),
 req(          21  ,  1795452512  ), resp(             37704502752  ),
 req(         -58  , -1137668036  ), resp(             65984746088  ),
 req(         -81  ,  -962130256  ), resp(             77932550736  ),
 req(          32  ,   388356542  ), resp(             12427409344  ),
 req(          -3  ,   218925220  ), resp(              -656775660  ),
 req(          76  , -2080231969  ), resp(           -158097629644  ),
 req(         -47  , -1494471533  ), resp(             70240162051  ),
 req(           8  , -1987225917  ), resp(            -15897807336  ),
 req(           2  ,   773856556  ), resp(              1547713112  ),
]


large_small_msgs = [
 req(      -32000  ,          16  ), resp(                 -512000  ),
 req(       -8509  ,         -72  ), resp(                  612648  ),
 req(      -18407  ,         -49  ), resp(                  901943  ),
 req(      -27869  ,          80  ), resp(                -2229520  ),
 req(      -10570  ,          60  ), resp(                 -634200  ),
 req(       -1554  ,         -94  ), resp(                  146076  ),
 req(        9641  ,         -32  ), resp(                 -308512  ),
 req(      -26524  ,          43  ), resp(                -1140532  ),
 req(      -26833  ,         -86  ), resp(                 2307638  ),
 req(      -13434  ,           6  ), resp(                  -80604  ),
]


large_large_msgs = [
 req(       -3010  ,       -2250  ), resp(                 6772500  ),
 req(       13423  ,      -20799  ), resp(              -279184977  ),
 req(       -7238  ,       14645  ), resp(              -106000510  ),
 req(      -16527  ,       14285  ), resp(              -236088195  ),
 req(       26785  ,        5035  ), resp(               134862475  ),
 req(       -1100  ,       10108  ), resp(               -11118800  ),
 req(      -18859  ,        9165  ), resp(              -172842735  ),
 req(      -19094  ,        2583  ), resp(               -49319802  ),
 req(       21673  ,      -27792  ), resp(              -602336016  ),
 req(      -22044  ,      -23107  ), resp(               509370708  ),
]


large_edge_msgs = [
 req(      -26813  , -2147483614  ), resp(          57580478142182  ),
 req(        4052  , -2147483634  ), resp(          -8701603684968  ),
 req(       17440  ,  2147483647  ), resp(          37452114803680  ),
 req(        3307  ,  2147483574  ), resp(           7101728179218  ),
 req(      -27405  , -2147483602  ), resp(          58851788112810  ),
 req(       23287  , -2147483562  ), resp(         -50008449708294  ),
 req(       12400  , -2147483575  ), resp(         -26628796330000  ),
 req(        6054  ,  2147483583  ), resp(          13000865611482  ),
 req(      -14037  ,  2147483646  ), resp(         -30144227938902  ),
 req(       22628  , -2147483631  ), resp(         -48593259602268  ),
]


large_random_msgs = [
 req(       31988  ,   -12575487  ), resp(           -402264678156  ),
 req(       31659  ,  1897694518  ), resp(          60079110745362  ),
 req(      -15422  , -1255908597  ), resp(          19368622382934  ),
 req(       10309  , -1239350252  ), resp(         -12776461747868  ),
 req(        9282  ,  -920079719  ), resp(          -8540179951758  ),
 req(       17668  , -1973814577  ), resp(         -34873355946436  ),
 req(      -21867  ,  1924562069  ), resp(         -42084398762823  ),
 req(       15670  ,  -779297676  ), resp(         -12211594582920  ),
 req(       20788  ,  1349239114  ), resp(          28047982701832  ),
 req(        3366  ,  1908914082  ), resp(           6425404800012  ),
]


edge_small_msgs = [
 req( -2147483588  ,         -16  ), resp(             34359737408  ),
 req(  2147483633  ,         -85  ), resp(           -182536108805  ),
 req(  2147483600  ,          47  ), resp(            100931729200  ),
 req( -2147483648  ,          69  ), resp(           -148176371712  ),
 req( -2147483564  ,         -89  ), resp(            191126037196  ),
 req(  2147483598  ,         -88  ), resp(           -188978556624  ),
 req(  2147483634  ,         -19  ), resp(            -40802189046  ),
 req(  2147483615  ,           5  ), resp(             10737418075  ),
 req( -2147483587  ,         -99  ), resp(            212600875113  ),
 req( -2147483568  ,         -77  ), resp(            165356234736  ),
]


edge_large_msgs = [
 req( -2147483589  ,      -15574  ), resp(          33444909415086  ),
 req( -2147483638  ,       28864  ), resp(         -61984967727232  ),
 req( -2147483568  ,      -32338  ), resp(          69445323621984  ),
 req( -2147483555  ,        4109  ), resp(          -8824009927495  ),
 req(  2147483630  ,       -6447  ), resp(         -13844826962610  ),
 req(  2147483626  ,      -13986  ), resp(         -30034705993236  ),
 req( -2147483612  ,       21230  ), resp(         -45591077082760  ),
 req( -2147483580  ,      -11732  ), resp(          25194277360560  ),
 req( -2147483638  ,       -9701  ), resp(          20832738772238  ),
 req(  2147483572  ,       10617  ), resp(          22799833083924  ),
]


edge_edge_msgs = [
 req( -2147483558  ,  2147483624  ), resp(    -4611685773614254192  ),
 req( -2147483621  , -2147483620  ), resp(     4611685900315788020  ),
 req( -2147483591  ,  2147483630  ), resp(    -4611685857366115330  ),
 req(  2147483563  , -2147483570  ), resp(    -4611685668387559910  ),
 req( -2147483593  , -2147483617  ), resp(     4611685833743795881  ),
 req(  2147483623  , -2147483584  ), resp(    -4611685827301344832  ),
 req( -2147483643  , -2147483626  ), resp(     4611685960445329518  ),
 req(  2147483566  ,  2147483635  ), resp(     4611685814416442410  ),
 req( -2147483564  , -2147483622  ), resp(     4611685782204188808  ),
 req( -2147483561  ,  2147483619  ), resp(    -4611685769319287259  ),
]


edge_random_msgs = [
 req(  2147483586  , -1617431410  ), resp(    -3473407404455836260  ),
 req( -2147483557  , -1351687685  ), resp(     2902727077736895545  ),
 req(  2147483639  ,   -29340705  ), resp(      -63008683944225495  ),
 req( -2147483643  , -1034139559  ), resp(     2220797787531733437  ),
 req( -2147483631  , -1869303867  ), resp(     4014299455747501077  ),
 req( -2147483615  ,  -482458810  ), resp(     1036072389387398150  ),
 req(  2147483600  , -2040148742  ), resp(    -4381185965005631200  ),
 req( -2147483549  ,   109879429  ), resp(     -235964266151013521  ),
 req(  2147483580  ,     -668469  ), resp(       -1435526201239020  ),
 req(  2147483631  ,   350522204  ), resp(      752740695392042724  ),
]


random_small_msgs = [
 req(  -350439366  ,         -96  ), resp(             33642179136  ),
 req(   996342458  ,          80  ), resp(             79707396640  ),
 req(   771742688  ,        -100  ), resp(            -77174268800  ),
 req(    18811779  ,          69  ), resp(              1298012751  ),
 req(  -100612553  ,         -42  ), resp(              4225727226  ),
 req( -1435677923  ,         -12  ), resp(             17228135076  ),
 req( -1862503134  ,          39  ), resp(            -72637622226  ),
 req( -1217963814  ,         -33  ), resp(             40192805862  ),
 req(  1555414237  ,          -6  ), resp(             -9332485422  ),
 req(  1503807239  ,         -97  ), resp(           -145869302183  ),
]


random_large_msgs = [
 req(  -505560281  ,      -11309  ), resp(           5717381217829  ),
 req( -2144449348  ,      -18409  ), resp(          39477168047332  ),
 req(  1739547911  ,       -6678  ), resp(         -11616700949658  ),
 req(  -574112255  ,       23500  ), resp(         -13491637992500  ),
 req(  -529507246  ,       11798  ), resp(          -6247126488308  ),
 req(  1534142954  ,        3877  ), resp(           5947872232658  ),
 req( -1835052710  ,      -23265  ), resp(          42692501298150  ),
 req(   657960658  ,        2573  ), resp(           1692932773034  ),
 req( -1062954964  ,      -28575  ), resp(          30373938096300  ),
 req( -1688571851  ,       -3955  ), resp(           6678301670705  ),
]


random_edge_msgs = [
 req(  -834415129  , -2147483619  ), resp(     1791892820973271851  ),
 req(   171634928  , -2147483619  ), resp(     -368583196328244432  ),
 req(  -888664482  ,  2147483640  ), resp(    -1908392436544074480  ),
 req( -1184270314  ,  2147483584  ), resp(    -2543201058333525376  ),
 req( -1501989101  ,  2147483590  ), resp(    -3225496946756352590  ),
 req(  -519586800  ,  2147483623  ), resp(    -1115804143726976400  ),
 req( -1023216195  ,  2147483579  ), resp(    -2197339976529361905  ),
 req(  1560135513  , -2147483645  ), resp(    -3350365498151184885  ),
 req( -1885609788  , -2147483579  ), resp(     4049316056131671252  ),
 req(  1104859340  , -2147483555  ), resp(    -2372667263238153700  ),
]


random_random_msgs = [
 req( -1328685195  , -1635311094  ), resp(     2172813639817053330  ),
 req(  -828793178  ,   617724079  ), resp(     -511965502561533062  ),
 req(  1315926239  , -1791225236  ), resp(    -2357120288011367404  ),
 req(  1090403951  ,   379500097  ), resp(      413808405173683247  ),
 req(  -602463958  , -1554043057  ), resp(      936254931022639606  ),
 req(   105587933  , -1802808116  ), resp(     -190354782564064228  ),
 req(  1262349940  ,   113637036  ), resp(      143449705576377840  ),
 req(  -670026434  , -1642288893  ), resp(     1100376970574597562  ),
 req(   -90483769  ,  2128234056  ), resp(     -192570638701037064  ),
 req( -1786637674  ,  -666439471  ), resp(     1190685866329230454  ),
 req(  4294967040  ,  4278255615  ), resp(    18374966855119929600  ),
 req(  4294902015  ,    16776960  ), resp(       72055399309574400  ),
 req(    16777215  ,  4278255360  ), resp(       71777209999622400  ),
 req(  4278255615  ,  4294901760  ), resp(    18374687570593382400  ),
 req(  4294901760  ,    16711935  ), resp(       71776119044505600  ),
 req(  4278190335  ,  4294902015  ), resp(    18374408290345025025  ),
 req(       65535  ,  4278255615  ), resp(         280375481729025  ),
 req(    16711935  ,  4278255360  ), resp(       71497925489721600  ),
 req(    16776960  ,    16776960  ), resp(         281466386841600  ),
 req(  4278255360  ,    16711935  ), resp(       71497925489721600  ),
 req(   177274880  ,           0  ), resp(                       0  ),
 req(  7678260387  ,  1194292802  ), resp(     9170091112075834374  ),
 req(       12352  ,   536870912  ), resp(           6631429505024  ),
 req(  7086909117  , 10108958559  ), resp(    71641270575152282403  ),
 req(           0  ,         512  ), resp(                       0  ),
 req(  1595852930  ,    95130635  ), resp(      151814502597510550  ),
 req(     2097154  ,       80384  ), resp(            168577627136  ),
 req(  6764654419  ,  2204770612  ), resp(    14914511263347134428  ),
 req(   403702273  ,           0  ), resp(                       0  ),
 req(  6494398486  , 13437813383  ), resp(    87270514889705738138  ),
]






test_case_table = mk_test_case_table([
(                        "msgs             src_delay   sink_delay"),
[       "toy_test",        toy_test_msgs,         0,         0],
[    "small_small",     small_small_msgs,         0,         0],
[    "small_small",     small_small_msgs,         0,         1],
[    "small_small",     small_small_msgs,        69,         0],
[    "small_small",     small_small_msgs,        59,        39],
[    "small_large",     small_large_msgs,         0,         0],
[    "small_large",     small_large_msgs,         0,        33],
[    "small_large",     small_large_msgs,        20,         0],
[    "small_large",     small_large_msgs,         0,        60],
[     "small_edge",      small_edge_msgs,         0,         0],
[     "small_edge",      small_edge_msgs,         0,        27],
[     "small_edge",      small_edge_msgs,        30,         0],
[     "small_edge",      small_edge_msgs,        26,        40],
[   "small_random",    small_random_msgs,         0,         0],
[   "small_random",    small_random_msgs,         0,        19],
[   "small_random",    small_random_msgs,        44,         0],
[   "small_random",    small_random_msgs,        95,        10],
[    "large_small",     large_small_msgs,         0,         0],
[    "large_small",     large_small_msgs,         0,        97],
[    "large_small",     large_small_msgs,        86,         0],
[    "large_small",     large_small_msgs,        55,        33],
[    "large_large",     large_large_msgs,         0,         0],
[    "large_large",     large_large_msgs,         0,        97],
[    "large_large",     large_large_msgs,        28,         0],
[    "large_large",     large_large_msgs,         8,        62],
[     "large_edge",      large_edge_msgs,         0,         0],
[     "large_edge",      large_edge_msgs,         0,        98],
[     "large_edge",      large_edge_msgs,        98,         0],
[     "large_edge",      large_edge_msgs,        36,        60],
[   "large_random",    large_random_msgs,         0,         0],
[   "large_random",    large_random_msgs,         0,        74],
[   "large_random",    large_random_msgs,        17,         0],
[   "large_random",    large_random_msgs,         9,        44],
[     "edge_small",      edge_small_msgs,         0,         0],
[     "edge_small",      edge_small_msgs,         0,        36],
[     "edge_small",      edge_small_msgs,        83,         0],
[     "edge_small",      edge_small_msgs,        33,         8],
[     "edge_large",      edge_large_msgs,         0,         0],
[     "edge_large",      edge_large_msgs,         0,        46],
[     "edge_large",      edge_large_msgs,        76,         0],
[     "edge_large",      edge_large_msgs,        57,        60],
[      "edge_edge",       edge_edge_msgs,         0,         0],
[      "edge_edge",       edge_edge_msgs,         0,        37],
[      "edge_edge",       edge_edge_msgs,         0,         0],
[      "edge_edge",       edge_edge_msgs,        46,         6],
[    "edge_random",     edge_random_msgs,         0,         0],
[    "edge_random",     edge_random_msgs,         0,        74],
[    "edge_random",     edge_random_msgs,        23,         0],
[    "edge_random",     edge_random_msgs,        55,        25],
[   "random_small",    random_small_msgs,         0,         0],
[   "random_small",    random_small_msgs,         0,        72],
[   "random_small",    random_small_msgs,        31,         0],
[   "random_small",    random_small_msgs,        85,        29],
[   "random_large",    random_large_msgs,         0,         0],
[   "random_large",    random_large_msgs,         0,        70],
[   "random_large",    random_large_msgs,        54,         0],
[   "random_large",    random_large_msgs,         6,        55],
[    "random_edge",     random_edge_msgs,         0,         0],
[    "random_edge",     random_edge_msgs,         0,        84],
[    "random_edge",     random_edge_msgs,        78,         0],
[    "random_edge",     random_edge_msgs,        23,        47],
[  "random_random",   random_random_msgs,         0,         0],
[  "random_random",   random_random_msgs,         0,        33],
[  "random_random",   random_random_msgs,        30,         0],
[  "random_random",   random_random_msgs,         8,         9],
])







#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_sim( TestHarness( IntMulFL(),
                        test_params.msgs[::2], test_params.msgs[1::2],
                        test_params.src_delay, test_params.sink_delay ),
           dump_vcd )

