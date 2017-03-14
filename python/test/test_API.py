import pytest
from unittest.mock import Mock
from time import sleep

def test_star():
    from ..rtcdc import Peer
    on_message = Mock()

    peerA = Peer(on_message = None)
    peerB = Peer(on_message = on_message)
    peerC = Peer(on_message = on_message)

    peerA.connect(peerB)
    peerA.connect(peerC)

    peerA.send_message(peerC, "message") #Exception if A is not connected to C
    print("Waiting 5 seconds just to be safe")
    sleep(5)
    on_message.assert_called_with(msg == "message")
