#!/bin/zsh

set -ue

CROSS_NUM=4

cat list/patent_id_list.txt| python3 src/output_feature_by_previous_method.py > feature/previous_method/all.feature
cat feature/previous_method/all.feature | grep "^1 " > feature/previous_method/pos_sample.feature
cat feature/previous_method/all.feature | grep "^-1 " > feature/previous_method/neg_sample.feature


#正例の3倍だけ、負例をサンプリング
pos_sample_num=`cat feature/previous_method/pos_sample.feature | grep -c ""`
sort -R feature/previous_method/neg_sample.feature | head -n $[$pos_sample_num * 3] > feature/previous_method/neg_sample_extracted.feature
cat feature/previous_method/pos_sample.feature \
    feature/previous_method/neg_sample_extracted.feature > feature/previous_method/sample.feature

#学習
svm-train -v $CROSS_NUM -h 0 feature/previous_method/sample.feature > feature/previous_method/result.txt
