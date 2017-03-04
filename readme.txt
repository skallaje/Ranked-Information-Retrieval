I have Python 3.5.2 on my system. The follwoing are the commands I executed to run the tests.

>>> exec(open("index.py").read())
>>> i=index("")
>>> i.buildIndex()
>>> i.exact_query("KASHMIR BRITISH",10)
>>> i.inexact_query_cluster_pruning("KASHMIR BRITISH",10)
>>> i.inexact_query_champion("KASHMIR BRITISH",10)
>>> i.inexact_query_index_elimination("KASHMIR BRITISH",10)
>>> i.print_dict()
>>> i.print_doc()

Please note that there are around unique 20K terms that form my dictionary. 
Index building and cluster creation will take no more than 45 seconds in the worst case (25 seconds and 15seconds respectively). 
