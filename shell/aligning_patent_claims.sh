#!/bin/bash

set -ue

function preprocessing_annotated_patent_data(){
    d=/home/lr/tsakaki/corpus/DTECH-TAGGING/labeled_csv
    for csv_path in $d"/"*.csv; do
	bname=${csv_path##*/}
	fname=${bname%.*}


	#請求項の抽出
	cl_result=result/$fname".claim"
	python3 src/preprocessing_annotated_patent_data.py --claim  $csv_path > $cl_result
	cut -d $'\t' -f1  $cl_result > $cl_result".num"
	cut -d $'\t' -f2  $cl_result | tee $cl_result".txt" | mecab -b 10000 -O wakati > $cl_result".txt.wakati"

	paste -d '\t' $cl_result".num" $cl_result".txt.wakati" > $cl_result".num.txt.wakati"

	#詳細説明の抽出
	dt_result=result/$fname".detail"
	python3 src/preprocessing_annotated_patent_data.py --detail $csv_path > $dt_result
	cut -d $'\t' -f1  $dt_result | nkf -Z0 | sed -e 's/<[^>]\+>//g' | tee $dt_result".txt" | mecab -b 10000 -O wakati > $dt_result".txt.wakati"
	cut -d $'\t' -f2- $dt_result > $dt_result".tags"

	paste -d '\t' $dt_result".txt.wakati" $dt_result".tags" > $dt_result".txt.wakati.tags"
    done
}

preprocessing_annotated_patent_data
list_dir=list
cat $list_dir/patent_id_list.txt | python3 src/preprocessing_similarity.py > $list_dir/similarity_list.txt
#exit 0

