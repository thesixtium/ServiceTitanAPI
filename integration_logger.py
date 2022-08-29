import datetime
import re


def log(change):
    now = datetime.datetime.now()
    date = str(now)
    date = re.sub(":", "-", date)
    date = re.sub("\.[0-9]+", "", date)

    change = re.sub('\n', ' \\n ', change)
    string = f"[{date}]: {change}\n"

    f = open("log.txt", "a")

    if len(string) > 300:
        string = string[0:300]

    f.write(string)
    print(string, end="")

    f.close()
