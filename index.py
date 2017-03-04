#Python 3.0
import re
import os
import collections
import math
import time
import zipfile
import random
from collections import defaultdict
from collections import Counter
from itertools import islice

class index:
    def __init__(self,path):
        self.path = path
        #Unzip the file using ZipFile API
        print ("Building Index...")
        print ("Building Champion Lists...")
        self.cl = defaultdict(list)
        zip_ref = zipfile.ZipFile("collection.zip", 'r')
        #unzip files
        if os.path.isdir("collection") is False:
            zip_ref.extractall("")
            zip_ref.close()
        self.d = defaultdict(set)
        self.d1 = defaultdict(list)
        self.docset = set()
        self.buildIndex()
        print ("Creating L2 Norm...")
        self.L2 = defaultdict(lambda:0)
        self.calculate_L2norm()
        print ("Creating Clusters...")
        self.leader_followers = defaultdict(list)
        self.create_clusters()        
        pass
        
    def remove_stop_words(self):
        #remove stop words from dictionary
        with open('stop-list.txt') as f:
            lines = f.read().splitlines()
        for line in lines:
            if line in self.d1:
                del self.d1[line]
                del self.cl[line]
        pass
        
    def create_clusters(self):
        start_time = time.time()
        leaders = set()
        lead_terms = []
        
        with open('stop-list.txt') as f:
            stopwords = f.read().splitlines()
        
        doc_lead = defaultdict(list)
        leader_followers = defaultdict(list)
        
        q = defaultdict(lambda:0)
        qtfidf = defaultdict(lambda:0)
        score = defaultdict(lambda:0)
        
        score = defaultdict(lambda:0)
        vect_len = defaultdict(lambda:0)
        length = defaultdict(lambda:0)
        cosine = defaultdict(lambda:0)
        
        #randomly select root N documents as leaders
        while True:
            leaders.add(random.choice(list(self.docset)))
            if len(leaders) > int(math.sqrt(len(self.docset))):
                break
        doc_lead = defaultdict(list)
        #for each file in the leaders list, compute cosine similarity between leader and it's followers
        for filename in leaders:
            f = open("collection/Text-"+str(filename)+".txt", "r")
            orig = str(f.read()).lower()
            tokens = re.split('\W+',orig.lower())
            tokens.pop(0)
            tokens.pop(len(tokens)-1)
            for word in tokens:
                if word not in stopwords:
                    lead_terms.append(word)
                        
            for term in lead_terms:
                q[term] = q[term]+1
            #dictionary to store tfidf value of leader
            for term in q:
                if term in self.d1:
                    qtfidf[term] = (1+math.log(q[term],10))*self.d1[term][0][0]
            for doc in self.docset:
                if filename != doc:
                    sumqterms = 0
                    for term in lead_terms:
                        sumqterms = sumqterms + math.pow(qtfidf[term],2)
                        if doc in self.d[term]:
                            for item in self.d1[term][0][1]:
                                if doc == item[0]:
                                    score[item[0]] = score[item[0]] + (item[1] * self.d1[term][0][0] * qtfidf[term])
                    x = math.sqrt(sumqterms)
                    #denominator part of cosine similarity
                    length[doc] = x * self.L2[doc]
                    cosine[doc] = score[doc]/length[doc]
                    tup = (filename, cosine[doc])
                    doc_lead[doc].append(tup)
            #clear the data structures so that they could be used for successive leaders and their cosine computations
            lead_terms.clear()
            q.clear()
            qtfidf.clear()
            score.clear()
            length.clear()
            cosine.clear()
        
        #assign leaders to documents
        for x in doc_lead:
            y = sorted(doc_lead[x], key=lambda x:-x[1])
            self.leader_followers[y[0][0]].append(x)
        print("--- Time taken to create clusters is %s seconds ---" % (time.time() - start_time))
        pass
        
    def buildIndex(self):
        #function to read documents from collection, tokenize and build the index with tokens
		# implement additional functionality to support methods 1 - 4
		#use unique document integer IDs
        z = zipfile.ZipFile("collection.zip", "r")
        start_time = time.time()
        for filename in z.namelist():
            if "-" in filename:
                orig = str(z.read(filename))
                tokens = re.split('\W+',orig.lower())
                tokens.pop(0)
                tokens.pop(len(tokens)-1)
                for word in tokens:
                    self.d[word].add(int(filename[filename.index("-")+1:filename.index(".")-len(filename)])) #initial dictionary created with terms and their posting lists
                    self.docset.add(int(filename[filename.index("-")+1:filename.index(".")-len(filename)])) #docIDs populated]
        
        #ignore the root path. Calculate the positions for each term only in the files that has the term.        
        for s1 in self.d.keys():
            idf_ml = []
            ml = []
            for filename in self.d[s1]:
                l=[]
                f = open("collection/Text-"+str(filename)+".txt", "r")
                orig = str(f.read()).lower()                    
                for m in re.finditer(s1, orig):
                    l.append(m.start())
                if len(l)!=0:
                    tup = (filename, 1+math.log(len(l),10), l)
                    ml.append(tup)
            idf_ml.append(math.log((len(self.docset)/len(self.d[s1])), 10))
            self.cl[s1]=list(islice(sorted(ml, key=lambda x: -x[1]),int(math.sqrt(len(self.docset)))))
            idf_ml.append(ml)
            self.d1[s1].append(idf_ml)            
        self.remove_stop_words()
        print("--- Time taken to build index is %s seconds ---" % (time.time() - start_time))
        pass
        
    def calculate_L2norm(self):
        q = defaultdict(lambda:0)
        for doc in self.docset:
            f = open("collection/Text-"+str(doc)+".txt", "r")
            orig = str(f.read()).lower()
            tokens = re.split('\W+',orig.lower())
            tokens.pop(0)
            tokens.pop(len(tokens)-1)
            for word in tokens:
                if word in self.d1:
                    q[word] = q[word]+1
            
            sum = 0
            for term in q:
                if term in self.d1:
                    sum = sum + math.pow(((1+math.log(q[term],10))*self.d1[term][0][0]),2)
            self.L2[doc] = math.sqrt(sum)
            q.clear()
                
    def exact_query(self, query_terms, k):
        #function for exact top K retrieval (method 1)
        #Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
        start_time = time.time()
        terms = re.split('\W+',query_terms.lower())
        q = defaultdict(lambda:0)
        qtfidf = defaultdict(lambda:0)
        score = defaultdict(lambda:0)
        vect_len = defaultdict(lambda:0)
        length = defaultdict(lambda:0)
        cosine = defaultdict(lambda:0)
        
        for term in terms:
            q[term] = q[term]+1
        
        #tfidf calculation for query
        for term in q:
            if term in self.d1:
                qtfidf[term] = (1+math.log(q[term],10))*self.d1[term][0][0]
        
        docs = set()
        
        #numerator part calculated for cosines
        for term in terms:
            if term in self.d1:
                for item in self.d1[term][0][1]:
                    score[item[0]] = score[item[0]] + (item[1] * self.d1[term][0][0] * qtfidf[term])
                    docs.add(item[0])
        
        sumqterms = 0
        for term in terms:
            sumqterms = sumqterms + math.pow(qtfidf[term],2)
        x = math.sqrt(sumqterms)
        
        #calculation of cosine        
        for d in docs:
            cosine[d] = score[d]/(x*self.L2[d])                        
        #print (cosine)
        
        topk = list(islice(sorted(cosine.items(), key=lambda x: -x[1]),k))
        
        for top in  topk:
            print ("Text-"+str(top[0])+".txt" +" "+str(top[1]))
        
        print("--- Time taken to process the query is %s seconds ---" % (time.time() - start_time))        
        pass
        
    def inexact_query_champion(self, query_terms, k):
        #function for exact top K retrieval using champion list (method 2)
        #Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
        start_time = time.time()
        terms = re.split('\W+',query_terms.lower())
        q = defaultdict(lambda:0)
        qtfidf = defaultdict(lambda:0)
        score = defaultdict(lambda:0)
        vect_len = defaultdict(lambda:0)
        length = defaultdict(lambda:0)
        cosine = defaultdict(lambda:0)
        
        for term in terms:
            q[term] = q[term]+1
        
        for term in q:
            if term in self.d1:
                qtfidf[term] = (1+math.log(q[term],10))*self.d1[term][0][0]
        
        docs = set()
        
        #sort documents with decreasing tfidfs
        for term in terms:
            if term in self.d1:
                for item in self.cl[term]:
                    score[item[0]] = score[item[0]] + (item[1] * self.d1[term][0][0] * qtfidf[term])
                    docs.add(item[0])
        
        sumqterms = 0
        for term in terms:
            sumqterms = sumqterms + math.pow(qtfidf[term],2)
        x = math.sqrt(sumqterms)
            
        for d in docs:
            cosine[d] = score[d]/(x*self.L2[d])                        
        
        topk = list(islice(sorted(cosine.items(), key=lambda x: -x[1]),k))
        
        for top in topk:
            print ("Text-"+str(top[0])+".txt" +" "+str(top[1]))
        
        print("--- Time taken to process the query is %s seconds ---" % (time.time() - start_time))
        pass
        
    def inexact_query_index_elimination(self, query_terms, k):
        #function for exact top K retrieval using index elimination (method 3)
        #Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
        start_time = time.time()
        terms = re.split('\W+',query_terms.lower())
        d = defaultdict(list)
        pl = set()
        for term in terms:
            if term in self.d1:
                d[term] = self.d1[term]
        
        #return list of terms with decreasing IDF values if number of query terms is greater than 1
        if len(d) > 1:
            dlen = int(len(d)/2)
            listlen = list(islice(sorted(d.items(), key=lambda x: x[0][0], reverse=True),dlen))
        else:
            listlen = list(islice(sorted(d.items(), key=lambda x: x[0][0], reverse=True),1))
        c = Counter()
        for l in listlen:
            count = 0
            sv = []
            for t in l:
                if count % 2 == 1:
                    v=[]
                    for ele in t[0][1]:
                        v.append(ele[0])
                    c.update(v)
                else:
                    sv.append(t)
                count=count+1  
                
        listv = c.most_common()
        for item in listv:
            if item[1] >= len(listlen):
                pl.add(item[0])
                
        ######################################################        
                
        #terms = query_terms.lower().split(" ")
        q = defaultdict(lambda:0)
        qtfidf = defaultdict(lambda:0)
        score = defaultdict(lambda:0)
        vect_len = defaultdict(lambda:0)
        length = defaultdict(lambda:0)
        cosine = defaultdict(lambda:0)
        
        for term in sv:
            q[term] = q[term]+1
        
        for term in q:
            if term in d:
                qtfidf[term] = (1+math.log(q[term],10))*d[term][0][0]
        
        docs = set()
        #cosine calculation that includes numerator calculation
        for term in sv:
            if term in d:
                for item in d[term][0][1]:
                    if item[0] in pl:
                        score[item[0]] = score[item[0]] + (item[1] * self.d1[term][0][0] * qtfidf[term])
                        docs.add(item[0])        
        sumqterms = 0
        for term in terms:
            sumqterms = sumqterms + math.pow(qtfidf[term],2)
        x = math.sqrt(sumqterms)
            
        for dc in docs:
            cosine[dc] = score[dc]/(x*self.L2[dc])                        
        
        topk = list(islice(sorted(cosine.items(), key=lambda x: x[1], reverse=True),k))
        
        for top in  topk:
            print ("Text-"+str(top[0])+".txt" +" "+str(top[1]))
            
        print("--- Time taken to process the query is %s seconds ---" % (time.time() - start_time))
        pass

    def compute_cosine(self, vector, query_terms,k):
        terms = re.split('\W+',query_terms.lower())
        q = defaultdict(lambda:0)
        qtfidf = defaultdict(lambda:0)
        score = defaultdict(lambda:0)
        vect_len = defaultdict(lambda:0)
        length = defaultdict(lambda:0)
        cosine = defaultdict(lambda:0)
        
        for term in terms:
            q[term] = q[term]+1
        
        #query term tfidf calculation
        for term in q:
            if term in self.d1:
                qtfidf[term] = (1+math.log(q[term],10))*self.d1[term][0][0]
        
        docs = set()
        
        #calculation of numerator part of cosine
        for term in terms:
            if term in self.d1:
                for item in self.d1[term][0][1]:
                    if item[0] in vector:
                        score[item[0]] = score[item[0]] + (item[1] * self.d1[term][0][0] * qtfidf[term])
                        docs.add(item[0])
        
        sumqterms = 0
        for term in terms:
            sumqterms = sumqterms + math.pow(qtfidf[term],2)
        x = math.sqrt(sumqterms)
            
        for d in docs:
            cosine[d] = score[d]/(x*self.L2[d])                        
        #print (cosine)
        
        topk = list(islice(sorted(cosine.items(), key=lambda x: -x[1]),k))
        return topk
        pass
        
    def inexact_query_cluster_pruning(self, query_terms, k):
        #function for exact top K retrieval using cluster pruning (method 4)
        #Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score        
        start_time = time.time()
        followers=self.compute_cosine(self.leader_followers.keys(), query_terms,k)
        
        #if the relevant documents afre not found in the first leader, fidn it in successive leaders  that have decreasing idf values
        topk = []
        for a in followers:
            topk=self.compute_cosine(self.leader_followers[a[0]], query_terms,k)
            if len(topk) != 0:
                break
        
        for top in  topk:
            print ("Text-"+str(top[0])+".txt" +" "+str(top[1]))
        
        print("--- Time taken to process the query is %s seconds ---" % (time.time() - start_time))        
        pass
        
    def print_dict(self):
        #function to print the terms and posting list in the index
        #print (len(self.d1))
        for key in self.d1:
            print (key, '---->', self.d1[key])
        pass
        #print (self.d1["india"])
        
    def print_doc_list(self):
        #function to print the documents and their document id
        for j in self.docset:
            print ("Doc ID: ",j, "---->", "Text-"+str(j)+".txt")
        pass


#i=index("")
#i.remove_stop_words()
#i.buildIndex()
#i.print_dict()
#i.exact_query("LAW DIVIDINGBELGIUM SEPARATE WALLOONS",10)
#i.inexact_query_index_elimination("LAW DIVIDINGBELGIUM SEPARATE WALLOONS",10)