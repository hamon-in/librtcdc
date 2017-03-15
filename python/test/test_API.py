import pytest
from time import sleep
from ..rtcdc import Peer, ConnectionError, SignalHandler, SignalError
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
    peerA = Peer(uid="xyz", OurHTTPSignalHandler)
    peerB = Peer(uid="123", OurHTTPSignalHandler)
    peerC = Peer(uid="abc", OurHTTPSignalHandler)

    peerA.connect("123")
    peerA.connect("abc")

    try:
        peerA.send_message(peerC, "message")
        assert peerC.get_message() == "message"
    except ConnectionError as e:
        print(e.message)
