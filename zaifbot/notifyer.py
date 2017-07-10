from slackclient import SlackClient


class SlackNotifier:
    def __init__(self, slack_token):
        self._slack_client = SlackClient(slack_token)

    def send_message(self, channel_id, message, username):
        try:
            api_response = self._slack_client.api_call(
                "chat.postMessage",
                channel=channel_id,
                text=message,
                username=username
            )
            if api_response['ok'] is True:
                response = {
                    'success': 1,
                    'return': api_response['message']
                }
            else:
                response = {
                    'success': 0,
                    'error': api_response['error']
                }
        except Exception as e:
            response = {
                'success': 0,
                'error': str(e)
            }
        return response


def send_slack_message(slack_token, channel_id, message, username):
    slack_notifier = SlackNotifier(slack_token)
    return slack_notifier.send_message(channel_id, message, username)