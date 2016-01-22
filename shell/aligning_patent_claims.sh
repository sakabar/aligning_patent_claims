#!/bin/bash

set -ue

d=/home/lr/tsakaki/corpus/DTECH-TAGGING/labeled_csv
for csv_path in $d"/"*.csv; do
    bname=${csv_path##*/}
    fname=${bname%.*}
    python3 src/aligning_patent_claims.py $csv_path > result/$fname".result"
    cut -d $'\t' -f1 result/$fname".result" | nkf -Z0 | sed -e 's/<[^>]\+>//g' | tee result/$fname.detail | mecab -b 10000 -O wakati > result/$fname.wakati
    cut -d $'\t' -f2- result/$fname".result" > result/$fname.tags

    #exit 0
done
