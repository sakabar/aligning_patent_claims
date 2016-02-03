#!/bin/bash

#!/bin/zsh

set -ue

if [ $# != 2 ]; then
    echo "Argument error" >&2
    exit 1
fi

NUM_TOPICS=$1
NUM_ITER=$2

#類似度に加えて手掛かり語の素性とトピックを加えて評価
function sim_and_keywords_and_topic(){
    CROSS_NUM=$1
    SIM_AND_KEYWORDS_AND_TOPIC_DIR=feature/proposed_method/sim_and_keywords_and_topic/t_$NUM_TOPICS/i_$NUM_ITER
    if [ -e $SIM_AND_KEYWORDS_AND_TOPIC_DIR/result.txt ]; then
	echo "The result file already exists" >&2
        # exit 1
    fi

MALLET_RESULT_DIR=/home/lr/tsakaki/work/aligning_patent_claims/mallet_dir/result/t_$NUM_TOPICS/i_$NUM_ITER
    if [ ! -e $MALLET_RESULT_DIR ]; then
	echo "The result of mallet doesn't exists. Execute as follows at first" >&2
	echo "./shell/run_mallet $NUM_TOPICS $NUM_ITER" >&2
	exit 1
    fi

    mkdir -p $SIM_AND_KEYWORDS_AND_TOPIC_DIR

    cat list/patent_id_list.txt | python3 src/output_feature.py --keywords --topic -t $NUM_TOPICS -i $NUM_ITER > $SIM_AND_KEYWORDS_AND_TOPIC_DIR/all.feature
    cat $SIM_AND_KEYWORDS_AND_TOPIC_DIR/all.feature | grep "^1 " > $SIM_AND_KEYWORDS_AND_TOPIC_DIR/pos_sample.feature
    cat $SIM_AND_KEYWORDS_AND_TOPIC_DIR/all.feature | grep "^-1 " > $SIM_AND_KEYWORDS_AND_TOPIC_DIR/neg_sample.feature

    #正例の3倍だけ、負例をサンプリング
    pos_sample_num=`cat $SIM_AND_KEYWORDS_AND_TOPIC_DIR/pos_sample.feature | grep -c ""`
    sort -R $SIM_AND_KEYWORDS_AND_TOPIC_DIR/neg_sample.feature | head -n $[$pos_sample_num * 3] > $SIM_AND_KEYWORDS_AND_TOPIC_DIR/neg_sample_extracted.feature
    cat $SIM_AND_KEYWORDS_AND_TOPIC_DIR/pos_sample.feature \
        $SIM_AND_KEYWORDS_AND_TOPIC_DIR/neg_sample_extracted.feature > $SIM_AND_KEYWORDS_AND_TOPIC_DIR/sample.feature

    #学習
    svm-train -v $CROSS_NUM -h 0 $SIM_AND_KEYWORDS_AND_TOPIC_DIR/sample.feature > $SIM_AND_KEYWORDS_AND_TOPIC_DIR/result.txt
}

CROSS_NUM=4
sim_and_keywords_and_topic $CROSS_NUM &
wait
