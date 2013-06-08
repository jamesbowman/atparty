python prep.py assets/*.jpg || exit

SKETCH=$HOME/sketchbook/atparty
mkdir -p $SKETCH
cp atparty.cpp $SKETCH/atparty.ino

make -C ../build/atparty &&
../build/atparty/gdatparty
