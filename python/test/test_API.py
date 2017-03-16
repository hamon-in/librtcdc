import pytest
from time import sleep
from ..rtcdc import Node, ConnectionError, SignalHandler, SignalError
import uuid
import requests

class OurHTTPSignalHandler(SignalHandler):
    def register(self, uid, sdp, candidate):
        requests.put(args.sigServer + "/register", data = {'sdp': sdp, 'uuid': uuid.hex, 'cand': cand})
    def request(self, t_uid):
        get_target = requests.get(args.sigServer + "/request", params = {'uuid': target_uuid })
        try:
            target = get_target.json()
        except ValueError:
            raise SignalError("Could not find {}".format(t_uid))
        return (target["sdp"], target["candidate"])


def test_star_local():
    nodeA = Node(uid="xyz", OurHTTPSignalHandler)
    nodeB = Node(uid="123", OurHTTPSignalHandler)
    nodeC = Node(uid="abc", OurHTTPSignalHandler)

    nodeA.connect("123")
    nodeA.connect("abc")

    try:
        nodeA.send_message("abc", "message")
        assert nodeC.get_message() == "message"
    except ConnectionError as e:
        print(e.message)
