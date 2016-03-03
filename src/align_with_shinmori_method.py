#新森らの手法を作ってアラインメント
import utils
import sys

def get_lst_of_S(patent_id):
    d = "/home/lr/tsakaki/work/aligning_patent_claims/psv_detail_cabocha_dir"
    file_path = d + '/' + patent_id + ".cabocha"
    return load_cabocha_file(patent_id, file_path)

def get_E(patent_id, claim_id):
    file_path = '/home/lr/tsakaki/work/aligning_patent_claims/psv_claim_cabocha_dir/' + patent_id + '_' + "{:03d}".format(int(claim_id)) + ".cabocha"
    return load_cabocha_file(patent_id, file_path)

def load_cabocha_file(patent_id, file_path):
    #形態素のリスト(mrphs) = 1つの文節
    #返すのはmrphsのリスト = chunks
    chunks = [] #[]
    with open(file_path, 'r') as detail_f:
        chunk_lst = []
        mrphs = []
        for line in detail_f:
            line = line.rstrip()
            if line[0] == '*':
                if mrphs != []:
                    chunk_lst.append("".join(mrphs))
                    mrphs = []
            elif line == "EOS":
                chunk_lst.append("".join(mrphs))
                mrphs = []

                chunks.append(chunk_lst)
                chunk_lst = []
            else:
                mrphs.append(line.split()[0])

    return chunks

def main():
    patent_id="98003851"
    claim_id = "1" 

    lst_of_S = get_lst_of_S(patent_id) #(対応付け対象文)のリスト:全ての詳細説明
    large_E = get_E(patent_id, claim_id) #対応付け対象要素の列
    score = 0
    
    for s in lst_of_S:
        for e in large_E[::-1]:
            print(e)
            print(s)
            sys.exit(1)

            # #2次元の表を作成しDPを行う
            dp_arr = utils.init_arr(len(), len(e))
        # []

    # # print(lst_of_S)
    # print(large_E)



    return


if __name__ == '__main__':
    main()
