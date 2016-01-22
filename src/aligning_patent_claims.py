import csv
#pandasをインストールしようとしたけど失敗。
from enum import Enum
import sys
import re
import os.path #あまり使いたくないけど…

class ReadArea(Enum):
    start = 1
    claim = 2
    detail = 3

def main2(csv_path):
    detail_regex = re.compile('^【[0-9０１２３４５６７８９]+】') #ここはわざと全角にしている。全角の0から9がハイフンで省略できるか分からないため、愚直に書いている

    with open(csv_path, 'r') as f:
        readArea = ReadArea.start
        claims = {} #請求項に関する情報を記憶する辞書
        details = [] #詳細説明に関する情報を記憶する配列

        reader = csv.reader(f)
        header = next(reader) #1行目は特許そのものに関する情報。

        for csv_line_obj in reader:
            if csv_line_obj[0] == '【特許請求の範囲】':
                readArea = ReadArea.claim
            elif csv_line_obj[0] == '【発明の詳細な説明】':
                readArea = ReadArea.detail

            #請求項に関する行→情報をclaimsに記憶
            if (readArea == ReadArea.claim):
                if (len(csv_line_obj) == 2 and len(csv_line_obj[1]) > 0):
                    st = csv_line_obj[0]
                    num = int(csv_line_obj[1])
                    if num in claims:
                        claims[num] += st
                    else:
                        claims[num] = st

            #詳細説明に関する行→どうしようかね。
            elif (readArea == ReadArea.detail):
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


def main():
    #アノテート結果のCSVファイル(未加工)を標準入力から読み込む
    #すなわち、中に入っている文字は全角英数やHTMLタグ(下付き<SB>など)が残っている
    #加工しないまま扱っているのは、全角ダブルクォーテーションがCSVの値に入っているためである。

    #コマンドライン引数で読み込むCSVファイルをフルパスで指定する
    if(len(sys.argv) != 2):
        raise Exception("ArgumentError: it needs only one argument")
   
    csv_path = sys.argv[1]
    if (not os.path.exists(csv_path)):
        raise Exception("ArgumentError: The csv file dosn't exists")

    main2(csv_path)
    return

if __name__ == '__main__':
    main()
