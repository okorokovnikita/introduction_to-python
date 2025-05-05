import sys
import math

def solve_quadratic(a, b, c):
    discriminant = b**2 - 4*a*c
    sqrt_discriminant = math.sqrt(discriminant)
    x1 = int((-b + sqrt_discriminant) / (2*a))
    x2 = int((-b - sqrt_discriminant) / (2*a))
    return x1, x2

a, b, c = map(int, sys.argv[1:4])
x1, x2 = solve_quadratic(a, b, c)
print(x1)
print(x2)
