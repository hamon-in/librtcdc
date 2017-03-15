import pytest
from unittest.mock import Mock
from time import sleep

def test_star():
    from ..rtcdc import Peer, connection_error
    on_message = Mock()

    peerA = Peer()
    peerB = Peer()
    peerC = Peer(on_message = on_message)

    peerA.connect(peerB)
    peerA.connect(peerC)

    try:
        peerA.send_message(peerC, "message")
        print("Waiting 5 seconds just to be safe")
        sleep(5)
        on_message.assert_called_with(msg == "message")
    except connection_error as e:
        print(e.message)

    
