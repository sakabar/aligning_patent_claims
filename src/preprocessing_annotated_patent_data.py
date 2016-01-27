"""Preprocessing Annotated Patent Data

Usage: preprocessing_annotated_patent_data.py (--claim | --detail) <csv_path>
       preprocessing_annotated_patent_data.py [-h | --help]



Options:
    -h --help   show this help message and exit
    --claim     output claim in <csv_path>
    --detail    output detail in <csv_path>
"""

import csv
from docopt import docopt
from enum import Enum
import os.path #あまり使いたくないけど…
import re
import sys


#列挙型
class ReadArea(Enum):
    start = 1
    claim = 2
    detail = 3

def main():
    args = docopt(__doc__)
    csv_path = args["<csv_path>"]

    if (not os.path.exists(csv_path)):
        raise Exception("ArgumentError: The csv file dosn't exists")

    if(args["--claim"]):
        output_claim(csv_path)
    elif(args["--detail"]):
        output_detail(csv_path)

    return

#アノテート結果のCSVファイル(未加工)を標準入力から読み込む
#すなわち、中に入っている文字は全角英数やHTMLタグ(下付き<SB>など)が残っている
#加工しないまま扱っているのは、全角ダブルクォーテーションがCSVの値に入っているためである。
def output_claim(csv_path):
    detail_regex = re.compile('^【[0-9０１２３４５６７８９]+】') #ここはわざと全角にしている。全角の0から9がハイフンで省略できるか分からないため、愚直に書いている

    with open(csv_path, 'r') as f:
        readArea = ReadArea.start
        claims = {} #請求項に関する情報を記憶する辞書
        # details = [] #詳細説明に関する情報を記憶する配列

        reader = csv.reader(f)
        header = next(reader) #1行目は特許そのものに関する情報。

        for csv_line_obj in reader:
            if csv_line_obj[0] == '【特許請求の範囲】':
                readArea = ReadArea.claim
            elif csv_line_obj[0] == '【発明の詳細な説明】':
                readArea = ReadArea.detail

            #請求項に関する行→情報をclaimsに記憶
            if (readArea == ReadArea.claim):
                if (len(csv_line_obj) >= 2 and len(csv_line_obj[1]) > 0):
                    st = csv_line_obj[0]
                    num = int(csv_line_obj[1])
                    if num in claims:
                        claims[num] += st
                    else:
                        claims[num] = st

        for num,st in claims.items():
            sys.stdout.write(str(num) + "\t")
            print(st.replace('\n', ''))

    return



#読み込むCSVの状態はoutput_claim()と同様
def output_detail(csv_path):
    detail_regex = re.compile('^【[0-9０１２３４５６７８９]+】') #ここはわざと全角にしている。全角の0から9がハイフンで省略できるか分からないため、愚直に書いている

    with open(csv_path, 'r') as f:
        readArea = ReadArea.start
        # claims = {} #請求項に関する情報を記憶する辞書
        details = [] #詳細説明に関する情報を記憶する配列

        reader = csv.reader(f)
        header = next(reader) #1行目は特許そのものに関する情報。

        for csv_line_obj in reader:
            if csv_line_obj[0] == '【特許請求の範囲】':
                readArea = ReadArea.claim
            elif csv_line_obj[0] == '【発明の詳細な説明】':
                readArea = ReadArea.detail

            #詳細説明に関する行→どうしようかね。
            if (readArea == ReadArea.detail):
                if(len(csv_line_obj) >= 2):
                    st = csv_line_obj[0]
                    match_obj = detail_regex.search(st)
                    if (match_obj): #アノテートされた行
                        st_removed_newline = st.replace('\n', '')
                        sys.stdout.write(st_removed_newline)
                        for i in range(1, len(csv_line_obj)):
                            sys.stdout.write("\t" + csv_line_obj[i])
                        print()

    return


if __name__ == '__main__':
    main()
