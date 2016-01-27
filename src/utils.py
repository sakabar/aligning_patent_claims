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
