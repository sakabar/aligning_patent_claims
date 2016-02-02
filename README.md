# aligning_patent_claims

#準備?
libsvm バージョン調べる
Precision, Recall, F-measureを出すパッチを当てる
mallet


## 構成
shell/aligning_patent_claims.sh 前処理
src/preprocessing_annotated_patent_data.py 前処理
src/preprocessing_similarity.py 類似度に関する情報をあらかじめファイルに出力
src/align_with_sim.py preprocessing_similarity.pyで出力した類似度を読み込み、類似度による手法を行う。類似度ファイルは特許IDに関してソートされていると仮定。(請求項IDや詳細説明IDはソートされていなくてよい)

shell/align_with_ml.sh 機械学習による分類
src/output_feature_by_previous_method.py

## 既知の不具合
98003851から詳細説明のtag(正解データなど)が読み込めていない?→たぶん大丈夫
98006528のtagに入っているのセミコロンって何?

## malletについて
これからシェルを書く →やった

## あとやること
mecabの単語分割時に原形に戻すのを忘れていた
それと、featureを加えていくのは同じ実験データでやらないと差が分からないでしょ。
→ そうすると、どうすればいいかというと、以下の2つの方法が考えられる
1 全ての素性を含むデータを作って、そこから一部分の列(素性)を抜き出して実験する
2 まず「請求項-素性」のペアの中からサンプリングして、そのデータに対して実験する


## 実行時間メモ
./shell/run_mallet.sh 20 30000  4418.58s user 3.72s system 101% cpu 1:12:49.27 total
./shell/run_mallet.sh 10 30000  4135.58s user 3.80s system 100% cpu 1:08:24.90 total
