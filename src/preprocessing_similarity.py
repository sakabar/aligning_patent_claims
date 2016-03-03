"""Preprocessing Similarity

Usage: preprocessing_similarity.py [-h | --help]

Options:
    -h --help   show this help message and exit
"""

from docopt import docopt
from enum import Enum
import utils
import math
import sys

sys.setrecursionlimit(10000) #再帰の回数を指定(デフォルトは1000)

def main():
    result_dir = "/home/lr/tsakaki/work/aligning_patent_claims/result"

    for patent_id in sys.stdin:
        patent_id = patent_id.rstrip()
        claims = utils.get_claim_dic(result_dir + "/" + patent_id + ".claim.num.txt.wakati")
        details = utils.get_detail_dic(result_dir + "/" + patent_id + ".detail.txt.wakati.tags")

        for detail_ind, tpl in enumerate(details):
            detail_wakati_lst = tpl[0]
            tags = tpl[1]
            for claim_id, claim_wakati_lst in claims.items():
                output_similarities(patent_id, detail_ind, claim_id, claim_wakati_lst, detail_wakati_lst)
    return

#整数と文字列のリストを引数として、n-gramのリストを返す
#つまり、文字列のリストのリストを返す
def get_ngram(n, words):
    lst = ["<s>"]
    lst.extend(words)
    lst.append("</s>")
    return [tuple(lst[k:k+n]) for k in range(len(lst)-n+1)]

#整数と文字列のリストを2つ引数として、rouge-nの値を返す
def calc_rouge(n, ref_words, sys_words):
    ref_ngram_set = set(get_ngram(n, ref_words))
    sys_ngram_set = set(get_ngram(n, sys_words))
    inter_set = ref_ngram_set.intersection(sys_ngram_set)
    return 1.0 * len(inter_set) / len(ref_ngram_set)

def output_similarities(patent_id, detail_ind, claim_id, claim_wakati_lst, detail_wakati_lst):
    rouge = calc_rouge(2, claim_wakati_lst, detail_wakati_lst) #claim, detailの順に注意。逆にすると結果が変わる
    dp_sim_tpl = calc_dp_matching_sim_and_dp_mod_sim(claim_wakati_lst, detail_wakati_lst)
    print("%s\t%d\t%s\t%f\t%f\t%f" % (patent_id, detail_ind, claim_id, rouge, dp_sim_tpl[0], dp_sim_tpl[1]))

#列挙型
class Direction(Enum):
    start = 0
    up = 1
    left = 2
    diag = 3

#r_num * c_numの行列を初期化
#direct
def init_direction_arr(r_num, c_num):
    return [[Direction.start for i in range(c_num)] for j in range(r_num)]

#lst0とlst1の間でマッチング
#FIXME これ、グローバルマッチングかな?
def dp_matching(lst0, lst1):
    score_arr = utils.init_arr(len(lst0), len(lst1))

    char_pena = -3 # 字が合わないときのペナルティ
    shift_pena = -1 #上下にズレるときのペナルティ
    from_arr = init_direction_arr(len(lst0), len(lst1))

    #まず0行目を埋める
    score_arr[0][0] = 0 if lst0[0] == lst1[0] else char_pena
    for j in range(1, len(lst1)):
        score_arr[0][j] = score_arr[0][j-1] + shift_pena #シフト
        score_arr[0][j] += 0 if lst0[0] == lst1[j] else char_pena #文字ペナ
        from_arr[0][j] = Direction.left

    #次に0列目を埋める
    for i in range(1, len(lst0)):
        score_arr[i][0] = score_arr[i-1][0] + shift_pena #シフト
        score_arr[i][0] += 0 if lst0[i] == lst1[0] else char_pena #文字ペナ
        from_arr[i][0] = Direction.up

    #残りを埋める
    for i in range(1, len(lst0)):
        for j in range(1, len(lst1)):
            a = score_arr[i][j-1] + shift_pena
            b = score_arr[i-1][j] + shift_pena
            c = score_arr[i-1][j-1] + (0 if lst0[i] == lst1[j] else char_pena) #文字ペナ
            max_score = max(a,b,c)
            score_arr[i][j] = max_score
            if a == max_score:
                from_arr[i][j] = Direction.left
            if b == max_score:
                from_arr[i][j] = Direction.up
            if c == max_score:
                from_arr[i][j] = Direction.diag #diagが最も優先される

    return (score_arr, from_arr)

#(0,0)から(row, col)までのポインタのリストを返す
#末尾再帰で書き直した
def get_ptrs(from_arr, row, col, acc):
    if row == 0 and col == 0:
        return [from_arr[0][0]] + acc
    else:
        if from_arr[row][col] == Direction.up:
            return get_ptrs(from_arr, row-1, col, [Direction.up] + acc)
        elif from_arr[row][col] == Direction.left:
            return get_ptrs(from_arr, row, col-1, [Direction.left] + acc)
        elif from_arr[row][col] == Direction.diag:
            return get_ptrs(from_arr, row-1, col-1, [Direction.diag] + acc)

def calc_dp_matching_sim_and_dp_mod_sim(lst0, lst1):
    score_arr, from_arr = dp_matching(lst0, lst1)
    len_row = len(lst0)
    len_col = len(lst1)

    ptr_lst = get_ptrs(from_arr, len_row-1, len_col-1, [])
    match = [ptr for ptr in ptr_lst if ptr == Direction.diag]

    dp_match_sim = 1.0 * len(match) / math.sqrt(len_col * len_row)
    dp_mod_sim = 1.0 * len(match) / min(len(lst0), len(lst1))

    return (dp_match_sim, dp_mod_sim)

if __name__ == '__main__':
    main()
