#!/bin/zsh

set -ue

#交差検定用にデータを作る
CROSS_NUM=10

d=/home/lr/tsakaki/work/aligning_patent_claims/feature/proposed_method/sim_and_keywords_and_topic/t_100/i_30000/handmade
#$dにall.featureが格納されていて、これを分割する

grep "^1 " $d/all.feature > $d/pos_all.feature
grep "^-1 " $d/all.feature > $d/neg_all.feature

pos_num=`cat $d/pos_all.feature | grep -c ""`
pos_split_num=$[$pos_num / $CROSS_NUM + 1]

neg_num=`cat $d/neg_all.feature | grep -c ""`
neg_split_num=$[$neg_num / $CROSS_NUM + 1]

split -l $pos_split_num $d/pos_all.feature "$d/pos_" --numeric-suffixes=1 --suffix-length=2 &#
split -l $neg_split_num $d/neg_all.feature "$d/neg_" --numeric-suffixes=1 --suffix-length=2 &#
wait

for i in {01..$CROSS_NUM}; do
    line_num=`grep -c "" pos_$i`
    cat $d/neg_$i | sort -R | head -n $[$line_num * 3] > $d/neg_$i".sample" &#
done
wait

#まずtest
for i in {01..$CROSS_NUM}; do
   cat $d/pos_$i $d/neg_$i > $d/test_$i &#
done


#まずtrain
for i in {01..$CROSS_NUM}; do
{
    if [ $i -ge 2 ]; then
        for j in {01..$[$i - 1]}; do
            cat $d/pos_$j $d/neg_$j.sample
        done
    fi

    if [ $i -lt $CROSS_NUM ]; then
        for j in {`printf "%02d" $[$i+1]`..$CROSS_NUM}; do
            cat $d/pos_$j $d/neg_$j.sample
        done
    fi
} > $d/train_$i
done

for i in {01..$CROSS_NUM}; do
    svm-train -h 0 $d/train_$i &#
done
wait

for i in {01..$CROSS_NUM}; do
  svm-predict $d/test_$i $d/train_$i.model $d/predict_$i > /dev/null &#
done
wait

for i in {01..$CROSS_NUM}; do
  paste -d ' ' $d/predict_$i $d/test_$i | awk '
$1 == "1" && $2 == "1" {
  tp++
}

$1 == "1" && $2 == "-1" {
  fp++
}

$1 == "-1" && $2 == "1" {
  fn++
}

END{
  p = 1.0 * tp / (tp + fp)
  r = 1.0 * tp / (tp + fn)
  printf("Precision:%f (%d / %d)\n", p, tp, tp+fp)
  printf("Recall   :%f (%d / %d)\n", r, tp, tp+fn)
  printf("F-measure:%f\n",2.0 * p *r / (p+r))
}' > $d/eval_$i
done

cat $d/eval_* | grep "F-measure" | awk -F':' '{s += $2}; END{ans=s/NR; print ans}' > $d/eval_mean_f_measure
