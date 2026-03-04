from datetime import datetime, timedelta
import sys
def parse_time(line):
    dt_part, utc_part = line.strip().rsplit(" ", 1)
    dt = datetime.strptime(dt_part, "%Y-%m-%d %H:%M:%S")
    sign = 1 if utc_part[3] == '+' else -1
    hours = int(utc_part[4:6])
    minutes = int(utc_part[7:9])
    offset = timedelta(hours=hours, minutes=minutes)
    return dt - sign * offset

start_line = sys.stdin.readline()
end_line = sys.stdin.readline()
start_utc = parse_time(start_line)
end_utc = parse_time(end_line)
duration = int((end_utc - start_utc).total_seconds())
print(duration)