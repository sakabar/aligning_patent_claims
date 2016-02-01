import sys
import utils

#patent_idの一覧を標準入力から読み込む
def main():
    similarity_file_path = '/home/lr/tsakaki/work/aligning_patent_claims/list/similarity_list.txt'
    similarity_dic = utils.get_similarity_dic(similarity_file_path)

    for patent_id in sys.stdin:
        patent_id = patent_id.rstrip()

        result_dir = "/home/lr/tsakaki/work/aligning_patent_claims/result"
        claims = utils.get_claim_dic(result_dir + "/" + patent_id + ".claim.num.txt.wakati")
        details = utils.get_detail_dic(result_dir + "/" + patent_id + ".detail.txt.wakati.tags")

        for detail_ind, tpl in enumerate(details):
            detail_wakati_lst = tpl[0]
            tags = tpl[1]
            gold_answers = set([tag[:-1] for tag in tags if len(tag) > 0 and (tag[-1] == 'A' or tag[-1] == 'B')]) #このgold_answersはあるdetailに関するgold_answers。データ全体に関するものではない。

            for claim_id, claim_wakati_lst in claims.items():
                key = (patent_id, detail_ind, claim_id)

                rouge_sim = similarity_dic[key][0]
                dp_match_sim = similarity_dic[key][1]
                dp_mod_sim = similarity_dic[key][2]
                

                vec_str = "1:%f 2:%f 3:%f" % (rouge_sim, dp_match_sim, dp_mod_sim)
                if claim_id in gold_answers:
                    print("1 " + vec_str)
                else:
                    print("-1 " + vec_str)


    return








if __name__ == '__main__':
    main()
