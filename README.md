# Netacea Lumberer

[![Netacea Header](https://assets.ntcacdn.net/header.jpg)](https://www.netacea.com/)

[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-394/)
[![Version](docs/version_badge.svg)](https://github.com/Netacea/lumberer/blob/main/log_generator/__init__.py)
[![GitHub contributors](https://img.shields.io/github/contributors/Netacea/lumberer.svg)](https://GitHub.com/Netacea/lumberer/graphs/contributors/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Netacea/lumberer/graphs/commit-activity)

## tl;dr
- Ever wanted to generate pseudo realistic data for testing a process?
- Ever wanted to take that data and stream it to the sink of your choice?
- Ever wanted to be able to rate limit that process?

**_Your dreams have been answered._**

![splash](docs/splash.gif)

## Usage
To get development instructions, skip down to [the development section](#development-setup)

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

In this example the compressed test data (1,000,000 Apache log lines) took 11 seconds to decompress and produce into Kafka, with a throughput of approximately 103,000 messages a second.

### Concurrency
To utilise more than one thread on the machine, you can use a combination of `xargs` and either `seq` for a fixed number, or polling `/proc/cpuinfo` to automatically used the thread count available to the tool. 

```bash
cat /proc/cpuinfo | grep processor | awk '{print $3}'| xargs -n 1 -P 0 bash -c "generate --logtype apache --iterations 10000 --quiet" | stream kafka --broker broker:9092 --topic test123
```

![benchmark](docs/xargs.gif)

See [xargs man page](https://man7.org/linux/man-pages/man1/xargs.1.html) for more details.

_tl;dr `xargs` is set to use as many threads as it can via the use of the `-P 0` option and `-n 1` option runs each `xargs` sub thread with one of the lines piped in._

## Sinks
This tool has various sinks, with bespoke configuration pertaining to each module.

**Note** - All the sinks implement a `--position` or `-p` flag on the `stream` program for setting the ordering of the progress bad, by default it's 0 but if you're piping from the generator, the progress bars will intersect, so set it to `1` for concurrent progress, else set the `--quiet` flag on the `generate` end to hide the first progress bar.
The progress bar is set to be hidden by default in non TTY situations, like piping the output out of the `stream` program.

### Apache Kafka
#### Local Development Kafka
If using the docker-compose stack included in the `.devcontainer` directory, you'll get locally running kafka/zoopkeeper/CMAK for local kafka development. There is no authentication so the use of this sink is as a simple as directing it to the docker container hostname:

```bash
stream kafka input.log --broker broker:9092 --topic my-topic
```

#### Confluent Kafka Cloud
To use a Confluent Kafka Cloud sink, you'll need to do some [additional configuration](https://docs.confluent.io/platform/current/installation/configuration/producer-configs.html) and authenticate.

The base command would look similar to this:

```bash
stream kafka input.log --broker example.eu-west-1.aws.confluent.cloud:9092 --topic test1 -e security.protocol=SASL_SSL -e sasl.mechanisms=PLAIN
```

However there's two additional strings that you need to provide, the username and password.

You have two options to set them, either as dedicated CLI option flags or via environment variable values. Running `stream kafka --help` demonstrates how, but the sub section we're interested in is the authentication:

```bash
  --sasl-username TEXT            [env var: SASL_USERNAME]
  --sasl-password TEXT            [env var: SASL_PASSWORD]
```

Optionally to increase producer performance, compress the messages by adding an addition `-e compression.type=zstd` flag (other [compression options](https://docs.confluent.io/platform/current/installation/configuration/producer-configs.html#producerconfigs_compression.type) exist).

### AWS S3
_For Authentication information read [this](#aws-authentication)._

You can write log files into S3 directly from the std stream, breaking the files at the `--linecount` size. In this example 100,000 log lines were split into 10 files, 10,000 log lines long.

```bash
generate --logtype apache --iterations 100000 | stream s3 --bucket "netacea-log-generator-sink" --prefix "demo/" --linecount 10000 -p 1
```

![benchmark](docs/s3_sink.gif)

![benchmark](docs/s3_sink.png)

Additionally you can use inline gzip compression when writing to S3, the files themselves are still represented as a `.log` plaintext file but the content encoding header for gzip is set for filesize/bandwidth reduction.

To use this functionality, use the `--compressed` option on the s3 streaming command.


### AWS Kinesis
_For Authentication information read [this](#aws-authentication)._

The sink will take care of batching the data up to the maximum size (500) and send them in the stream provided. The stream should already exist in AWS.

```bash
generate --logtype apache --iterations 100000 | stream kinesis --stream "log-generator-stream" -p 1
```

### Local Filesystem
This sink will just write files into a directory with a batch size set to split the files up, with optional compression. The destination path must exist first and can be a relative or absolute path.

This sink is primarily useful for pre-rendering logs locally to stream in when generation is a bottleneck for performance testing.

```bash
generate --logtype apache --iterations 100000 | stream filesystem --path "./dump" --linecount 10000 --compressor gzip -p 1
```

Output from this as follows:

```bash
vscode ➜ /workspace (documentation ✗) $ generate --logtype apache --iterations 100000 | stream filesystem --path "./dump" --linecount 10000 --compressor gzip -p 1
Generating: 100%|███████████████████████████████████████████| 100k/100k [00:07<00:00, 12.9klines/s]
Streaming: 100k msgs [00:07, 13.0k msgs/s] 
vscode ➜ /workspace (documentation ✗) $ ls -lah dump/
total 548K
drwxr-xr-x 2 vscode vscode 4.0K May  6 11:28 .
drwxr-xr-x 9 vscode vscode 4.0K May  6 11:23 ..
-rw-r--r-- 1 vscode vscode  53K May  6 11:28 2021-05-06T11:28:29.851030+00:00.log.gz
-rw-r--r-- 1 vscode vscode  53K May  6 11:28 2021-05-06T11:28:30.629801+00:00.log.gz
-rw-r--r-- 1 vscode vscode  52K May  6 11:28 2021-05-06T11:28:31.419421+00:00.log.gz
-rw-r--r-- 1 vscode vscode  52K May  6 11:28 2021-05-06T11:28:32.161834+00:00.log.gz
-rw-r--r-- 1 vscode vscode  54K May  6 11:28 2021-05-06T11:28:32.955496+00:00.log.gz
-rw-r--r-- 1 vscode vscode  52K May  6 11:28 2021-05-06T11:28:33.754064+00:00.log.gz
-rw-r--r-- 1 vscode vscode  54K May  6 11:28 2021-05-06T11:28:34.526077+00:00.log.gz
-rw-r--r-- 1 vscode vscode  54K May  6 11:28 2021-05-06T11:28:35.275809+00:00.log.gz
-rw-r--r-- 1 vscode vscode  52K May  6 11:28 2021-05-06T11:28:36.022407+00:00.log.gz
-rw-r--r-- 1 vscode vscode  51K May  6 11:28 2021-05-06T11:28:36.785243+00:00.log.gz

```

### Stdout
This is a debugging sink, just streams the input to the output, similar to `cat`. However all the rate limiting and scheduling still works so you can use it as a throttle on a pipe similar to `pv` except it's working on lines of text rather than raw bytes.

When using stdout as a test for rate limiting it's most useful to append a redirection to `/dev/null` to the command, which will just show the progress bar and current rate.

```bash
generate --logtype apache --iterations 1000 | stream stdout --rate 10 -p 1 >/dev/null
```

If you're generating to use as a pipe to somewhere else you may wish to silence the progress bar, which is done by redirecting `stderr` to `/dev/null`.

```bash
generate --logtype apache --iterations 10000 --quiet | stream stdout --rate 100 -p 1 2>/dev/null | less
```

## Sources
### Local File
Most simply, you can provide a log file as a positional argument, in this case `larger.log`. It'll open the file, iterate the lines and send it to the sink.

```bash
stream kafka large.log --broker broker:9092 --topic large-log --rate 10
```

### Stdin Pipe
Similar to the local file option, if you don't provide a local file argument the `stream` program will listen to the stdin pipe for text.
This forms the basis of most of the more complex interation with the other sources, which ultimately take logs and get them into the pipe.

#### AWS S3
_For Authentication information read [this](#aws-authentication)._

![s3_source](docs/s3_source.gif)

In addition to being a sink, you can copy S3 keys to - (stdout) so you can use it as a source to read from and send to a different sink. This is especially useful when combined with the rate limiting or scheduling shown here:

```bash
aws s3 ls s3://netacea-log-generator-sink/demo --recursive | awk '{print $4}' | xargs -n 1 -I {} aws s3 cp s3://netacea-log-generator-sink/{} - | stream kafka --broker broker:9092 --topic aws-dump --rate 10
```

Now you can have many large log files on S3 and send them into a sink in a rate limited fashion. 

## Development
This project is a boilerplate python package using pip to install dependencies. As such you can set up a virtualenv and install dependencies if you wish, run it inside a docker container, or use the Visual Studio Code Devcontainer bindings for a full development stack.

### Virtualenv
_This only sets up the client application, not the docker compose stack for kafka to develop against_

- `git clone` this repository
- `cd lumberer`
- `python -m venv .venv`
- `pip install -r requirements.txt`

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

## Footnotes
### AWS Authentication

The AWS configuration is left up to environmental variables, so make sure to set either `~/.aws/credentials` and `~/.aws/config` [files](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) inside the container or volume mount them; or use the [environmental variables](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html) to configure the AWS boto3 library in the terminal session:

```bash
$ export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
$ export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
$ export AWS_DEFAULT_REGION=us-west-2
```