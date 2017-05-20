from slackclient import SlackClient


class SlackNotifier(object):
    def __init__(self, slack_token):
        self._slack_client = SlackClient(slack_token)

    def send_message(self, channel_id, message, username):
        return self._slack_client.api_call(
            "chat.postMessage",
            channel=channel_id,
            text=message,
            username=username
        )


def send_slack_message(slack_token, channel_id, message, username):
    slack_notifier = SlackNotifier(slack_token)
    return slack_notifier.send_message(channel_id, message, username)
