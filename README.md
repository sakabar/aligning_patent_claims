# aligning_patent_claims

## 構成
shell/aligning_patent_claims.sh 前処理
src/preprocessing_annotated_patent_data.py 前処理
src/preprocessing_similarity.py 類似度に関する情報をあらかじめファイルに出力
src/align_with_sim.py preprocessing_similarity.pyで出力した類似度を読み込み、類似度による手法を行う。類似度ファイルは特許IDに関してソートされていると仮定。(請求項IDや詳細説明IDはソートされていなくてよい)

## 既知の不具合
98003851.csvなどから請求項がうまく取れていない。
98012137などから取得した詳細説明が足りない? (idがいきなり70番台に飛んでいる)
