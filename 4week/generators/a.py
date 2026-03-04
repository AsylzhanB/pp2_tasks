def even(n):
    for i in range(0, n+1,2):
        yield i

n = int(input().strip())
print(",".join(map(str, even(n))))