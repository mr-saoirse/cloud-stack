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
        
    def consume(self, handler):
        logger.info("consuming...")
        while True:
            
            try:
                msg = self._consumer.poll(DEFAULT_POLL_TIMEOUT)
                if msg is None:
                    continue
                logger.info('got a message')
                logger.info(msg)
                message= self._avro_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
                handler(message)
            except:
                logger.warning(f"Error on consumption {traceback.format_exc()}")
                pass
        

    def produce(self, message : Union[BaseModel, dict], validate: str =None):
        """
        try to send a message - if its pydantic then dict it otherwise send as is
        we can also validate on entry or on exit - the latter might seem strange but fastavro can explain better what went wrong
        """
        if hasattr(message, 'dict'):
            message = message.dict()
        raise NotImplementedError("TODO")