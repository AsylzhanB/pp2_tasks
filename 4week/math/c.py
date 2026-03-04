import math
import sys
r = float(sys.stdin.readline())
x1, y1 = map(float, sys.stdin.readline().split())
x2, y2 = map(float, sys.stdin.readline().split())
dx = x2 - x1
dy = y2 - y1
a = dx*dx + dy*dy
b = 2 * (x1*dx + y1*dy)
c = x1*x1 + y1*y1 - r*r
D = b*b - 4*a*c
if D < 0:
    print("0.0000000000")
else:
    sqrtD = math.sqrt(D)
    t1 = (-b - sqrtD) / (2*a)
    t2 = (-b + sqrtD) / (2*a)
    t_min = max(0.0, min(t1, t2))
    t_max = min(1.0, max(t1, t2))
    if t_min > t_max:
        print("0.0000000000")
    else:
        segment_length = math.hypot(dx, dy)
        inside_length = segment_length * (t_max - t_min)
        print(f"{inside_length:.10f}")