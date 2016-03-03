#!/bin/zsh

set -ue

d='/home/lr/tsakaki/work/psv/analyze_result'
tmpdir='/home/lr/tsakaki/work/aligning_patent_claims/psv_tmp_dir'
resultdir='/home/lr/tsakaki/work/aligning_patent_claims/psv_result_dir'
claim_cabocha_dir='/home/lr/tsakaki/work/aligning_patent_claims/psv_claim_cabocha_dir'
detail_cabocha_dir='/home/lr/tsakaki/work/aligning_patent_claims/psv_detail_cabocha_dir'


for f in $d'/'**/*-2.csv; do
    patent_id=`echo $f:t:r | grep -o "^[0-9]*"`
    csplit $f '/^-/' '{*}' --prefix=$tmpdir"/"${patent_id}"_" --suffix='%03d.txt' >/dev/null
done

for f in $tmpdir/*.txt; do
  cat $f | nkf -w | nkf -Lu | grep -v "^-" | tr -d ',' > $resultdir/$f:t
#  rm -rf $f
done

rm -rf $resultdir/*_000.txt

for f in $resultdir/*.txt; do
    cat $f | mecab -b 10000 | cabocha -I1 -O2 > $claim_cabocha_dir/$f:t:r".cabocha"
done

for f in /home/lr/tsakaki/work/aligning_patent_claims/result/*.detail.txt; do
    patent_id=$f:t:r:r
    cat $f | sed -e 's/【[^】]*】//g' | mecab -b 10000 | cabocha -I1 -O2 > $detail_cabocha_dir/$patent_id".cabocha"
done
