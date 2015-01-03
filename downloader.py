from __future__ import print_function

import prox
import re
import json
import os
import sys

MAX_SHORT = 120
NUM_DIRS = 82
START_NUM = 1

def fix_short(long):
    if len(item.group('long')) < MAX_SHORT:
        # It's short enough, we can just use the long one in place of the short
        return (long, None)
    attempt_1 = long.split(".")
    if len(attempt_1[0]) < MAX_SHORT:
        # Use the first sentence if it's short enough
        short = attempt_1[0]+"."
        return (short, long)
    words = long.split()
    if len(words) > 13:
        short = " ".join(words[:13])+"..."
        return (short, long)
    else:
        print("WHAT IS THIS: " + long)
        return (None, long)

regex = (r'<A HREF="(?P<url>.*?)"><B>(?P<title>.*?) - by (?P<author>.*?)</B>' +
         r'</A>( - (?P<short>.*?))? - (?P<long>.*)\s*\((?P<tags>.*?)\)\s*' +
         r'.*?<BR><BR>')

if not os.path.isdir("karchive"):
    os.mkdir("karchive")

directories = []
for _ in range(NUM_DIRS+1):
    directories.append([])

sys.stdout.write("\r{:02d}/82".format(0))
sys.stdout.flush()

for number in range(START_NUM, NUM_DIRS+1):
    req = prox.request("http://asstr.org/~Kristen/{n:02d}/index{n:02d}.htm".format(n=number))
    content = req.read()
    for item in re.finditer(regex, content):
        url = item.group('url').decode('latin1').encode('utf8')
        title = item.group('title').decode('latin1').encode('utf8')
        author = item.group('author').decode('latin1').encode('utf8')

        short = item.group('short')
        long = item.group('long').strip().strip('"').decode(
                    'latin1').encode('utf8')
        if short is None:
            short, long = fix_short(long)
        else:
            short = short.strip().strip('"').decode('latin1').encode('utf8')
        
        tags = item.group('tags').decode('latin1').encode('utf8').split(",")
        entry = {
            "title": title,
            "url": url,
            "author": author,
            "short": short,
            "long": long,
            "tags": tags
        }
        directories[number].append(entry)
    with open("karchive/{:02d}.json".format(number), "w") as f:
        f.write(json.dumps(directories[number]))
    sys.stdout.write("\r{:02d}/82".format(number))
    sys.stdout.flush()
