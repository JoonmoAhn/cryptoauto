import requests

class Slackbot:
    def __init__(self, token, channel):
        self.token_ = token
        self.channel_ = channel

    def post_text(self, text):
        # send message to slack
        response = requests.post("https://slack.com/api/chat.postMessage",
            headers={"Authorization": "Bearer "+self.token_},
            data={"channel": self.channel_,"text": text}
            )
        return response

