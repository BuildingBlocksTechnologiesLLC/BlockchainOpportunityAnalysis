#!/bin/bash


for f in *_; do
    python3 checkJson.py $f
done
    
