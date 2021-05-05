# Netacea Log Generator

:trophy: _Lab Week Winner 2021/04_ :trophy:

![splash](docs/splash.gif) 

## tl;dr

- Ever wanted to generate pseudo realistic data for testing a process?
- Ever wanted to take that data and stream it to the sink of your choice?
- Ever wanted to be able to rate limit that process?

**_Your dreams have been answered._**



## Requirements 

### Functional Requirements
- [x] Generate logs
- [x] To be used by multiple parsers
- [x] Output to multiple sinks

### Non Functional Requirements
- [x] Benchmark mode
- [x] Add some unexpected data
- [x] Pacing of outputing data -> Scheduling in the future
- [x] Handle a lot of data
- [x] Multithreaded processes

## Development Setup

This project is a boilerplate python package using pip to install dependencies. As such you can set up a virtualenv and install dependencies if you wish, run it inside a docker container, or use the Visual Studio Code Devcontainer bindings for a full development stack.

### Virtualenv

_This only sets up the client application, not the docker compose stack for kafka to develop against_

- Git clone this repository
- python -m venv .venv
- pip install -r requirements.txt

### Visual Studio Code (WSL2/Linux VM/Windows)

_This starts a docker compose stack found at `.devcontainer/docker-compose.yml`, including kafka, zookeeper and CMAK_

#### Prerequisites

- Visual Studio Code
- [Docker Remote Connection](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension
- Docker available locally
  - Docker for Desktop should work fine for WSL2 and Windows
  - Docker linux install works fine if your VS Code is installed in the same virtual machine

#### First Run

- On Windows press ```Ctrl, shift + P``` to open up the command palette
- Execute ```Remote-Containers: Open Workspace in Container``` to download all the requirements for the container and reopen Visual Studio Code.
- On a browser open ```http://localhost:9000``` to access CMAK to administrate the local Kafka cluster.
- Click on Cluster > Add Cluster & copy the setup in the image and save.
  
![cmak](docs/cmak_setup.png) 

## Usage

### Docker Specific Instructions

Instead of dealing with the dependencies you can work with a docker container directly, but you need to build the Dockerfile included.

```bash
docker build -f Dockerfile . -t log-generator:latest
```

The instructions below apply to the container in terms of general use cases but the syntax is different:

```bash
docker run -i -e SASL_USERNAME=EXAMPLEUSERNAME -e SASL_PASSWORD=EXAMPLEPASSWORD log-generator:latest python stream kafka --broker example.eu-west-1.aws.confluent.cloud:9092 --topic test1 -e security.protocol=SASL_SSL -e sasl.mechanisms=PLAIN -e compression.type=zstd < larger.log
```

In this example, we're taking a file that resides outside the docker conatainer (`larger.log`) and using a pipe to stream it into stdin on the running python application inside the container, this then streams each line to Confluent Kafka with the additional configuration needed (such as the security options and optional compression).

Conversely, generate works by writing to the docker containers stdout buffer, which is then returned to the docker client running the command:

```bash
docker run -i log-generator:latest python generate --logtype apache --iterations 10
```

You can run both together with a pipe, despite it being a lot of clunky docker CLI wrapping it:

```bash
docker run -i log-generator:latest python generate --logtype apache --iterations 10 | docker run -i -e SASL_USERNAME=EXAMPLEUSERNAME -e SASL_PASSWORD=EXAMPLEPASSWORD log-generator:latest python stream kafka --broker example.eu-west-1.aws.confluent.cloud:9092 --topic test1 -e security.protocol=SASL_SSL -e sasl.mechanisms=PLAIN -e compression.type=zstd -p 1
```

### General Usage

The tool is split into two commands, the `generate` command which only deals with generating log lines (and printing them to standard out) and the `stream` command, which can either take a pipe in standard in, or a filename to a text file to open and stream.

**Firstly and foremost, both tools have detailed `--help` flags to display the arguments and options each command has.**

A common use-case is to pipe `generate` to `stream` and create and send data to Kafka.

```bash
generate --logtype apache --iterations 100000 | stream kafka --broker broker:9092 --topic my-topic -p 1
```

However you can redirect the output of `generate` to a file:

```bash
generate --logtype apache --iterations 10000 > apache.log
```

Additionally you can feed a file into the streamer, and this is useful if you want to create a reproduceable log, or stream a log to the sink quicker than you can generate new log lines:

```bash
stream kafka --broker broker:9092 --topic my-topic apache.log 
```

### Random Insertion of Corrupted Logs

You can run the `generate` command with the `-b` or `--baddata` flag to insert incorrect data among the data being generated. An example command is `generate -l apache -b 100`. The number after the `-b` flag is a percentage of logs you want to be corrupted. 

E.g. ```-baddata 50``` would give you roughly 50% corrupted data in your sample. Example of an incorrect log line for Apache is as follows:

```bash
256.500.301.9000 - - [29/Apr/2021:15:28:31 +0000] "BLAH /!?£$%^&*()-_category/tags/list-----=two&f=1 HTTP/5.0" 603 "!?£$%^&*()-_http://stein.com/" "!£$%^&*()-_+Mozilla/5.0 (iPod; U; CPU iPhone OS 3_3 like Mac OS X; ur-PK) AppleWebKit/531.32.3 (KHTML, like Gecko) Version/3.0.5 Mobile/8B115 Safari/6531.32.3"
```

If you need to intersperce broken data into your logs, to test error handling downstream you can use the `generate` command with the `--baddata` or `-b` option. This option is an integer which represents the approximate average of bad data to inject in the stream.

For example; `-b 40` value would on average, send 40% bad data to the sink.

### Rate Limiting and Scheduling

The stream utility has the capacity to either flat out rate limit the streaming data, or adjust the streaming data rate limit using a json file.

#### Rate Limiting

In this example we're reading from a local file, and rate limiting the downstream transmission rate to 1 message a second.

```bash
stream kafka --broker broker:9092 --topic my-topic --rate 1 example.apache.log
```
![rate-limit](docs/rate_limit.gif) 


To confirm if this is working, you can refer to CMAK for an overview of the status for the topic -
![rate-limit](docs/rate_limit.png) 

There will be some overhead with buffering in the transmission phase, so the generated pace may not accurately line up with the reported pace of messages but it's pretty close.

#### Scheduling

To schedule rate limiting in the streamer, you can call the command in the example shown below, and the json format shown here.

The update interval represents how long it stays at that pace in seconds, in this example 10 seconds. Every 3 seconds it'll jump to the next number in the array, so for the first 3 seconds, it'll stream 10 records a second, then the next 3 seconds stream at a rate of 20 records a second, and finally 5 records a second for the third block of 3 seconds.

At completion of iterating through the array, it'll cycle back the beginning and read the first value and continue iterating.

```json
{
    "update_interval": 3,
    "schedule": [
        10,
        20,
        5
    ]
}
```

![scheduling](docs/schedule.gif)

Another example could look something like this, where you change the interval every hour (3600 seconds), and the timings vaguely represent the load variations in the hours throughout the day.

In this example, lunchtime is vaguely busy, and the evening is busy, with early morning being very sparse.

```json
{
    "update_interval": 3600,
    "schedule": [
        1,
        1,
        1,
        1,
        1,
        2,
        2,
        3,
        3,
        3,
        4,
        4,
        5,
        3,
        2,
        2,
        4,
        5,
        6,
        10,
        7,
        5,
        2,
        1,
    ]
}
```

### Benchmarking Kafka

:+1: _The docker image has `pv` installed to monitor the bandwidth through a unix pipe, so running this command will give you both the runtime of the process but also the instantaneous current bandwidth in the pipe._

#### Simple Benchmark

```bash
$ time bzcat example.apache.log.bz2 | stream kafka --broker broker:9092 --topic my-topic
```

![benchmark](docs/benchmark.gif)

In this example the compressed test data (1,000,000 Apache log lines) took 11 seconds to decompress and produce into Kafka, and a throughput of approximately 103,000 messages a second.

### Concurrency

To utilise more than one thread on the machine, you can use a combination of `xargs` and either `seq` for a fixed number, or polling `/proc/cpuinfo` to automatically used the thread count available to the tool. 

```bash
cat /proc/cpuinfo | grep processor | awk '{print $3}'| xargs -n 1 -P 0 bash -c "generate --logtype apache --iterations 10000 --quiet" | stream kafka --broker broker:9092 --topic test123
```

![benchmark](docs/xargs.gif)

See [xargs man page](https://man7.org/linux/man-pages/man1/xargs.1.html) for more details.

_tl;dr `xargs` is set to use as many threads as it can via the use of the `-P 0` option and `-n 1` option runs each `xargs` sub thread with one of the lines piped in._

## Sources and Sinks

This tool has various sources and sinks.

### S3

AWS Simple Storage Service is a common storage both as a source and a sink.


#### Sink

You can write log files into S3 directly from the std stream, breaking the files at the `--linecount` size. In this example 100,000 log lines were split into 10 files, 10,000 log lines long.

```bash
generate --logtype apache --iterations 100000 | stream s3 --bucket "netacea-log-generator-sink" --prefix "demo/" --linecount 10000 -p 1
```

![benchmark](docs/s3_sink.gif)

![benchmark](docs/s3_sink.png)

#### Source

In addition to being a sink, you generate log files to - you can also use it as a source to read from and send to a different sink.

This is especially useful when combined with the rate limiting or scheduling shown here:

```bash
aws s3 ls s3://netacea-log-generator-sink/demo --recursive | awk '{print $4}' | xargs -n 1 -I {} aws s3 cp s3://netacea-log-generator-sink/{} - | stream kafka --broker broker:9092 --topic aws-dump --rate 10
```

![benchmark](docs/s3_source.gif)

### Kinesis

AWS Kinesis can be used to send data.


#### Sink

You can send data in kinesis. The sink will take care of batching the data up to the maximum size (500) and send them in the stream provided. The stream should already exist in AWS.

```bash
generate --logtype apache --iterations 100000 | stream kinesis --stream "log-generator-stream"
```