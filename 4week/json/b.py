import sys
g = 0 
def outer(commands):
    n = 0  
    def inner():
        nonlocal n
        global g
        for scope, value in commands:
            value = int(value)
            if scope == "global":
                g += value
            elif scope == "nonlocal":
                n += value
            elif scope == "local":
                x = value  
    inner()
    return n
input = sys.stdin.read
data = input().splitlines()
t = int(data[0])
commands = [line.split() for line in data[1:]]
n_final = outer(commands)
print(g, n_final)