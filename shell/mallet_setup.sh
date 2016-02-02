#!/bin/bash

set -ue

MALLET_DIR=/home/lr/tsakaki/work/aligning_patent_claims/mallet_dir
MALLET_INPUT_DIR=$MALLET_DIR/input_doc_dir

#ファイルを一行ごとに分割して$MALLET_INPUT_DIRに格納
for f in result/*.claim.txt.wakati; do
    split -l 1 $f $MALLET_INPUT_DIR/${f##*/}"." --numeric-suffixes --suffix-length=4
done

for f in result/*.detail.txt.wakati; do
    split -l 1 $f $MALLET_INPUT_DIR/${f##*/}"." --numeric-suffixes --suffix-length=4
done

mallet import-dir --input $MALLET_INPUT_DIR \
                  --output $MALLET_DIR/topic-input.mallet \
                  --keep-sequence --remove-stopwords --token-regex '[\p{L}\p{M}]+'
