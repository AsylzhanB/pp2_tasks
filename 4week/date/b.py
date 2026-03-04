from datetime import date
import sys
def parse_local_date(line):
    dt_part = line.strip().split()[0]
    year, month, day = map(int, dt_part.split("-"))
    return date(year, month, day)

def next_birthday(birth_date, current_date):
    year = current_date.year
    month = birth_date.month
    day = birth_date.day
    try:
        candidate = date(year, month, day)
    except ValueError:
        candidate = date(year, 2, 28)
    if candidate < current_date:
        year += 1
        try:
            candidate = date(year, month, day)
        except ValueError:
            candidate = date(year, 2, 28)
    return candidate
birth = parse_local_date(sys.stdin.readline())
current = parse_local_date(sys.stdin.readline())
next_bday = next_birthday(birth, current)
days_left = (next_bday - current).days
print(days_left)