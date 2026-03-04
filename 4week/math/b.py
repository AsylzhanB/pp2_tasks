import sys
x1, y1 = map(float, sys.stdin.readline().split())
x2, y2 = map(float, sys.stdin.readline().split())
y2_ref = -y2
t = -y1 / (y2_ref - y1)
x_reflect = x1 + t * (x2 - x1)
y_reflect = 0.0
print(f"{x_reflect:.10f} {y_reflect:.10f}")