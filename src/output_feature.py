"""Output Feature

Usage: output_feature.py [-h | --help]
       output_feature.py --keywords
       output_feature.py --keywords --topic -t <num_topics> -i <num_iter>

Options:
    -h, --help  show this help message and exit
    --keywords  類似度だけでなく、手掛かり語の情報も素性に加える
    --topic     類似度だけでなく、トピックの情報も素性に加える
"""

from docopt import docopt
import sys
import utils
import collections
import copy

#patent_idの一覧を標準入力から読み込む
def main():
    args = docopt(__doc__)

    similarity_file_path = '/home/lr/tsakaki/work/aligning_patent_claims/list/similarity_list.txt'
    similarity_dic = utils.get_similarity_dic(similarity_file_path)

    claim_topic_dic = {}
    detail_topic_dic = {}

    if(args["--topic"]):
        num_topics = int(args["<num_topics>"])
        num_iter = int(args["<num_iter>"])
        claim_topic_dic, detail_topic_dic = utils.get_mallet_result_dic(num_topics, num_iter)


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
                
                feature_lst = [] #素性値(float)を値とするリスト。このリストの0番目が素性番号1に対応するので、扱いに注意が必要。
                feature_lst.append(rouge_sim)
                feature_lst.append(dp_match_sim)
                feature_lst.append(dp_mod_sim)

                if(args["--keywords"]):
                    feature_lst = append_keyword_feature(feature_lst, detail_wakati_lst, claim_wakati_lst)

                if(args["--topic"]):
                    feature_lst = append_topic_feature(feature_lst, claim_topic_dic, detail_topic_dic, patent_id, claim_id, detail_ind)

                feature_str = get_feature_str(claim_id, gold_answers, feature_lst)
                print(feature_str)

    return

#素性リストに手がかり語に関する素性を加え、新しい素性リストを返す
def append_keyword_feature(feature_lst, detail_wakati_lst, claim_wakati_lst):
    ans = copy.deepcopy(feature_lst)
    keywords = ["特徴", "上記", "目的", "形成",
                "記載", "課題", "可能", "解決",
                "発明", "構成", "有する", "係る",
                "本発明", "防止", "配置", "実施",
                "請求項", "提供", "効果", "検出"]

    #TODO FIXME
    #請求項と詳細説明に出現する手掛かり語の頻度数を素性に加える
    counter_dic = collections.Counter(detail_wakati_lst + claim_wakati_lst)
    for keyword_ind,keyword in enumerate(keywords):
        cnt = counter_dic[keyword]
        ans.append(cnt)

    return ans

#素性リストとトピック数、イテレーション数を指定し、そのトピック数・イテレーション数で実行したmalletの結果を読み込んでなにやらする。
#素性リストにトピックに関する素性を加え、新しい素性リストを返す
#請求項に現れるトピックごとの出現率(長さ:トピック数)、正規化
#詳細説明に現れるトピックごとの出現率(長さ:トピック数)、正規化
#これらのベクトルのcos類似度
def append_topic_feature(feature_lst, claim_topic_dic, detail_topic_dic, patent_id, claim_id, detail_ind):
    ans = copy.deepcopy(feature_lst)

    claim_topic_dist = claim_topic_dic[(patent_id, claim_id)]
    detail_topic_dist = detail_topic_dic[(patent_id, detail_ind)]
    topic_sim = utils.cos_sim(claim_topic_dist, detail_topic_dist)

    ans.append(topic_sim)
    return ans






    return ans

def get_feature_str(claim_id, gold_answers, feature_lst):
    ans_lst = []
    if claim_id in gold_answers:
        ans_lst.append("1")
    else:
        ans_lst.append("-1")

    for feature_ind, feature_val in enumerate(feature_lst):
        ans_lst.append("%d:%f" % (feature_ind + 1, feature_val)) #この+1がポイント。素性番号は0ではなく1から始まる

    return " ".join(ans_lst)

if __name__ == '__main__':
    main()
