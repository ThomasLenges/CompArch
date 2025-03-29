#!/bin/bash

for tnum in ./given_tests/*
do
    cat ${tnum}/desc.txt
    printf "\n"
    python3 ./compare.py ${tnum}/user_output.json -r ${tnum}/output.json
done
