## Build Instructions

### C source

For the C source in `./src/` folder, obtain the dependencies "OpenSSL" and "libnice (>= 0.1.8)"
On reasonably modern Ubuntu/Debian distros, this can be done by `sudo apt-get update && sudo apt-get install libnice-dev libssl-dev`

The other dependency is "usrsctp" that is bundled in this repo as a subtree.

Simply do `make` from `./src/` directory.

### Python bindings

* Install cython via your package manager OR create a virtualenv, activate it.

* From the `./python/` directory, do a `make`.

* `make test` after that to run example.py

