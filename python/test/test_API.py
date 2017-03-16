import pytest
from time import sleep
from ..rtcdc import Node, ConnectionError, SignalHandler, SignalError
import uuid
import requests

class OurHTTPSignalHandler(SignalHandler):
    def __init__(self, server_url):
        self.server_url = server_url
    def register(self, uid, sdp, candidate):
        requests.put(self.server_url + "/register", data = {'sdp': sdp, 'uuid': uuid.hex, 'cand': cand})
    def request(self, t_uid):
        get_target = requests.get(self.server_url + "/request", params = {'uuid': target_uuid })
        try:
            target = get_target.json()
        except ValueError:
            raise SignalError("Could not find {}".format(t_uid))
        return (target["sdp"], target["candidate"])

def test_star_local():
    sig_handler = OurHTTPSignalHandler("http://127.0.0.1:5000")
    nodeA = Node("xyz", sig_handler, "stun.services.mozilla.com", 3418)
    nodeB = Node("123", sig_handler, "stun.services.mozilla.com", 3418)
    nodeC = Node("abc", sig_handler, "stun.services.mozilla.com", 3418)

    nodeA.connect("123")
    nodeA.connect("abc")

    try:
        nodeA.send_message("abc", "message")
        assert nodeC.get_message() == "message"
    except ConnectionError as e:
        print(e.message)
