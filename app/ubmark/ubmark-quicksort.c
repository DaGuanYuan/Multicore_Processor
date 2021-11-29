//========================================================================
// ubmark-quicksort
//========================================================================
// This version (v1) is brought over directly from Fall 15.

#include "common.h"
#include "ubmark-quicksort.dat"

//------------------------------------------------------------------------
// quicksort-scalar
//------------------------------------------------------------------------

// '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Add functions you may need
// '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

__attribute__ ((noinline))
void quicksort_scalar( int* dest, int* src, int size )
{

  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Implement main function of serial quicksort
  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    if (size == 0)
      return;
    // implement quicksort algorithm here
    int i;
    int pivot = src[0];
    int left[size], mid[size], right[size];
    int left_ptr = 0, mid_ptr = 0, right_ptr = 0;

    for ( i = 0; i < size; i++ ){
      if(src[i] < pivot){
        left[left_ptr++] = src[i];
      } else if (src[i] == pivot){
        mid[mid_ptr++] = src[i];
      } else {
        right[right_ptr++] = src[i];
      }
    }

    int left_sorted[left_ptr], right_sorted[right_ptr];
    quicksort_scalar(left_sorted, left, left_ptr);
    quicksort_scalar(right_sorted, right, right_ptr);

    for ( i = 0; i < size; i++){
      if (i < left_ptr) 
        dest[i] = left_sorted[i];
      else if (i >=left_ptr && i < mid_ptr + left_ptr)
        dest[i] = mid[i - left_ptr];
      else if(i >= left_ptr + mid_ptr && i < size)
        dest[i] = right_sorted[i - mid_ptr - left_ptr];
    }

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
  int dest[size];

  int i;
  for ( i = 0; i < size; i++ )
    dest[i] = 0;

  test_stats_on();
  quicksort_scalar( dest, src, size );
  test_stats_off();

  verify_results( dest, ref, size );

  return 0;
}
