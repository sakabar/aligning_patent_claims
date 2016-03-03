#!/bin/zsh

set -ue

#mallet_dir/input_doc_dir/内に配置された分かち書きのデータを使う
#先に準備しておこう

cat mallet_dir/input_doc_dir/*.wakati.* | sed -e 's/【[^】]*】//g' | sed -e 's/ \+/ /g' > word2vec/input.txt.wakati



#time word2vec -train word2vec/input.txt.wakati -output word2vec/out.bin -size 300 -window 5 -threads 4 -binary 1

