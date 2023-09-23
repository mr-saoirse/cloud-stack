
from . KafkaClient import PydanticKafkaClient
from loguru import logger

def as_topic(name):
    return name.lower().replace('/','.')

def from_module(module_name, name):
    module = f'monolith.modules.{module_name}'
    module = __import__(module, fromlist=[name])
    return getattr(module, name)
 

def consume_for_module(module):
    """
    using very simple convention 
    """
    handler = from_module(module, 'handler')
    ptype = from_module(module, 'entity_type' )
    
    logger.info(f"We have {handler}({ptype})")
    
    client = PydanticKafkaClient(ptype, as_topic(module))
    client.consume(handler=handler)
    
    
    