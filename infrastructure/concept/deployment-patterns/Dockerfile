FROM python:3.10
RUN pip install loguru pydantic confluent-kafka[avro] typer pyyaml argo-workflows
ADD ./monolith/ /app/
ADD ./sample/map-reduce-flow.yaml /app/workflows
ENV PYTHONPATH "${PYTHONPATH}:/app"
CMD ["python", "/app/cli.py"]

#docker build --pull --rm -f "Dockerfile" -t res-data:test-kafka --platform linux/amd64 .
#docker tag res-data:test-kafka 286292902993.dkr.ecr.us-east-1.amazonaws.com/res-data:test-kafka & docker push 286292902993.dkr.ecr.us-east-1.amazonaws.com/res-data:test-kafka
