import math
def primes(n):
    for num in range(2, n + 1):
        is_prime = True
        for i in range(2, int(math.isqrt(num)) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            yield num
n = int(input())
print(" ".join(str(p) for p in primes(n)))