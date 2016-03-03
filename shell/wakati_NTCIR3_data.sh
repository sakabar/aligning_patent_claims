#!/bin/zsh

set -ue

##解凍
# for f in /auto/local/data/corpora/NTCIR-3/patent/kkh/*.tar.gz ; do
#     tar xf $f -C /local/tsakaki/NTCIR3/
# done

for patent_literature_file in /local/tsakaki/NTCIR3/980*/**/*.txt; do
  lv $patent_literature_file | awk "/【特許請求の範囲】/,/【符号の説明】/"
done | sed -e 's/【[^】]*】//g' | sed -e 's/<BR>//g' | sed -e 's/<[^>]*>//g' | grep -v "^$" | mecab -b 100000 -F"%f[6] " -U"%m " -E"\n" > word2vec/out.txt

cat word2vec/input.txt.wakati word2vec/out.txt > word2vec/input2.txt.wakati

time word2vec -train word2vec/input2.txt.wakati -output word2vec/out.vec -size 300 -window 5 -threads 10 -binary 0






