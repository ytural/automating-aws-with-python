import os
import requests


def post_to_slack(event, context):
    slack_webhook_url = os.environ['SLACK_WEBHOOK_URL']
    slack_message = 'From {source} at {detail[StartTime]}: {detail[Description]}'.format(**event)
    requests.post(slack_webhook_url, json=slack_message)
    print(slack_message)
    return
