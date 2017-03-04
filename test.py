#AND_Query.py
from collections import defaultdict
"""
import collections as coll

documents=[['dog', 'deer', 'cat', 'mouse'], ['parrot', 'cat'], ['turtle', 'dog']]
index = {'dog': [0, 2], 'cat': [0, 1], 'parrot': [1], 'turtle': [2]};
def and_search1(documents, index, queries):
    doc_ids = set([doc_id for doc_id in index[queries[0]]])
    for query in queries[1:]:
        doc_ids = doc_ids & set([doc_id for doc_id in index[query]])
    return [documents[doc_id] for doc_id in doc_ids]
    
def and_search2(documents, index, queries):
    c = coll.Counter()
    for q in queries:
        c.update(index[q])
    return [documents[c.most_common()[0][0]]]

print (and_search1(documents, index, ['cat', 'dog']))
print (and_search2(documents, index, ['cat', 'dog']))
"""
"""
l = [(1,2,3), (4,5,6), (5,1,9)]
fn = sorted(l, key=lambda x:x[1])

for i in fn[:2]:
    print (i)
"""
"""
sum=0    
for x,y in zip([1, 2, 3], [1,2,3]):
    sum += x*y
print (sum)
"""
"""
l1 = ["a","b","c", "e", "f"]
l2 = ["c", "e", "f"]

for l in l2:
    l1.remove(l)
    
l1.remove("g")
print (l1)
"""
d = defaultdict(lambda:0)
l=[]

print (type(d))
print (type(l))