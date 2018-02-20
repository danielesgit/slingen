#!/bin/bash

set -e

source envvar.sh

if [ -z $PYTHON2BIN ] || [ -z $PYTHON3BIN ] || [ -z $PYTHON2INC ]; then
  echo "Please fill in \$PYTHON2BIN, \$PYTHON3BIN, \$PYTHON2INC (and \$PYTHON2LIB if needed) in envvar.sh. Aborting."
  exit 1
fi

mkdir -p compileroot
mkdir -p libs
mkdir -p output

rm -rf py27env
rm -rf py35env
virtualenv -p $PYTHON2BIN py27env
virtualenv -p $PYTHON3BIN py35env
source py27env/bin/activate
pip install -U setuptools
LC_ALL=C pip install numpy
pip install -r py2req.txt

rm -rf scloog
tar xzf scloog.tar.gz
cd scloog
./configure --prefix=$(readlink -f ../libs) --with-osl=bundled --with-isl=bundled
make clean
make -j $(grep -m 1 "^cpu cores" /proc/cpuinfo | grep -o "[0-9]*")
make install

cd ..
rm -rf boost_1_55_0
wget https://sourceforge.net/projects/boost/files/boost/1.55.0/boost_1_55_0.tar.gz/download -O boost.tar.gz
cd boost_1_55_0
./bootstrap.sh --prefix=$(readlink -f ../libs) --with-libraries=python --with-python=$PYTHON2BIN
./b2 install cxxflags="-I$PYTHON2INC"

cd ../slingen
g++ -c -fPIC sigmacloog.cpp -o sigmacloog.o -I$(readlink -f ../libs/include) -I"$PYTHON2INC"
g++ -shared -Wl,-soname,sigmacloog.so -o sigmacloog.so sigmacloog.o -lpython2.7 -L$(readlink -f ../libs/lib) -lboost_python -lcloog-isl -losl

deactivate

cd ..
source py35env/bin/activate
pip install -U setuptools
LC_ALL=C pip install numpy
pip install -r py3req.txt
deactivate

echo "Installation completed."

