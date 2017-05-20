from slackclient import SlackClient


class _SlackNotifier:
    def __init__(self, slack_token):
        self._slack_client = SlackClient(slack_token)

    def send_message(self, channel_id, message, username):
        try:
            return self._slack_client.api_call(
                "chat.postMessage",
                channel=channel_id,
                text=message,
                username=username
            )
        except Exception as e:
            return {
                'ok': False,
                'error': e
            }


def send_slack_message(slack_token, channel_id, message, username):
    slack_notifier = _SlackNotifier(slack_token)
    return slack_notifier.send_message(channel_id, message, username)
