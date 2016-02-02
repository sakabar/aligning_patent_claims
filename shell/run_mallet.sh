#!/bin/bash

#素性ファイルを出力して、LIBLINEARで分類
#

set -ue

if [ $# != 2 ]; then
    echo "Argument error" >&2
    exit 1
fi

MALLET_DIR=/home/lr/tsakaki/work/aligning_patent_claims/mallet_dir

NUM_TOPICS=$1
NUM_ITER=$2

RESULT_DIR=$MALLET_DIR/result/t_$NUM_TOPICS/i_$NUM_ITER
if [ -e $RESULT_DIR ]; then
  echo "The result dir already exists" >&2
  exit 1
fi
mkdir -p $RESULT_DIR

mallet train-topics \
  --input $MALLET_DIR/topic-input.mallet \
  --num-topics $NUM_TOPICS \
  --num-iterations $NUM_ITER \
  --output-state $RESULT_DIR/topic-state.gz \
  --output-topic-keys $RESULT_DIR/topic-keys.txt \
  --output-doc-topics $RESULT_DIR/doc-topics.txt

#topic-state.gzは、
#"0 /home/lr/tsakaki/work/aligning_patent_claims/mallet_dir/input_dir/99187900.claim.txt.wakati 27 5 に 7"
#このような出力
#doc-id doc-name word_ind word_id word topic
