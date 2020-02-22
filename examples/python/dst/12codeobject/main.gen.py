import re
import sys


pattern = re.compile('^(?P<label>DEBUG|INFO|WARNING|ERROR|CRITICAL):\\s*(?P<message>\\S+)', re.IGNORECASE)
for line in sys.stdin:
    matched = pattern.search(line)
    if matched is not None:
        print(matched.groupdict())
