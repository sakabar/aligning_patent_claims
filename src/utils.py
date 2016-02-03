import os
import math

def get_claim_dic(file_path):
    claims = {}
    with open(file_path, 'r') as claim_f:
        for line in claim_f:
            line = line.rstrip()
            lst = line.split('\t')
            wakati_lst = lst[1].split(' ')
            if lst[0] in claims:
                raise Exception('key conflict error')
            else:
                claims[lst[0]] = wakati_lst
    return claims

def get_detail_dic(file_path):
    details = []
    with open(file_path, 'r') as detail_f:
        for line in detail_f:
            line = line.rstrip()
            lst = line.split('\t')
            wakati_lst = lst[0].split(' ')
            tags = lst[1:]
            tpl = (wakati_lst, tags)
            details.append(tpl)

    return details

#similarity_fileのパスを引数として、その中身を辞書として返す
def get_similarity_dic(file_path):
    similarity_dic = {}
    with open(file_path, 'r') as f:
        for line in f:
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
    return similarity_dic

#malletの実行結果を読み込んで辞書として返す
def get_mallet_result_dic(num_topics, num_iter):
    claim_topic_dic = {} #(patent_id, claim_id)をキーとして、「トピック番号をインデックスとして割合を値とするリスト」を返す辞書
    detail_topic_dic = {} #(patent_id, detail_ind)をキーとして、「トピック番号をインデックスとして割合を値とするリスト」を返す辞書

    mallet_dir_path = "/home/lr/tsakaki/work/aligning_patent_claims/mallet_dir/result/t_%d/i_%d" % (num_topics, num_iter)

    if(not os.path.exists(mallet_dir_path)):
        raise Exception("The result of mallet doesn't exists. Execute as follows at first\n./shell/run_mallet %d %d" % (num_topics, num_iter))

    with open(mallet_dir_path + '/doc-topics.txt', 'r') as f:
        for line in f:
            line = line.rstrip()
            if line[0] != '#':
                lst = line.split()
                doc_id = lst[0]
                doc_path=lst[1].replace("file:", "")

                topic_dist_lst = [0 for i in range(num_topics)] #トピック番号をインデックス、割合を値とするリスト
                for i in range(num_topics):
                    topic = int(lst[2*i + 2])
                    rate = float(lst[2*i + 3])
                    topic_dist_lst[topic] = rate


                _, p_tail = os.path.split(doc_path)
                p_basename, p_ext = os.path.splitext(p_tail)
                if ".claim." in doc_path:
                    claim_id = str(int(p_ext.replace('.', '')) + 1) #claim_idは0ではなく1から始まる
                    patent_id = p_basename.replace(".claim.txt.wakati", "")
                    key = (patent_id, claim_id)
                    if key in claim_topic_dic:
                        raise Exception('dup key error')
                    claim_topic_dic[key] = topic_dist_lst
                elif ".detail." in doc_path:
                    detail_ind = int(p_ext.replace('.', ''))
                    patent_id = p_basename.replace(".detail.txt.wakati", "")
                    key = (patent_id, detail_ind)
                    if key in detail_topic_dic:
                        raise Exception('dup key error')
                    detail_topic_dic[key] = topic_dist_lst
                else:
                    raise Exception('mallet_dir error : %s' % doc_path)
                
    return (claim_topic_dic, detail_topic_dic)


def dot_times(lst1, lst2):
    return sum([t[0] * t[1]  for t in zip(lst1, lst2)])

def vec_abs(lst):
    return math.sqrt(sum([i * i for i in lst]))

def cos_sim(lst1, lst2):
    if len(lst1) != len(lst2):
        raise Exception('Wrong length')

    return 1.0 * dot_times(lst1, lst2) / vec_abs(lst1) / vec_abs(lst2)
