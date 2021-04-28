# Netacea Log Generator

## Requirements 

### Functional Requirements
- [x] Generate logs
- [ ] To be used by multiple parsers
- [x] Output to multiple sinks

### Non Functional Requirements
- [ ] "Benchmark mode"
- [ ] Add some unexpected data
- [x] Pacing of outputing data -> Scheduling in the future
- [x] Handle a lot of data
- [ ] Multithreaded processes
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

```python log_generator generate --logtype apache --iterations 100000 | python log_generator stream --output kafka```

However you can redirect the output of `generate` to a file:

```python log_generator generate --logtype apache --iterations 10000 > apache.log```

Additionally you can feed a file into the streamer, and this is useful if you want to create a reproduceable log, or stream a log to the sink quicker than you can generate new log lines:

```python log_generator stream --file apache.log --output kafka```

## Benchmarking Kafka

The docker image has `pv` installed to monitor the bandwidth through a unix pipe, so running this command will give you both the runtime of the process but also the instantaneous current bandwidth in the pipe.

Example Output:

```bash
$ time bzcat example.apache.log.bz2 | pv | python log_generator stream --output kafka
 215MiB 0:01:27 [2.48MiB/s] [                    <=>                                ]

real    1m27.189s
user    1m52.882s
sys     0m17.771s
```

In this example the test data (1,000,000 Apache log lines) took 1m27 to produce into Kafka, and a throughput from the text source of 2.5MiB/s.

## Rate Limiting and Scheduling

Log generation rate limiting and scheduling of changes to the rate limiter is implemented in the streaming side of the project.

See [the documentation](docs/rate_limit.md) for more.