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

## Setup (VS Code)
- Download ms-vscode-remote.remote-containers extension
- On Windows press ```Ctrl, shift + P``` to open up the command palette
- Find ```Remote-Containers: Open Workspace in Container```
    - This should download all the requirements for the container
- On a browser head to ```http://localhost:9000``` to access CMAK
- Click on Cluster > Add Cluster & copy the setup in the image [here](docs/cmak_setup.png) & hit save
- Run the [kafka_python](log_generator/output/kafka_python.py) file & you will have messages to view in CMAK
