#!/usr/bin/env bash

LIB_SRC=./lib
LIB_TARGET=./tests/testLib

QUEUE_SRC=./tests/testData/queue
QUEUE_TARGET=./tests/testQueue

if $( test -d "$LIB_TARGET" ); then
    rm -rf "$LIB_TARGET"
fi

mkdir "$LIB_TARGET"
cp "$LIB_SRC"/* "$LIB_TARGET" -r
cp ./tests/testData/lib/* "$LIB_TARGET" -r


if $( test -d "$QUEUE_TARGET" ); then
    rm -rf "$QUEUE_TARGET"
fi

mkdir "$QUEUE_TARGET"
cp "$QUEUE_SRC"/* "$QUEUE_TARGET" -r

if $( test -d ./data.dat ); then
    rm ./data.dat
fi
