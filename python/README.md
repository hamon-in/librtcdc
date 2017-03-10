Before running any python scripts below, make sure the C part is compiled (or use dockerfile), set the env var `export LD_LIBRARY_PATH=../src/vendor/build` (from `./python` dir)

Build the CFFI module by running `python setup.py build` once.

Use python3

## Star topology test

* `python star_test.py`. onConnect only fires once. Open the script to view comments/notes.

## stress_p2p.py

* Install Flask
* Run the signalling server `python sig_srv.py` It will run on 127.0.0.1:5000
* Run `python stress_p2p.py "http://127.0.0.1:5000"` to create the first peer.
* Run the above in another terminal to create the second peer.
* Copy paste/exchange the UUIDs between the terminals.
* Connection will be established and one of the peers will try to send packets to another peer.
* Fails at 40th packet. Each packet being 6.4 kB in size. (ie, breaks at 256 kB)
