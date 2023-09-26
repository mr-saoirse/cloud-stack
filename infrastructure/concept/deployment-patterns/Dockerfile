FROM python:3.10
RUN pip install loguru pydantic==1.10.9 confluent-kafka[avro] typer pyyaml argo-workflows wrapt apscheduler
ADD ./monolith/ /app/
ADD ./sample/map-reduce-flow.yaml /app/workflows
ENV PYTHONPATH "${PYTHONPATH}:/app"
CMD ["python", "/app/cli.py"]
