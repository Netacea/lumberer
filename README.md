# Netacea Log Generator

![splash](docs/splash.gif) 

## Requirements 

### Functional Requirements
- [x] Generate logs
- [x] To be used by multiple parsers
- [x] Output to multiple sinks

### Non Functional Requirements
- [x] "Benchmark mode"
- [x] Add some unexpected data
- [x] Pacing of outputing data -> Scheduling in the future
- [x] Handle a lot of data
- [x] Multithreaded processes
- [ ] Test python consumer parsers (integration testing)

## Setup

### Visual Studio Code (WSL2/Linux VM/Windows)

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
- Click on Cluster > Add Cluster & copy the setup in the image and save 
  ![cmak](docs/cmak_setup.png) 


## Example Usage

The tool is split into two commands, the `generate` command which only deals with generating fake log lines (and printing them to standard out) and the `stream` command, which can either take a pipe in standard in, or a filename to a text file to open and stream.

The most common usecase is to pipe `generate` to `stream` and create and send data to Kafka.

```generate --logtype apache --iterations 100000 | stream kafka --broker broker:9092 --topic my-topic```

However you can redirect the output of `generate` to a file:

```generate --logtype apache --iterations 10000 > apache.log```

Additionally you can feed a file into the streamer, and this is useful if you want to create a reproduceable log, or stream a log to the sink quicker than you can generate new log lines:

```stream kafka --broker broker:9092 apache.log --topic my-topic```

## Benchmarking Kafka

The docker image has `pv` installed to monitor the bandwidth through a unix pipe, so running this command will give you both the runtime of the process but also the instantaneous current bandwidth in the pipe.

Example Output:

```bash
$ time bzcat example.apache.log.bz2 | pv | stream kafka --broker broker:9092 --topic my-topic
 215MiB 0:01:27 [2.48MiB/s] [                    <=>                                ]

real    1m27.189s
user    1m52.882s
sys     0m17.771s
```

In this example the test data (1,000,000 Apache log lines) took 1m27 to produce into Kafka, and a throughput from the text source of 2.5MiB/s.

## Rate Limiting and Scheduling

Log generation rate limiting and scheduling of changes to the rate limiter is implemented in the streaming side of the project.

See [the documentation](docs/rate_limit.md) for more.

## Random insertion of corrupted logs
You can run the ```generate``` command with the ```-b``` or ```--baddata``` flag to insert incorrect data among the data being generated. An example command is ```generate -l apache -b 100```. The number after the ```-b``` flag is a percentage of logs you want to be corrupted. 

E.g. ```-baddata 50``` would give you roughly 50% corrupted data in your sample. Example of an incorrect log line for Apache is as follows:
```
256.500.301.9000 - - [29/Apr/2021:15:28:31 +0000] "BLAH /!?£$%^&*()-_category/tags/list-----=two&f=1 HTTP/5.0" 603 "!?£$%^&*()-_http://stein.com/" "!£$%^&*()-_+Mozilla/5.0 (iPod; U; CPU iPhone OS 3_3 like Mac OS X; ur-PK) AppleWebKit/531.32.3 (KHTML, like Gecko) Version/3.0.5 Mobile/8B115 Safari/6531.32.3"
```
## FOR SOME REAL SPEEEEEED

To utilise all threads on the machine, use the following command.

```cat /proc/cpuinfo | grep processor | xargs -n 1 -P 0 bash -c "generate --logtype apache --iterations 100000 --quiet" | stream kafka --broker broker:9092 --topic test123 ```

See [xargs man page](https://man7.org/linux/man-pages/man1/xargs.1.html) for more details.
