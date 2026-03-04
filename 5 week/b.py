import re
pattern = "(\d\d\d)-(\d\d\d)-(\d\d\d\d)"
new_pattern = r"\1\2\3"
user_phone = input()
new_user_phone = re.sub(pattern, new_pattern, user_phone)
print(new_user_phone)