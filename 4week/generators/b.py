def div(n):
    for i in range(0, n+1):
        if i %12 == 0:
            yield i

n = int(input().strip())
print(" ".join(str(s) for s in div(n)))