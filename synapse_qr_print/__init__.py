import logging
from datetime import datetime

from synapse.logging.context import make_deferred_yieldable
from synapse.module_api.errors import ConfigError
from twisted.internet.threads import deferToThread

from .db import init_db, mark_printed, save_message
from .pdf import build_pdf
from .qr import render
from .storage import print_file, save_pdf

logger = logging.getLogger(__name__)

REQUIRED_KEYS = ("target_user", "printer_name", "output_dir", "db_path")
DEFAULT_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

class QrPrintModule:
    def __init__(self, config, api):
        self.config = config
        self.api = api
        init_db(config["db_path"])
        api.register_third_party_rules_callbacks(on_new_event=self.new_event)

    @staticmethod
    def parse_config(config):
        missing = [key for key in REQUIRED_KEYS if not config.get(key)]
        if missing:
            raise ConfigError(f"synapse_qr_print: не заданы параметры {', '.join(missing)}")
        config = dict(config)
        config.setdefault("font_path", DEFAULT_FONT_PATH)
        return config

    async def new_event(self, event, state_events):
        if event.type == "m.room.encrypted":
            logger.info("Сообщение от %s зашифровано, печать невозможна", event.sender)
            return
        if event.type != "m.room.message":
            return

        target = self.config["target_user"]
        if event.sender == target:
            return

        body = event.content.get("body")
        if not isinstance(body, str) or not body.strip():
            return

        member = state_events.get(("m.room.member", target))
        if member is None or member.content.get("membership") != "join":
            return

        logger.info("Сообщение %s от %s, отправляем на печать", event.event_id, event.sender)
        try:
            await make_deferred_yieldable(
                deferToThread(
                    self.process_message,
                    event.event_id,
                    event.room_id,
                    event.sender,
                    event.origin_server_ts,
                    body,
                )
            )
        except Exception:
            logger.exception("Не удалось обработать сообщение %s", event.event_id)

    def process_message(self, event_id, room_id, sender, ts_ms, body):
        sent_at = datetime.fromtimestamp(ts_ms / 1000)

        qr_png = render(f"От {sender} Сообщение: {body}")
        metadata = {
            "Отправитель": sender,
            "Комната": room_id,
            "Время": f"{sent_at:%Y-%m-%d %H:%M:%S}",
        }
        pdf_bytes = build_pdf(body, metadata, qr_png, self.config["font_path"])
        pdf_path = save_pdf(pdf_bytes, self.config["output_dir"], event_id, sent_at)

        db_path = self.config["db_path"]
        if not save_message(db_path, event_id, room_id, sender, sent_at, body, pdf_path):
            logger.info("Сообщение %s уже обработано, повторно не печатаем", event_id)
            return

        print_file(pdf_path, self.config["printer_name"])
        mark_printed(db_path, event_id)
        logger.info("Сообщение %s напечатано, файл %s", event_id, pdf_path)