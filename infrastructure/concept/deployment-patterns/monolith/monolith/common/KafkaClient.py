import os
from loguru import logger
import traceback
from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
import fastavro
from pydantic import BaseModel
from typing import Union
import functools
import wrapt

DEFAULT_POLL_TIMEOUT = 3.
DUMMY_PATH = "/app/monolith/modules/test/order_status/schema.avsc"

class PydanticKafkaClient:
    def __init__(self, pydantic_type, topic, local_schema_path=DUMMY_PATH, group_id='test'):
        sr_conf = {'url': f"http://{os.environ['KAFKA_SCHEMA_REGISTRY_URL']}"}
        schema_registry_client = SchemaRegistryClient(sr_conf)
        
        with open(local_schema_path) as f:
            schema_str = f.read()
        
        consumer_conf = {
            'bootstrap.servers': os.environ['KAFKA_BROKERS'],
            'group.id': group_id,
            'security.protocol': 'ssl',
            'auto.offset.reset': "earliest"
            }
        
        self._consumer = Consumer(consumer_conf)
        self._consumer.subscribe([topic])
        self._avro_deserializer = AvroDeserializer(schema_registry_client,
                                         schema_str,
                                         lambda obj, ctx: pydantic_type(**obj))
        
        logger.info("setup client")
        
    def consume(self, handler, limit= -1):
        """
        supply a handler to handle pydantic message
        if you want to limit the batch size specify a positive number as batch size
        """
        logger.info("consuming...")
        while True:
            try:
                msg = self._consumer.poll(DEFAULT_POLL_TIMEOUT)
                if msg is None:
                    continue
                logger.debug('got a message')
                logger.debug(msg)
                message= self._avro_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
                handler(message)       
            except:
                logger.warning(f"Error on consumption {traceback.format_exc()}")
            finally:
                limit -=1
                if limit == 0:
                    break
            
    def fetch(self, limit):
        """
        fetches a batch of messages
        if you want to limit the batch size specify a positive number as batch size
        """
        logger.info("consuming...")
        while True:
            try:
                msg = self._consumer.poll(DEFAULT_POLL_TIMEOUT)
                if msg is None:
                    continue
                #note we are not strictly consuming LIMIT messages if we timeout - we can add two different types of counters for that
                logger.debug('got a message')
                logger.debug(msg)
                yield self._avro_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
                
            except:
                logger.warning(f"Error on consumption {traceback.format_exc()}")
            finally:
                limit -=1
                if limit == 0:
                    break

    def produce(self, message : Union[BaseModel, dict], validate: str =None):
        """
        try to send a message - if its pydantic then dict it otherwise send as is
        we can also validate on entry or on exit - the latter might seem strange but fastavro can explain better what went wrong
        """
        if hasattr(message, 'dict'):
            message = message.dict()
        raise NotImplementedError("TODO")
    
    

    @staticmethod
    def consume_for_module(module):
        """
        using very simple convention to start a consumer
        """
        def as_topic(name):
            return name.lower().replace('/','.')

        def from_module(module_name, name):
            module = f'monolith.modules.{module_name}'
            module = __import__(module, fromlist=[name])
            return getattr(module, name)

        handler = from_module(module, 'handler')
        ptype = from_module(module, 'entity_type' )
        
        logger.info(f"We have {handler}({ptype})")
        
        client = PydanticKafkaClient(ptype, as_topic(module))
        client.consume(handler=handler)
    
    
def kafka_batch_consumer(obj=None, topic=None, ptype=None, limit=-1): 
    """
    A wrapper on handler function to turn it into a consumer
    """
    # to allow with or without args we trap the case where there is no obj
    if obj is None:
        return functools.partial(kafka_batch_consumer)
    
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        
        #note for testing if you want to you can *could* check if the message is in kwargs here
        #then you can just call the wrapped message with the payload and skip kafka
        #this is useful if you want to test the workflow without kafka
        
        client = PydanticKafkaClient(ptype, topic)
        messages = list(client.fetch(limit=limit, *args, **kwargs))
        return wrapped(messages, **args, **kwargs)

    return wrapper(obj)