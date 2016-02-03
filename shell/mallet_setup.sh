#!/bin/bash

set -ue

MALLET_DIR=mallet_dir
MALLET_INPUT_DIR=$MALLET_DIR/input_doc_dir

if [ ! -e $MALLET_INPUT_DIR ]; then
  mkdir -p $MALLET_INPUT_DIR
fi

#ファイルを一行ごとに分割して$MALLET_INPUT_DIRに格納
for f in result/*.claim.txt.wakati; do
    split -l 1 $f $MALLET_INPUT_DIR/${f##*/}"." --numeric-suffixes --suffix-length=4
done

for f in result/*.detail.txt.wakati; do
    split -l 1 $f $MALLET_INPUT_DIR/${f##*/}"." --numeric-suffixes --suffix-length=4
done

#--remove-stopwordsオプションを使うと英語のストップワードしか除外されない。
#--stoplist-fileオプションで明示的に指定する必要がある
mallet import-dir --input $MALLET_INPUT_DIR \
                  --output $MALLET_DIR/topic-input.mallet \
                  --keep-sequence --token-regex '[\p{L}\p{M}]+' \
                  --remove-stopwords --stoplist-file /home/lr/tsakaki/local/src/mallet-2.0.7/stoplists/jp.txt
