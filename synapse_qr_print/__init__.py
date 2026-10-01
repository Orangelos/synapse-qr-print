import logging
from dataclasses import dataclass 
from typing import Any, Dict
from synapse.module_api import ModuleApi

from .qr import render
from .printing import print_png
logger=logging.getLogger(__name__)

class QrPrintModule:
    def __init__(self, config, api):
        self.config=config
        self.api=api
        api.register_third_party_rules_callbacks(on_new_event=self.new_event)

    @staticmethod
    def parse_config(config):
        return config
    
    async def new_event(self, event, state_events):
        if event.type == "m.room.message":
            if event.sender != self.config["target_user"]:
                if event.content.get("body")!="":
                    member=state_events.get(("m.room.member",self.config["target_user"]))
                    if member is None or member.content.get("membership")!="join":
                        return
                    logger.info("Событие: %s от %s", event.type, event.sender)
            elif event.type == "m.room.encrypted":
                logger.info("Сообщение зашифровано от %s", event.sender)
        
                    


