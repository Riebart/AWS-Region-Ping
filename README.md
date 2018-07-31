# AWS-Region-Ping

Performs repeated TCP handshakes with the EC2 API endpoints (enumerated via ec2:DescribeRegions) in the various regions, and returns statistics on the RTTs.

## Example Output

```json
$ python3 aws_region_ping.py --pings-per-region 250
{
  ...
    "ca-central-1": {
        "count": 250,
        "errors": 0,
        "max": 0.0732574462890625,
        "mean": 0.035907711029052734,
        "median": 0.03600454330444336,
        "min": 0.03160262107849121,
        "stdev": 0.0035189862267197072
    },
    "eu-central-1": {
        "count": 250,
        "errors": 0,
        "max": 0.2570481300354004,
        "mean": 0.13174918460845947,
        "median": 0.1292515993118286,
        "min": 0.12469148635864258,
        "stdev": 0.009426455151220692
    },
  ...
}
```

`jq` is handy for massaging this into something you might care more about, the average milliseconds for a one-way round trip (assuming path)

```json
$ python3 aws_region_ping.py --pings-per-region 100 | jq '. | map_values(10000*.mean | floor | ./10)'
{
  "ap-northeast-1": 87.5,
  "ap-northeast-2": 102.5,
  "ap-south-1": 146,
  "ap-southeast-1": 131.9,
  "ap-southeast-2": 142.1,
  "ca-central-1": 17.95,
  "eu-central-1": 65.85,
  "eu-west-1": 69.1,
  "eu-west-2": 63.75,
  "eu-west-3": 61.7,
  "sa-east-1": 92.5,
  "us-east-1": 29.05,
  "us-east-2": 24.25,
  "us-west-1": 46.6,
  "us-west-2": 33.3
}
```
