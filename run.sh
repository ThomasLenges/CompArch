#!/bin/bash

INPUT=$1
OUTPUT=$2

echo "Running simulator: $INPUT → $OUTPUT"
python3 src/simulator.py "$INPUT" "$OUTPUT"

