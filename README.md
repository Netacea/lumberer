# Netacea Log Generator

## Functional Requirements
- Generate logs
- To be used by multiple parsers
- Output to multiple sinks

## Non Functional Requirements
- "Benchmark mode"
- Add some unexpected data
- Pacing of outputing data -> Scheduling in the future
- Handle a lot of data
- Multithreaded processes (producer)
- Test python consumer parsers (integration testing)

## Setup

### Visual Studio Code (WSL2/Linux VM/Windows)

**Prerequisites**

- Visual Studio Code
- [Docker Remote Connection](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension
- Docker available locally
  - Docker for Desktop should work fine for WSL2 and Windows
  - Docker linux install works fine if your VS Code is installed in the same virtual machine



- On Windows press ```Ctrl, shift + P``` to open up the command palette
- Execute ```Remote-Containers: Open Workspace in Container``` to download all the requirements for the container and reopen Visual Studio Code.
- On a browser open ```http://localhost:9000``` to access CMAK to administrate the local Kafka cluster.
- Click on Cluster > Add Cluster & copy the setup in the image [here](docs/cmak_setup.png) & hit save


**Example Usage**
The tool is split into two commands, the `generate` command which only deals with generating fake log lines (and printing them to standard out) and the `stream` command, which can either take a pipe in standard in, or a filename to a text file to open and stream.

The most common usecase is to pipe `generate` to `stream` and create and send data to Kafka.

`python log_generator generate --log-type apache --iterations 100000 | python log_generator stream --output kafka`

However you can redirect the output of `generate` to a file:
`python log_generator generate --log-type apache --iterations 10000 > apache.log`

Additionally you can feed a file into the streamer, and this is useful if you want to create a reproduceable log, or stream a log to the sink quicker than you can generate new log lines.
`python log_generator stream --file apache.log --output kafka`
