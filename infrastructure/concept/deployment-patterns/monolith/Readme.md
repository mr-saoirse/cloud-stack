# About - WIP

Monolith is a dummy project for playing with deployment patterns and Kubernetes use cases.

## The Kafka clients

To run the sample set some env variables

```bash
export MONOLITH_IMAGE="WHERE YOU BUILD AND PUSH THE DOCKER IMAGE"
export WORKFLOW_DIR="WHERE YOUR WORKFLOW LIVES"
```

You can start the scheduler

```bash
python cli.py scheduler start
```

Post message(s) to Kafka - the workflow runs every N minutes, consumes from Kafka and applies the workers
