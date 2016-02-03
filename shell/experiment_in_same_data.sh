#!/bin/bash
#同一のデータに関して、複数の素性を用いて実験を行い、比較する

set -ue

# #前処理
# shell/preprocessing.sh

#LDA
shell/mallet_setup.sh

shell/run_mallet.sh 10 30000 &
shell/run_mallet.sh 50 30000 &
shell/run_mallet.sh 100 30000 &
wait

#類似度、キーワード、トピックの素性で実験
./shell/align_with_ml_topic.sh 10 30000
./shell/align_with_ml_topic.sh 50 30000
./shell/align_with_ml_topic.sh 100 30000

#類似度の部分だけ抜き出して実験
CROSS_NUM=4
cat feature/proposed_method/sim_and_keywords_and_topic/t_10/i_30000/sample.feature | cut -d ' ' -f1-4 > feature/previous_method/sim_only/sample.feature
svm-train -v $CROSS_NUM -h 0 feature/previous_method/sim_only/sample.feature > feature/previous_method/sim_only/result.txt

#類似度とキーワードの部分だけ抜き出して実験
cat feature/proposed_method/sim_and_keywords_and_topic/t_10/i_30000/sample.feature | cut -d ' ' -f1-24 > feature/previous_method/sim_and_keywords/sample.feature
svm-train -v $CROSS_NUM -h 0 feature/previous_method/sim_and_keywords/sample.feature > feature/previous_method/sim_and_keywords/result.txt
