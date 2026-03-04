def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b
n = int(input())
print(",".join(str(num) for num in fibonacci(n)))