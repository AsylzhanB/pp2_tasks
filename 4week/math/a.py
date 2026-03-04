import math
import sys
r = float(sys.stdin.readline())
x1, y1 = map(float, sys.stdin.readline().split())
x2, y2 = map(float, sys.stdin.readline().split())
direct_dist = math.hypot(x2 - x1, y2 - y1)
dx = x2 - x1
dy = y2 - y1
A = dy
B = -dx
C = dx*y1 - dy*x1
dist_to_line = abs(C) / math.hypot(A, B)
dot1 = (0 - x1)*(x2 - x1) + (0 - y1)*(y2 - y1)
dot2 = (0 - x2)*(x1 - x2) + (0 - y2)*(y1 - y2)
intersects = (
    dist_to_line < r and
    dot1 >= 0 and
    dot2 >= 0
)
if not intersects:
    print(f"{direct_dist:.10f}")
else:
    OA = math.hypot(x1, y1)
    OB = math.hypot(x2, y2)
    tangent_A = math.sqrt(OA*OA - r*r)
    tangent_B = math.sqrt(OB*OB - r*r)
    angle_A = math.acos(r / OA)
    angle_B = math.acos(r / OB)
    angle_between = math.acos(
        (x1*x2 + y1*y2) / (OA * OB)
    )
    arc_angle = angle_between - angle_A - angle_B
    shortest = tangent_A + tangent_B + r * arc_angle
    print(f"{shortest:.10f}")