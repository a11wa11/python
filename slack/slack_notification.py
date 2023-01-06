nsimport json
import logging
import requests
import boto3
from base64 import b64decode

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):

    # 要識別子&チャンネル名&ユーザー名修正
    WEB_HOOK_URL = 'https://hooks.slack.com/services/識別子'
    event['channel'] = 'チャンネル名'
    event['username'] = 'ユーザー名'
    event['text'] = 'これはテストメッセージです'
    if ('channel' not in event):
        raise AttributeError('slack channel is not set.')
    logger.info('request: %s', str(event))
    try:
        requests.post(WEB_HOOK_URL, json.dumps(event).encode('utf-8'))
        logger.info("Message posted to %s", event['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)
