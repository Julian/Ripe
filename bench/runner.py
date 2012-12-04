#!/usr/bin/env python
"""
Modified from fijal/hippyvm's runner.

./runner.py -b <base ruby> -m <modified ruby>

"""

import argparse
import glob
import json
import os
import subprocess


ALL_BENCHMARKS = sorted(
    glob.iglob(os.path.join(os.path.dirname(__file__), "*.rb"))
)

def run_bench(ruby):
    results = {}
    for bench in ALL_BENCHMARKS:
        print "Running %s %s" % (ruby, bench)
        command = [ruby, bench]

        r = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        r.wait()
        if r.returncode != 0:
            dump_output(r)
            raise subprocess.CalledProcessError(r.returncode, command)
        results[bench] = time(r)

    print
    return results


def time(process):
    return process.stdout.read()


def dump_output(process):
    print "=" * 79
    print "stdout"
    print "=" * 79

    for line in process.stdout:
        print line

    print "=" * 79
    print "stderr"
    print "=" * 79

    for line in process.stderr:
        print line


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('base')
    parser.add_argument('modified', nargs="?", default=None)
    parser.add_argument('-o', '--output', type=argparse.FileType("w"))

    args = parser.parse_args(argv)
    base = run_bench(args.base)

    if args.modified is not None:
        modified = run_bench(args.modified)

    if args.output is not None:
        json.dump({'base': base, 'modified': modified}, args.output)
    else:
        for bench, time in base.iteritems():
            print "%s\t%s" % (bench, time)

if __name__ == '__main__':
    main()
