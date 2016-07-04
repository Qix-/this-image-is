#!/usr/bin/env bash
set -e
set -o pipefail

git submodule update --init --recursive

virtualenv env
. env/bin/activate

pip install -r requirements.txt

(yes | bash < ext/torch/install-deps) || echo An error occurred here\; bravely going forth.
(cd ext/torch && yes n | ./install.sh) || echo An error occurred here\; bravely going forth.
export PATH=`pwd`/ext/torch/install/bin:$PATH

mkdir -p env/build
(cd env/build && cmake ../../ext/nanomsg && cmake --build . && sudo cmake --build . --target install)

if ! command -v 'luarocks'; then
	if command -v 'brew'; then
		brew install luarocks protobuf hdf5 graphviz
	elif command -v 'apt'; then
		echo 'attempting to install deps; will require sudo'
		sudo apt-get -y install luarocks libprotobuf-dev protobuf-compiler graphviz libhdf5-dev
	else
		echo 'cannot automatically install deps; please install it and re-run' >&2
		exit 1
	fi
fi

luarocks install nn
luarocks install nngraph
luarocks install image
luarocks install loadcaffe
luarocks install hdf5

if [ ! -f env/snapshot.zip ]; then
	curl http://cs.stanford.edu/people/karpathy/neuraltalk2/checkpoint_v1_cpu.zip -o env/snapshot.zip
fi

if ! ls "env/*.t7"; then
	(cd env && unzip snapshot.zip)
fi
