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
