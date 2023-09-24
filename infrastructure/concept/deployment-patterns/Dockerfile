FROM python:3.10
RUN pip install loguru pydantic confluent-kafka[avro] typer pyyaml argo-workflows wrapt
ADD ./monolith/ /app/
ADD ./sample/map-reduce-flow.yaml /app/workflows
ENV PYTHONPATH "${PYTHONPATH}:/app"
CMD ["python", "/app/cli.py"]
