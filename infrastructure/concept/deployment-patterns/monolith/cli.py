import typer
import json
from loguru import logger
from typing import Optional
from monolith.common.KafkaClient import PydanticKafkaClient
from monolith.modules.core.scheduler import start_scheduler

app = typer.Typer()

kafka_app = typer.Typer()
app.add_typer(kafka_app, name="kafka")

scheduler_app = typer.Typer()
app.add_typer(scheduler_app, name="scheduler")

@app.command("run")
def run_method(
    topic:str = typer.Option(None, "--topic", "-t"),
    method: Optional[str] = typer.Option(None, "--method", "-m"),
    value: Optional[str] = typer.Option(None, "--value", "-v")
):
    logger.info(f"Invoke -> {topic=} {method=} {value=}")
    
    """
    Run the specific module - unit test we can always load them and we get correct request
    Also output something for the workflow output parameters below
    """
    
    
    #if we start doing real work on the handlers we can remove this
    with open('/tmp/out', 'w') as f:
        #illustrates the contract in the workflow DAG
        dummy_message =  {'message':'dummy', "metadata": {'memory': '1Gi'}}
        data = [dummy_message, dummy_message] if method == "generator" else dummy_message
        logger.debug(f"Dumping {data}")
        json.dump(data,f) 
        
    return data
    
@kafka_app.command("consume")
def consume_topic(
    topic:str = typer.Option(None, "--topic", "-t"),
):
    logger.info(f"Dispatching {topic}")
    PydanticKafkaClient.consume_for_module(topic)
    
@scheduler_app.command("start")
def scheduler_start():
    logger.info(f"Starting scheduler")
    _ = start_scheduler()
    
if __name__ == "__main__":
    app()