#!/bin/zsh

set -ue

#類似度のみ
function sim_only(){
    CROSS_NUM=$1
    SIM_ONLY_DIR=feature/previous_method/sim_only
    cat list/patent_id_list.txt| python3 src/output_feature_by_previous_method.py > $SIM_ONLY_DIR/all.feature
    cat $SIM_ONLY_DIR/all.feature | grep "^1 " > $SIM_ONLY_DIR/pos_sample.feature
    cat $SIM_ONLY_DIR/all.feature | grep "^-1 " > $SIM_ONLY_DIR/neg_sample.feature


    #正例の3倍だけ、負例をサンプリング
    pos_sample_num=`cat $SIM_ONLY_DIR/pos_sample.feature | grep -c ""`
    sort -R $SIM_ONLY_DIR/neg_sample.feature | head -n $[$pos_sample_num * 3] > $SIM_ONLY_DIR/neg_sample_extracted.feature
    cat $SIM_ONLY_DIR/pos_sample.feature \
        $SIM_ONLY_DIR/neg_sample_extracted.feature > $SIM_ONLY_DIR/sample.feature

    #学習
    svm-train -v $CROSS_NUM -h 0 $SIM_ONLY_DIR/sample.feature > $SIM_ONLY_DIR/result.txt
}

#類似度に加えて手掛かり語の素性を加えて評価
function sim_and_keywords(){
    CROSS_NUM=$1
    SIM_AND_KEYWORDS_DIR=feature/previous_method/sim_and_keywords
    cat list/patent_id_list.txt| python3 src/output_feature_by_previous_method.py --keywords > $SIM_AND_KEYWORDS_DIR/all.feature
    cat $SIM_AND_KEYWORDS_DIR/all.feature | grep "^1 " > $SIM_AND_KEYWORDS_DIR/pos_sample.feature
    cat $SIM_AND_KEYWORDS_DIR/all.feature | grep "^-1 " > $SIM_AND_KEYWORDS_DIR/neg_sample.feature


    #正例の3倍だけ、負例をサンプリング
    pos_sample_num=`cat $SIM_AND_KEYWORDS_DIR/pos_sample.feature | grep -c ""`
    sort -R $SIM_AND_KEYWORDS_DIR/neg_sample.feature | head -n $[$pos_sample_num * 3] > $SIM_AND_KEYWORDS_DIR/neg_sample_extracted.feature
    cat $SIM_AND_KEYWORDS_DIR/pos_sample.feature \
        $SIM_AND_KEYWORDS_DIR/neg_sample_extracted.feature > $SIM_AND_KEYWORDS_DIR/sample.feature

    #学習
    svm-train -v $CROSS_NUM -h 0 $SIM_AND_KEYWORDS_DIR/sample.feature > $SIM_AND_KEYWORDS_DIR/result.txt
}

CROSS_NUM=4
sim_only $CROSS_NUM
sim_and_keywords $CROSS_NUM
