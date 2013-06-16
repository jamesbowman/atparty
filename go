python prep.py assets/*.jpg || exit

# SKETCH=$HOME/sketchbook/atparty
# SKETCH=$HOME/Documents/Arduino/atparty
# mkdir -p $SKETCH
# cp atparty.cpp $SKETCH/atparty.ino
# cp sdcard.h $SKETCH/
# exit

make -C ../build/atparty &&
../build/atparty/gdatparty
# gdb -x x.gdb ../build/atparty/gdatparty
