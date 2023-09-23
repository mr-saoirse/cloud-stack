FROM python:3.10
RUN pip install loguru pydantic confluent-kafka[avro] typer
ADD ./monolith/ /app/
ENV PYTHONPATH "${PYTHONPATH}:/app"
CMD ["python", "/app/cli.py"]

