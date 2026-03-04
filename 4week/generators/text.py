class Reverse:
    def __init__(self, s):
        self.s = s
        self.index = len(s)  # Start after last character
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index == 0:
            raise StopIteration
        self.index -= 1
        return self.s[self.index]
s = input()
for ch in Reverse(s):
    print(ch, end="")
print()