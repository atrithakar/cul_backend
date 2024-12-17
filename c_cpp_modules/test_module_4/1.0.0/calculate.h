#include "../test_module_1/1.0.2/mathss.h"

int addply(int a, int b) {
    int sum = add(a, b);
    int prod = multiply(sum, b);
    return prod;
}