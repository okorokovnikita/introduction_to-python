import sys

steps = int(sys.argv[1])
for i in range(1, steps + 1):
    print(" " * (steps - i) + "#" * i)
