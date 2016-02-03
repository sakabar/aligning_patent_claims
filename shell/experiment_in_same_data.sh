#!/bin/zsh
#同一のデータに関して、複数の素性を用いて実験を行い、比較する

set -ue

# #前処理
# shell/preprocessing.sh

#LDA
# shell/mallet_setup.sh


function output_topic_feature(){
    NUM_TOPICS=$1
    NUM_ITER=$2

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
}

#類似度、キーワード、トピックの素性を出力
output_topic_feature 10 30000 &
output_topic_feature 50 30000 &
output_topic_feature 100 30000 &
echo -n "feature output..." >&2
wait
echo "done." >&2

#負例を正例の3倍だけサンプリング
#FIXME ベタ打ち
TMPFILE=`mktemp`
pos_sample_num=`cat feature/proposed_method/sim_and_keywords_and_topic/t_10/i_30000/pos_sample.feature | grep -c ""`

paste -d '\t' feature/proposed_method/sim_and_keywords_and_topic/t_10/i_30000/neg_sample.feature feature/proposed_method/sim_and_keywords_and_topic/t_50/i_30000/neg_sample.feature feature/proposed_method/sim_and_keywords_and_topic/t_100/i_30000/neg_sample.feature | sort -R | head -n $[$pos_sample_num * 3] > $TMPFILE
cat $TMPFILE | awk -F'\t' '{print $1}' > feature/proposed_method/sim_and_keywords_and_topic/t_10/i_30000/neg_sample_extracted.feature
cat $TMPFILE | awk -F'\t' '{print $2}' > feature/proposed_method/sim_and_keywords_and_topic/t_50/i_30000/neg_sample_extracted.feature
cat $TMPFILE | awk -F'\t' '{print $3}' > feature/proposed_method/sim_and_keywords_and_topic/t_100/i_30000/neg_sample_extracted.feature

cat feature/proposed_method/sim_and_keywords_and_topic/t_10/i_30000/pos_sample.feature feature/proposed_method/sim_and_keywords_and_topic/t_10/i_30000/neg_sample_extracted.feature > feature/proposed_method/sim_and_keywords_and_topic/t_10/i_30000/sample.feature

cat feature/proposed_method/sim_and_keywords_and_topic/t_50/i_30000/pos_sample.feature feature/proposed_method/sim_and_keywords_and_topic/t_50/i_30000/neg_sample_extracted.feature > feature/proposed_method/sim_and_keywords_and_topic/t_50/i_30000/sample.feature

cat feature/proposed_method/sim_and_keywords_and_topic/t_100/i_30000/pos_sample.feature feature/proposed_method/sim_and_keywords_and_topic/t_100/i_30000/neg_sample_extracted.feature > feature/proposed_method/sim_and_keywords_and_topic/t_100/i_30000/sample.feature

#学習
svm-train -v 4 -h 0 feature/proposed_method/sim_and_keywords_and_topic/t_10/i_30000/sample.feature > feature/proposed_method/sim_and_keywords_and_topic/t_10/i_30000/result.txt &
svm-train -v 4 -h 0 feature/proposed_method/sim_and_keywords_and_topic/t_50/i_30000/sample.feature > feature/proposed_method/sim_and_keywords_and_topic/t_50/i_30000/result.txt &
svm-train -v 4 -h 0 feature/proposed_method/sim_and_keywords_and_topic/t_100/i_30000/sample.feature > feature/proposed_method/sim_and_keywords_and_topic/t_100/i_30000/result.txt &

#類似度の部分だけ抜き出して実験
cat feature/proposed_method/sim_and_keywords_and_topic/t_10/i_30000/sample.feature | cut -d ' ' -f1-4 > feature/previous_method/sim_only/sample.feature
svm-train -v 4 -h 0 feature/previous_method/sim_only/sample.feature > feature/previous_method/sim_only/result.txt &

#類似度とキーワードの部分だけ抜き出して実験
cat feature/proposed_method/sim_and_keywords_and_topic/t_10/i_30000/sample.feature | cut -d ' ' -f1-24 > feature/previous_method/sim_and_keywords/sample.feature
svm-train -v 4 -h 0 feature/previous_method/sim_and_keywords/sample.feature > feature/previous_method/sim_and_keywords/result.txt &

echo -n "evaluating..." >&2
wait
echo "done." >&2
