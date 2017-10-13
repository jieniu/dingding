#!/usr/bin/python
#coding:utf-8

import logging, sys
import ConfigParser
import requests
import json

config = ConfigParser.ConfigParser()
config.read("/usr/lib/zabbix/alertscripts/config.ini")
log_path = config.get("global", "log_path")

logger = logging.getLogger()
handler = logging.FileHandler(log_path)
formatter = logging.Formatter('%(asctime)s %(name)-s %(levelname)-s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)

class DingdingAlerter():
    def __init__(self, webhook_url, title, content):
        self.webhook_url = webhook_url
        self.title = title
        self.content = content

    def getTextMsg(self):
        payload = {
            "msgtype": "text",
            "text": {
                "content": self.content
            }
        }
        return payload

    def alert(self):
        headers = {'content-type': 'application/json'}
        payload = self.getTextMsg()
        try:
            response = requests.post(self.webhook_url, json.dumps(payload, cls=DateTimeEncoder), headers=headers)
            response.raise_for_status()
        except Exception as e:
            logger.error("Unexpected Error: {}".format(e))


if len(sys.argv) == 4:
    send_to = sys.argv[1]
    subject = sys.argv[2]
    content = sys.argv[3]
    logger.debug("send_to: %s, subject %s, content %s" % (send_to, subject, content))

    try:
        webhook_url = config.get("webhooks", send_to)
        alert = DingdingAlerter(webhook_url, subject, content)
        alert.alert()
    except Exception as e:
        logger.error("Unexpected Error: {}".format(e))

else:
    logger.error("usage: ./dingding.py $send_to $subject $content")
