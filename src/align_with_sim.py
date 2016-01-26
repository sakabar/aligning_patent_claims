"""Align With Sim

Usage: align_with_sim.py [--rouge] [--dpmatch] [--dpmod] [--debug]
       align_with_sim.py [-h | --help]

Options:
    -h --help   show this help message and exit
    --rouge     use ROUGE-2     similarity
    --dpmatch   use dp_matching similarity
    --dpmod     use dp_mod      similarity
    --debug     output information for debug
"""

from docopt import docopt
from enum import Enum
import math
import sys

args = docopt(__doc__) #FIXME これがグローバルなのはちょっとまずい

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

#類似度の閾値を引数として実行する
def execute_with_sim_th(sim_th, patent_ids):
    if(args["--debug"]):
        sys.stderr.write(str(sim_th) + '\n')

    result_dir = "/home/lr/tsakaki/work/aligning_patent_claims/result"
    true_pos = 0
    false_pos = 0
    false_neg = 0

    for patent_id in patent_ids:
        if(args["--debug"]):
            sys.stderr.write(str(patent_id) + '\n')

        claims = {}
        details = []

        with open(result_dir + "/" + patent_id + ".claim.num.txt.wakati", 'r') as claim_f:
            for line in claim_f:
                line = line.rstrip()
                lst = line.split('\t')
                wakati_lst = lst[1].split(' ')
                if lst[0] in claims:
                    raise Exception('key conflict error')
                else:
                    claims[lst[0]] = wakati_lst

        with open(result_dir + "/" + patent_id + ".detail.txt.wakati.tags", 'r') as detail_f:
            for line in detail_f:
                line = line.rstrip()
                lst = line.split('\t')
                wakati_lst = lst[0].split(' ')
                tags = lst[1:]
                tpl = (wakati_lst, tags)
                details.append(tpl)


        for ind, tpl in enumerate(details):
            detail_wakati_lst = tpl[0]
            tags = tpl[1]

            lst = []
            for claim_id, claim_wakati_lst in claims.items():
                sim = 1.0
                if(args["--rouge"]):
                    sim *= calc_rouge(2, claim_wakati_lst, detail_wakati_lst) #claim, detailの順に注意

                dp_sim_tpl = calc_dp_matching_sim_and_dp_mod_sim(claim_wakati_lst, detail_wakati_lst)
                
                if(args["--dpmatch"]):
                    # if(args["--debug"]):
                    #    sys.stderr.write("dpmatch\n")

                    sim *= dp_sim_tpl[0]
                if(args["--dpmod"]):
                    # if(args["--debug"]):
                    #    sys.stderr.write("dpmod\n")

                    sim *= dp_sim_tpl[1]

                lst.append((claim_id, sim))

            system_answers = set([tpl[0] for tpl in lst if tpl[1] >= sim_th]) #不等号はイコールを含むことに注意
            gold_answers = set([tag[:-1] for tag in tags if len(tag) > 0 and (tag[-1] == 'A' or tag[-1] == 'B')])

            tp = system_answers.intersection(gold_answers)
            fp = system_answers.difference(tp)
            fn = gold_answers.difference(tp)

            true_pos += len(tp)
            false_pos += len(fp)
            false_neg += len(fn)

    f_measure = calc_f_measure(true_pos, false_pos, false_neg)
    return (sim_th, f_measure)

def main():
    patent_ids = [line.rstrip() for line in sys.stdin.readlines()]
    answers = [execute_with_sim_th(i / 10.0, patent_ids) for i in range(0, 10)]
    sorted_ans = sorted(answers, key=lambda tpl: tpl[1])

    print(sorted_ans[-1])

    return

#PrecisionやRecallが0の場合はF値は算出できないが、
#この後に最大のF値のみを使うので0としておけばよい
def calc_f_measure(tp, fp, fn):
    p = 0.0
    r = (1.0 * tp / (tp + fn))
    
    if(tp+fp == 0):
        return 0.0
    else:
        p = (1.0 * tp / (tp + fp))

    if(p != 0 and r != 0):
        f = (2.0 * p * r / (p + r))
        return f
    else:
        return 0.0

# def output_f_measure(tp, fp, fn):
#     p = -1.0
#     if(tp+fp == 0):
#         print("Precision: NAN (0 / 0)")
#     else:
#         p = (1.0 * tp / (tp + fp))
#         print("Precision: %f (%d / %d)" % (p, tp, (tp+fp)))

#     r = (1.0 * tp / (tp + fn))
#     print("Recall   : %f (%d / %d)" % (r, tp, (tp+fn)))

#     if(p != 0 and r != 0):
#         f = (2.0 * p * r / (p + r))
#         print("F-measure: %f" % f)
#     else:
#         print("F-measure: NAN")



########## ここから dp_matching の話 ##########

#列挙型
class Direction(Enum):
    start = 0
    up = 1
    left = 2
    diag = 3


#r_num * c_numの行列を初期化
def init_arr(r_num, c_num):
    return [[0 for i in range(c_num)] for j in range(r_num)]

#r_num * c_numの行列を初期化
#direct
def init_direction_arr(r_num, c_num):
    return [[Direction.start for i in range(c_num)] for j in range(r_num)]

#lst0とlst1の間でマッチング
#FIXME これ、グローバルマッチングかな?
def dp_matching(lst0, lst1):
    score_arr = init_arr(len(lst0), len(lst1))

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
def get_ptrs(from_arr, row, col):
    if row == 0 and col == 0:
        return [from_arr[0][0]]
    else:
        if from_arr[row][col] == Direction.up:
            return get_ptrs(from_arr, row-1, col) + [from_arr[row][col]]
        elif from_arr[row][col] == Direction.left:
            return get_ptrs(from_arr, row, col-1) + [from_arr[row][col]]
        elif from_arr[row][col] == Direction.diag:
            return get_ptrs(from_arr, row-1, col-1) + [from_arr[row][col]]

# def calc_dp_matching_sim(lst0, lst1):
#     score_arr, from_arr = dp_matching(lst0, lst1)
#     len_row = len(lst0)
#     len_col = len(lst1)

#     ptr_lst = get_ptrs(from_arr, len_row-1, len_col-1)
#     match = [ptr for ptr in ptr_lst if ptr == Direction.diag]

#     return 1.0 * len(match) / math.sqrt(len_col * len_row)

# def calc_dp_mod_sim(lst0, lst1):
#     score_arr, from_arr = dp_matching(lst0, lst1)
#     len_row = len(lst0)
#     len_col = len(lst1)

#     ptr_lst = get_ptrs(from_arr, len_row-1, len_col-1)
#     match = [ptr for ptr in ptr_lst if ptr == Direction.diag]

#     return 1.0 * len(match) / min(len(lst0), len(lst1))
    


def calc_dp_matching_sim_and_dp_mod_sim(lst0, lst1):
    score_arr, from_arr = dp_matching(lst0, lst1)
    len_row = len(lst0)
    len_col = len(lst1)

    ptr_lst = get_ptrs(from_arr, len_row-1, len_col-1)
    match = [ptr for ptr in ptr_lst if ptr == Direction.diag]

    dp_match_ans = 1.0 * len(match) / math.sqrt(len_col * len_row)
    dp_mod_ans = 1.0 * len(match) / min(len(lst0), len(lst1))

    return (dp_match_ans, dp_mod_ans)


if __name__ == '__main__':
    main()
