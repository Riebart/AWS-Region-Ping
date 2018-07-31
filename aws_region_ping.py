#!/usr/bin/env python3
"""
Test the TCP RTT to each AWS region by connecting to the HTTP port for the EC2 API endpoint
for EC2 in each region.
"""

from __future__ import print_function

import sys
import json
import time
import socket
import argparse
import threading
import statistics

import boto3

global region_results
region_results = dict()


def tcping(host, port, verbose):
    """
    Open a socket to the remote endpoint, timing how long it takes the socket to become ready.
    """
    t0 = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    try:
        s.connect((host, port))
    except Exception as e:
        sys.stderr.write(repr(e) + "\n")
        result = e
    else:
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        result = None
    ret = (time.time() - t0, s, result)

    if verbose:
        print((host, ret[0]), file=sys.stderr)
    return ret


def ping_region(region, region_name, ping_count, verbose):
    """
    TCPing a region a handful of times, returning the full set of errors and timings.
    """
    if verbose:
        print(
            "Pinging %s %d times" % (region_name, ping_count), file=sys.stderr)
    result = [tcping(region, 80, verbose) for _ in range(ping_count)]
    global region_results
    region_results[region_name] = result


def __summarize_region_results(results):
    successes = [r[0] / 2 for r in results if r[-1] is None]
    return {
        "count": len(results),
        "errors": len(results) - len(successes),
        "min": min(successes),
        "max": max(successes),
        "mean": statistics.mean(successes),
        "median": statistics.median(successes),
        "stdev": statistics.stdev(successes)
    }


def __main(pings_per_region, verbose):
    ec2 = boto3.client("ec2")
    try:
        regions = ec2.describe_regions()
    except:
        if verbose:
            print(
                "Unable to get regions from AWS API, using hard-coded defaults",
                file=sys.stderr)
        regions = {
            "Regions": [{
                "Endpoint": "ec2.ap-south-1.amazonaws.com",
                "RegionName": "ap-south-1"
            }, {
                "Endpoint": "ec2.eu-west-3.amazonaws.com",
                "RegionName": "eu-west-3"
            }, {
                "Endpoint": "ec2.eu-west-2.amazonaws.com",
                "RegionName": "eu-west-2"
            }, {
                "Endpoint": "ec2.eu-west-1.amazonaws.com",
                "RegionName": "eu-west-1"
            }, {
                "Endpoint": "ec2.ap-northeast-2.amazonaws.com",
                "RegionName": "ap-northeast-2"
            }, {
                "Endpoint": "ec2.ap-northeast-1.amazonaws.com",
                "RegionName": "ap-northeast-1"
            }, {
                "Endpoint": "ec2.sa-east-1.amazonaws.com",
                "RegionName": "sa-east-1"
            }, {
                "Endpoint": "ec2.ca-central-1.amazonaws.com",
                "RegionName": "ca-central-1"
            }, {
                "Endpoint": "ec2.ap-southeast-1.amazonaws.com",
                "RegionName": "ap-southeast-1"
            }, {
                "Endpoint": "ec2.ap-southeast-2.amazonaws.com",
                "RegionName": "ap-southeast-2"
            }, {
                "Endpoint": "ec2.eu-central-1.amazonaws.com",
                "RegionName": "eu-central-1"
            }, {
                "Endpoint": "ec2.us-east-1.amazonaws.com",
                "RegionName": "us-east-1"
            }, {
                "Endpoint": "ec2.us-east-2.amazonaws.com",
                "RegionName": "us-east-2"
            }, {
                "Endpoint": "ec2.us-west-1.amazonaws.com",
                "RegionName": "us-west-1"
            }, {
                "Endpoint": "ec2.us-west-2.amazonaws.com",
                "RegionName": "us-west-2"
            }]
        }


    threads = [
        threading.Thread(
            target=lambda
                _host=region["Endpoint"],
                _name=region["RegionName"],
                _count=pings_per_region,
                _verbose=verbose: ping_region(_host, _name, _count, _verbose))
            for region in regions["Regions"]
            ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    summary = {
        k: __summarize_region_results(v)
        for k, v in region_results.items()
    }

    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pings-per-region",
        type=int,
        required=True,
        help="""Number of times to complete a TCP handshake with the region""")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="""If set, print out information about pings for each region""")
    pargs = parser.parse_args()

    __main(pargs.pings_per_region, pargs.verbose)
