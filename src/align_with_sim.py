"""Align With Sim

Usage: align_with_sim.py [-h | --help]
       align_with_sim.py [--debug]

Options:
    -h --help   show this help message and exit
    --debug     output information for debug
"""

from docopt import docopt
import utils
import sys

args = docopt(__doc__) #FIXME これがグローバルなのはちょっとまずい

#標準入力から、preprocessing_similarity.pyの出力を読み込む
#類似度の重みと閾値を動かして最適な値を見つけ、その値とその時のF値を出力
def main():
    similarity_dic = {}
    patent_ids = []
    for line in sys.stdin:
        line = line.rstrip()
        lst = line.split('\t')
        if(len(lst) != 6):
            raise Exception('Invalid similarity file')
        patent_id = lst[0]
        detail_ind = int(lst[1])
        claim_id = lst[2]
        rouge_sim = float(lst[3])
        dp_matching_sim = float(lst[4])
        dp_mod_sim = float(lst[5])
        similarity_dic[(patent_id, detail_ind, claim_id)] = (rouge_sim, dp_matching_sim, dp_mod_sim)

        if(len(patent_ids) == 0):
            patent_ids.append(patent_id)
        elif(patent_ids[-1] != patent_id):
            patent_ids.append(patent_id)


    #うまくいくのか?
    ans_lst = []
    for i in range(11):
        w0 = i / 10.0
        for j in range(11):
            w1 = j / 10.0
            w2 = 1.0 - w0 - w1
            if(w2 < 0 or 1.0 < w0 + w1 + w2):
                continue

            eval_tpl = (w0, w1, w2) + eval_with_weight_and_threshold(w0, w1, w2, patent_ids, similarity_dic)
            print(eval_tpl)
            ans_lst.append(eval_tpl)
    ans = sorted(ans_lst, key=lambda tpl:tpl[9])[-1] #9番目:F値
    print("#The final result is:")
    print(ans)

    return


#rougeの重み、dp_matchの重み、dp_modの重み、類似度の閾値を引数として、
#その時のtrue_pos, false_pos, false_negの組を返す
def eval_with_weight_and_threshold(rouge_weight, dp_match_weight, dp_mod_weight, patent_ids, similarity_dic):
    weight_sum = rouge_weight + dp_match_weight + dp_mod_weight
    rouge_weight_ = rouge_weight / weight_sum
    dp_match_weight_ = dp_match_weight / weight_sum
    dp_mod_weight_ = dp_mod_weight / weight_sum
    # assert rouge_weight_ + dp_match_weight_ + dp_mod_weight_ == 1.0, "weight values are not normalized"

    tmp_system_answers = [] #閾値によるフィルタリングをしていない状態の、システムの出力
    gold_answers_all = set() #全データに関するGold standard

    for patent_id in patent_ids:
        #あるdetailに対して、全てのclaimに関して類似度を計算、その中の最大値を返す
        result_dir = "/home/lr/tsakaki/work/aligning_patent_claims/result"
        claims = utils.get_claim_dic(result_dir + "/" + patent_id + ".claim.num.txt.wakati")
        details = utils.get_detail_dic(result_dir + "/" + patent_id + ".detail.txt.wakati.tags")

        for detail_ind, tpl in enumerate(details):
            detail_wakati_lst = tpl[0]
            tags = tpl[1]
            gold_answers = set([tag[:-1] for tag in tags if len(tag) > 0 and (tag[-1] == 'A' or tag[-1] == 'B')]) #このgold_answersはあるdetailに関するgold_answers。データ全体に関するものではない。

            #gold_answers_allにdetailごとの正解データを追加
            for gold_claim in gold_answers:
                tmp_tpl = (patent_id, detail_ind, gold_claim)
                gold_answers_all.add(tmp_tpl)

            for claim_id, claim_wakati_lst in claims.items():
                key = (patent_id, detail_ind, claim_id)
                sim = rouge_weight_ * similarity_dic[key][0] + dp_match_weight_ * similarity_dic[key][1] + dp_mod_weight_ * similarity_dic[key][2]
                assert 0 <= sim <= 1.0, "Invalid similarity"
                tmp_system_answers.append((patent_id, detail_ind, claim_id, sim, (claim_id in gold_answers)))

    ans_lst = []
    for i in range(10):
        sim_th = i / 10
        tp_set = set([ans_tpl[0:3] for ans_tpl in tmp_system_answers if ans_tpl[3] >= sim_th and ans_tpl[4]])
        true_pos = len(tp_set)
        false_pos = len([ans_tpl for ans_tpl in tmp_system_answers if ans_tpl[3] >= sim_th and (not ans_tpl[4])]) #不等号はイコールを含むことに注意
        fn_set = gold_answers_all.difference(tp_set)
        false_neg = len(fn_set)

        p, r, f = calc_prec_rec_f_measure(true_pos, false_pos, false_neg)
        ans_lst.append((sim_th, true_pos, false_pos, false_neg, p, r, f))

    return sorted(ans_lst, key=lambda tpl: tpl[6])[-1]

#PrecisionやRecallが0の場合はF値は算出できないが、
#この後に最大のF値のみを使うので0としておけばよい
def calc_prec_rec_f_measure(tp, fp, fn):
    p = 0.0
    r = (1.0 * tp / (tp + fn))
    
    if(tp+fp == 0):
        return (0.0, 0.0, 0.0)
    else:
        p = (1.0 * tp / (tp + fp))

    if(p != 0 and r != 0):
        f = (2.0 * p * r / (p + r))
        return (p, r, f)
    else:
        return (0.0, 0.0, 0.0)

if __name__ == '__main__':
    main()
