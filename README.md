# AWS-Region-Ping

Performs repeated TCP handshakes with the EC2 API endpoints (enumerated via ec2:DescribeRegions) in the various regions, and returns statistics on the RTTs.

The RTT is derived from the three-way handshake pair (open, and close) by dividing the handshake time in two. In practice, it is two round trips to complete the socket open and graceful close.

## Example Output

```json
$ python3 aws_region_ping.py --pings-per-region 250
{
  ...
    "ca-central-1": {
        "count": 250,
        "errors": 0,
        "max": 0.03694558143615723,
        "mean": 0.01730522918701172,
        "median": 0.017184555530548096,
        "min": 0.01574873924255371,
        "stdev": 0.001495932409499759
    },
    "eu-central-1": {
        "count": 250,
        "errors": 0,
        "max": 0.13738274574279785,
        "mean": 0.0649686689376831,
        "median": 0.0638437271118164,
        "min": 0.060950517654418945,
        "stdev": 0.005276259454930074
    },
  ...
}
```

`jq` is handy for massaging this into something you might care more about, the average milliseconds for a one-way round trip (assuming path)

```json
$ python3 aws_region_ping.py --pings-per-region 100 | jq '. | map_values(10000*.mean | floor | ./10)'
{
  "ap-northeast-1": 42.9,
  "ap-northeast-2": 51.25,
  "ap-south-1": 73.6,
  "ap-southeast-1": 65.25,
  "ap-southeast-2": 70.45,
  "ca-central-1": 8.65,
  "eu-central-1": 32.45,
  "eu-west-1": 34.45,
  "eu-west-2": 31.85,
  "eu-west-3": 31.15,
  "sa-east-1": 44.9,
  "us-east-1": 14.5,
  "us-east-2": 12.25,
  "us-west-1": 21.35,
  "us-west-2": 17.1
}
```
