
    
def main():
    mean_vec_dic = get_word2vec()
    claims = utils.get_claim_dic(result_dir + "/" + patent_id + ".claim.num.txt.wakati")
    details = utils.get_detail_dic(result_dir + "/" + patent_id + ".detail.txt.wakati.tags")



    return

if __name__ == '__main__':
    main()
