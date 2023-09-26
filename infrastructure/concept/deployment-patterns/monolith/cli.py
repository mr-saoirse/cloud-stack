import typer
import json
from loguru import logger
from typing import Optional
from monolith.common.KafkaClient import PydanticKafkaClient
from monolith.modules.core.scheduler import start_scheduler
from monolith.modules.core.ops import load_op, inspect_modules

app = typer.Typer()

kafka_app = typer.Typer()
app.add_typer(kafka_app, name="kafka")

scheduler_app = typer.Typer()
app.add_typer(scheduler_app, name="scheduler")

modules_app = typer.Typer()
app.add_typer(modules_app, name="modules")

@app.command("run")
def run_method(
    name:str = typer.Option(None, "--name", "-n"),
    method: Optional[str] = typer.Option(None, "--method", "-m"),
    value: Optional[str] = typer.Option(None, "--value", "-v"),
    is_test: Optional[bool] = typer.Option(False, "--test", "-t")
):
    logger.info(f"Invoke -> {name=} {method=} {value=}")
    
    """
    Run the specific module - unit test we can always load them and we get correct request
    Also output something for the workflow output parameters below
    
    to test the workflows and not worry about real handlers you can pass -t in the workflow
    """
    
    with open('/tmp/out', 'w') as f:
        if is_test:
            dummy_message =  {'message':'dummy', "memory": "1Gi"}
            data = [dummy_message, dummy_message] if method == "generator" else dummy_message
            logger.debug(f"Dumping {data}")
        else:
            fn = load_op(name, method)
            data = fn(value)
        
        json.dump(data,f) 
        
        return data or []
        
    
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
    
@modules_app.command("inspect")
def scheduler_start():
    logger.info(f"Starting scheduler")
    for m in inspect_modules():
        logger.info(m.dict())
    
if __name__ == "__main__":
    app()