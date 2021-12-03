//========================================================================
// mtbmark-sort-v1
//========================================================================
// This version (v1) is brought over directly from Fall 15. It uses
// quicksort to sort each fourth of the elements, and then run 3 times of
// two-way merge. The first two merge runs are parallelized.

#include "common.h"
#include "mtbmark-sort.dat"

// '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Implement multicore sorting
// '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

//------------------------------------------------------------------------
// Argument struct
//------------------------------------------------------------------------
// This is used to pass arguments when we spawn work onto the cores.

typedef struct {
  int* src;  // pointer to src0 array
  int  begin; // first element this core should process
  int  end;   // (one past) last element this core should process
} arg_t;

//------------------------------------------------------------------------
// multicore-hybrid-quicksort-mergesort
//------------------------------------------------------------------------
void quicksort_scalar(int* src, int begin, int end){
  // implement quicksort algorithm here
    if (end-begin == 0)
      return;
      
    int i, size = end - begin;
    int pivot = src[0];
    int left[size], mid[size], right[size];
    int left_ptr = 0, mid_ptr = 0, right_ptr = 0;

    for ( i = begin; i < end; i++ ){
      if(src[i] < pivot){
        left[left_ptr++] = src[i];
      } else if (src[i] == pivot){
        mid[mid_ptr++] = src[i];
      } else {
        right[right_ptr++] = src[i];
      }
    }

    quicksort_scalar(left, 0, left_ptr);
    quicksort_scalar(right,0, right_ptr);

    for ( i = begin; i < end; i++){
      if (i < begin+left_ptr) 
        src[i] = left[i-begin];
      else if (i >= begin + left_ptr && i < begin+mid_ptr + left_ptr)
        src[i] = mid[i - left_ptr - begin];
      else if(i >= begin+ left_ptr + mid_ptr && i < end)
        src[i] = right[i - mid_ptr - left_ptr - begin];
    }
}

__attribute__ ((noinline))
void quicksort( void* arg_vptr )
{
  // Cast void* to argument pointer.

  arg_t* arg_ptr = (arg_t*) arg_vptr;

  // Create local variables for each field of the argument structure.

  int* src   = arg_ptr->src;
  int  begin = arg_ptr->begin;
  int  end   = arg_ptr->end;

  // Call scalar quicksort
  quicksort_scalar(src, begin, end);

}

//------------------------------------------------------------------------
// verify_results
//------------------------------------------------------------------------

void verify_results( int dest[], int ref[], int size )
{
  int i;
  for ( i = 0; i < size; i++ ) {
    if ( !( dest[i] == ref[i] ) ) {
      test_fail( i, dest[i], ref[i] );
    }
  }
  test_pass();
}

//------------------------------------------------------------------------
// Test Harness
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{

  // Initialize the bthread (bare thread)

  bthread_init();

  int dest[size];

  // Initialize dest array, which stores the final result.

  //--------------------------------------------------------------------
  // Start counting stats
  //--------------------------------------------------------------------

  test_stats_on();

  int i = 0;

  // Because we need in-place sorting, we need to create a mutable temp
  // array.
  int temp0[size];
  for ( i = 0; i < size; i++ ) {
    temp0[i] = src[i];
  }

  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: distribute work and call sort_scalar()
  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  int block_size = size / 4;
  arg_t arg0 = {temp0, 0,             block_size};
  arg_t arg1 = {temp0, block_size,    2*block_size};
  arg_t arg2 = {temp0, 2*block_size,  3*block_size};
  arg_t arg3 = {temp0, 3*block_size,  size};

  // Spawn work onto cores 1, 2, and 3.

  bthread_spawn( 1, &quicksort, &arg1 );
  bthread_spawn( 2, &quicksort, &arg2 );
  bthread_spawn( 3, &quicksort, &arg3 );

  // Have core 0 also do some work.

  quicksort( &arg0 );

  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: do bthread_join(), do the final reduction step here
  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // Wait for all to join
  bthread_join(1);
  bthread_join(2);
  bthread_join(3);

  // mergesort
  // merge 4 in one loop, can do parallelization
  // first mergesort 2 on 2 cores, then core 0 responsible for doing the final merge
  // As it is stated on the top of this file.
  int temp0_ptr = 0;
  int temp1_ptr = block_size;
  int temp2_ptr = 2*block_size;
  int temp3_ptr = 3*block_size;
  for (i = 0; i < size; i++){
    int min = 0x7fffffff;
    if (temp0[temp0_ptr] < min && temp0_ptr < block_size)
      min = temp0[temp0_ptr];
    if (temp0[temp1_ptr] < min && temp1_ptr < 2*block_size)
      min = temp0[temp1_ptr];
    if (temp0[temp2_ptr] < min && temp2_ptr < 3*block_size)
      min = temp0[temp2_ptr];
    if (temp0[temp3_ptr] < min && temp3_ptr < size)
      min = temp0[temp3_ptr];

    dest[i] = min;

    if (temp0[temp0_ptr] == dest[i])
      temp0_ptr += 1;
    else if (temp0[temp1_ptr] == dest[i])
      temp1_ptr += 1;
    else if (temp0[temp2_ptr] == dest[i])
      temp2_ptr += 1;
    else if (temp0[temp3_ptr] == dest[i])
      temp3_ptr += 1;
  }

  //--------------------------------------------------------------------
  // Stop counting stats
  //--------------------------------------------------------------------

  test_stats_off();

  // verifies solution

  verify_results( dest, ref, size );

  return 0;
}
