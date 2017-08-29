#!/usr/bin/python

from twitter import *

# -----------------------------------------------------------------------
# load our API credentials
# -----------------------------------------------------------------------
config = {}
execfile("config.py", config)

# -----------------------------------------------------------------------
# create twitter API object
# -----------------------------------------------------------------------
twitter = Twitter(
    auth=OAuth(config["access_token"],
               config["access_token_secret"],
               config["consumer_key"],
               config["consumer_secret"]))


query = twitter.search.tweets(q="arganoel")

# -----------------------------------------------------------------------
# How long did this query take?
# -----------------------------------------------------------------------
print "Search complete (%.3f seconds)" % (query["search_metadata"]["completed_in"])

# -----------------------------------------------------------------------
# Loop through each of the results, and print its content.
# -----------------------------------------------------------------------
for result in query["statuses"]:
    print "(%s) @%s %s" % (result["created_at"], result["user"]["screen_name"], result["text"])
