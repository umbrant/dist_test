#!/usr/bin/env python

import getpass
import logging
import os
import sys
import time
import urllib
import urllib2
import simplejson
import time

TEST_MASTER = "http://a1228.halxg.cloudera.com:8081"

RED = "\x1b[31m"
RESET = "\x1b[m"

def generate_job_id():
  return "%s.%d.%d" % (getpass.getuser(), int(time.time()), os.getpid())

def watch_results(job_id):
  url = TEST_MASTER + "/job_status?" + urllib.urlencode([("job_id", job_id)])
  start_time = time.time()

  first = True
  while True:
    result_str = urllib2.urlopen(url).read()
    result = simplejson.loads(result_str)

    # On all but the first iteration, replace the previous line
    if not first:
      print "\x1b[F\x1b[2K",

    first = False
    run_time = time.time() - start_time
    print "%.1fs\t" % run_time,

    print "%d/%d tasks complete" % \
        (result['finished_tasks'], result['total_tasks']),

    if result['failed_tasks']:
      print RED,
      print "(%d failed)" % result['failed_tasks'],
      print RESET,
    print

    if result['finished_tasks'] == result['total_tasks']:
      break
    time.sleep(0.5)

def submit_job_json(json):
  # Verify that it is proper JSON
  simplejson.loads(json)
  job_id = generate_job_id()
  form_data = urllib.urlencode({'job_id': job_id, 'job_json': json})
  result_str = urllib2.urlopen(TEST_MASTER + "/submit_job",
                               data=form_data).read()
  result = result_str
  logging.info("Submitted job: %s", repr(result))
  return job_id

def main(argv):
  logging.basicConfig(level=logging.INFO)

  if len(argv) != 2:
    print >>sys.stderr, "usage: %s tasks.json"
    sys.exit(1)
  job_id = submit_job_json(file(argv[1]).read())

  watch_url = TEST_MASTER + "/job?" + urllib.urlencode([("job_id", job_id)])
  logging.info("Submitted tasks. Watch your results at %s", watch_url)

  watch_results(job_id)

if __name__ == "__main__":
  main(sys.argv)
