import base64
import json
import logging
from flask import Flask
import flask_sockets

HTTP_SERVER_PORT = 5770

# Fix for flask_sockets
# https://community.plotly.com/t/dash-extensions-websockets-getting-error-when-i-run-examples/54562/4
def add_url_rule(self, rule, _, f, **options):
    self.url_map.add(flask_sockets.Rule(rule, endpoint=f, websocket=True))
flask_sockets.Sockets.add_url_rule = add_url_rule

app = Flask(__name__)
sockets = flask_sockets.Sockets(app)

@sockets.route('/media', websocket=True)
def echo(ws):
    app.logger.info("Connection accepted")
    # A lot of messages will be sent rapidly. We'll stop showing after the first one.
    has_seen_media = False
    message_count = 0
    while not ws.closed:
        message = ws.receive()
        if message is None:
            app.logger.info("No message received...")
            continue

        # Messages are a JSON encoded string
        data = json.loads(message)

        # Using the event type you can determine what type of message you are receiving
        if data['event'] == "connected":
            app.logger.info("Connected Message received: {}".format(message))
        if data['event'] == "start":
            app.logger.info("Start Message received: {}".format(message))
        if data['event'] == "media":
            if not has_seen_media:
                app.logger.info("Media message: {}".format(message))
                payload = data['media']['payload']
                app.logger.info("Payload is: {}".format(payload))
                chunk = base64.b64decode(payload)
                app.logger.info("That's {} bytes".format(len(chunk)))
                app.logger.info("Additional media messages from WebSocket are being suppressed....")
                has_seen_media = True
        if data['event'] == "closed":
            app.logger.info("Closed Message received: {}".format(message))
            break
        message_count += 1

    app.logger.info("Connection closed. Received a total of {} messages".format(message_count))


if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('0.0.0.0', HTTP_SERVER_PORT), app, handler_class=WebSocketHandler)
    print("Server listening on: http://localhost:" + str(HTTP_SERVER_PORT))
    server.serve_forever()