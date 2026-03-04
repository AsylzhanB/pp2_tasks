import re
pattern = "[a -zA-Z0-9]+@[a-zA-Z]+\.(com|edu|net)"
user_email = input()
if (re.search(pattern, user_email)):
    print("valid email")
else:
    print("invalid email")