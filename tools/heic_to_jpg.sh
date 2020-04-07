#!/usr/bin/bash

for f in "$@"
do
    echo "Working on file ${f}"
    name=$(echo ${f} | sed "s/^\(.*\)\.HEIC$/\1/g")
    heif-convert "${f}" "${name}.jpg"
done
