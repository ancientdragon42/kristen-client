from __future__ import print_function

import prox
import re
import json
import os
import sys

# The constants
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
        # Make a 13 word summary with a "..."
        short = " ".join(words[:13])+"..."
        return (short, long)
    else:
        # Someone used crazy vocab and 13 words made 120 characters
        print("WHAT IS THIS: " + long)
        return (None, long)

regex = (r'<A HREF="(?P<url>.*?)"><B>(?P<title>.*?) - by (?P<author>.*?)</B>' +
         r'</A>( - (?P<short>.*?))? - (?P<long>.*)\s*\((?P<tags>.*?)\)\s*' +
         r'.*?<BR><BR>')

# Ensure the index folder exists
if not os.path.isdir("karchive"):
    print("Creating index folder...")
    os.mkdir("karchive")

# This is so we don't print a newline if there's no status printed
need_newline = False
for number in range(START_NUM, NUM_DIRS+1):
    # Skip already downloaded pages
    if os.path.isfile("karchive/{:02d}.json".format(number)):
        continue

    # Print the status message for the current folder
    sys.stdout.write("\rDownloading {:02d}/82...".format(number))
    sys.stdout.flush()
    need_newline = True

    # Create an empty directory to be saved
    directory = []
    # Download page #N of the archive
    req = prox.request(
        "http://asstr.org/~Kristen/{n:02d}/index{n:02d}.htm".format(n=number)
    )
    content = req.read()
    # Extract all the entries out of the HTML
    for item in re.finditer(regex, content):
        # Get properties from the entry
        # Things need to be brought from latin1 into utf8 so they
        # can be JSON encoded later
        url = item.group('url').decode('latin1').encode('utf8')
        title = item.group('title').decode('latin1').encode('utf8')
        author = item.group('author').decode('latin1').encode('utf8')

        # Get the long and short descriptions
        short = item.group('short')
        long = item.group('long').strip().strip('"').decode(
                    'latin1').encode('utf8')
        # If the short description is missing, try to build one
        if short is None:
            # This might involve moving the long description into the short
            # one if it's short enough, or cutting a sentence out of the long
            short, long = fix_short(long)
        else:
            # Clean up the quotes and things and sanitize the string
            short = short.strip().strip('"').decode('latin1').encode('utf8')
        
        # Split the tags on commas to make a tag list
        tags = item.group('tags').decode('latin1').encode('utf8').split(",")
        entry = {
            "title": title,
            "url": url,
            "author": author,
            "short": short,
            "long": long,
            "tags": tags
        }
        # Store the created entry in the directory so we can export them
        # all at once
        directory.append(entry)

    # Write out the current directory as JSON
    with open("karchive/{:02d}.json".format(number), "w") as f:
        f.write(json.dumps(directory))

# Print a newline if we had printed inline stuff
if need_newline:
    print()
