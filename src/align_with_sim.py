"""Align With Sim

Usage: align_with_sim.py --rouge
       align_with_sim.py [-h | --help]

Options:
    -h --help   show this help message and exit
    --rouge     calc similarity with ROUGE-2
"""

import sys

#整数と文字列のリストを引数として、n-gramのリストを返す
#つまり、文字列のリストのリストを返す
def get_ngram(n, words):
    lst = ["<s>"]
    lst.extend(words)
    lst.append("</s>")
    return [tuple(lst[k:k+n]) for k in range(len(lst)-n+1)]

#整数と文字列のリストを2つ引数として、rouge-nの値を返す
def rouge(n, ref_words, sys_words):
    ref_ngram_set = set(get_ngram(n, ref_words))
    sys_ngram_set = set(get_ngram(n, sys_words))
    inter_set = ref_ngram_set.intersection(sys_ngram_set)
    return 1.0 * len(inter_set) / len(ref_ngram_set)


#類似度の閾値を引数として実行する
def execute_with_sim_th(sim_th, patent_ids):
    result_dir = "/home/lr/tsakaki/work/aligning_patent_claims/result"
    true_pos = 0
    false_pos = 0
    false_neg = 0

    for patent_id in patent_ids:
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
                rouge2_cl_dt = rouge(2, claim_wakati_lst, detail_wakati_lst)
                lst.append((claim_id, rouge2_cl_dt))

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
    answers = [execute_with_sim_th(i / 10.0, patent_ids) for i in range(10)]
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

if __name__ == '__main__':
    main()
