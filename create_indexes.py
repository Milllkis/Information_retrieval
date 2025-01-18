from information_retrieval import InformationRetrieval

ir = InformationRetrieval('new_biographies.csv')

ir.index_tfidf()
ir.index_bert()