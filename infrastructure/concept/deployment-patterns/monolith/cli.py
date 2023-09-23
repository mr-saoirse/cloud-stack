import typer
from monolith.common.dispatcher import consume_for_module
from loguru import logger
app = typer.Typer()

kafka_app = typer.Typer()
app.add_typer(kafka_app, name="kafka")


@kafka_app.command("consume")
def consume_topic(
    topic:str = typer.Option(None, "--topic", "-t"),
):
    logger.info(f"Dispatching {topic}")
    consume_for_module(topic)
    
if __name__ == "__main__":
    app()