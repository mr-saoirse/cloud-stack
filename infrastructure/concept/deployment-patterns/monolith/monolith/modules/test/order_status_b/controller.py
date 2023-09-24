from .schema import OrderStatus
from loguru import logger
from monolith.modules.core.ops import deployment_attributes
from monolith.common.KafkaClient import kafka_batch_consumer
from typing import Optional, List, Union

@deployment_attributes(memory='2Gi', namespace="test.order_status")
def handler(message: Union[OrderStatus,dict,str], context=None) -> dict:
    # we can map any of these values to the object if its correct: str->dict->OrderStatus
    logger.info(f"handling message {message}")
    return {}
   
   
@deployment_attributes(interval_minutes='*/5', memory='1Gi', namespace="test.order_status") 
@kafka_batch_consumer(limit=2, topic='test.order_status')
def generator(messages: Optional[List[OrderStatus]], context=None ) -> List[dict]:
    logger.info(f"Generating...")
    if messages:
        return [d.dict() for d in messages]
    #for testing a dummy message - we should change the memory to the ^ if its not memory mapped
    return [
        {'message':'dummy', "memory": '1Gi'}
    ]
    

def reducer(context=None)-> dict:
    logger.info(f"Reducing...")
    return {}