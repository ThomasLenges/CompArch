#!/bin/bash

./build.sh

for tnum in ./given_tests/*
do
    ./run.sh ${tnum}/input.json ${tnum}/user_output.json
done
