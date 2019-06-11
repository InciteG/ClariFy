#finalize notebook
#create pipeline for data processing
#Final Text Processing, changeable with input
# TF-IDF, KMean, Ward, top vectors
# Word2Vec, Kmean, Ward, top vectors
# LDA, 
#import
import re
import random
import sys
import numpy as np
from operator import itemgetter
import pandas as pd #df
import sklearn as sk
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, ENGLISH_STOP_WORDS #vectorizers & stop_words
from sklearn.cluster import KMeans
from sklearn.externals import joblib
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE, MDS
from sklearn.decomposition import PCA
import nltk
from nltk import text
from nltk.tokenize import word_tokenize, wordpunct_tokenize, sent_tokenize
from nltk.stem.snowball import SnowballStemmer
import gensim #w2v, lda
from gensim import corpora


stemmer = SnowballStemmer('english')
#function that takes list of documents and determines stop_words to add based on conditions
#text variable must be dataframe
def text_process(texts, clean=True, pos=True, sentence=True, **kwargs):
    corpus = texts.Description.values #init corpus, unmodified description
    #remove repeating sentences
    if sentence is True:
        tv = CountVectorizer(tokenizer=sent_tokenize)
        tmat =tv.fit_transform(texts)
        tf = tv.get_feature_names()
        tmata = tmat.toarray()
        tmatat = tmata.transpose()
        tl = []
        for item,name in zip(tmatat, tf):
            tl.append([name, item.mean()])
        newl = []
        for item in tl:
            if item[1] >= ((1/len(texts.Description.values))*1.1):
                newl.append(item)
        nono = []
        for item in newl:
            reg = re.search('[ ]', item[0])
            if reg is None:
                nono.append(item)
        nnl = [n for n in newl if n not in nono]
        ccorpus = []
        for desc in texts.Description.values:
            sent = sent_tokenize(desc)
            nxt = [u for u in sent if u not in nnl]
            string = ''.join(nxt)
            ccorpus.append(string)
        corpus= ccorpus
    else:
        print('sentence=false')
    #clean \n and misaligned words
    if clean is True:
        ccorpus = []
        for txt in corpus:
            nre = re.sub(r"(\n)", r" ", txt) #remove "\n" characters
            cap = re.sub(r"\b([a-z0-9]+)([A-Z])", r"\1 \2", nre) #Split words that were misformatted and conjoined together e.g. "tasksProgram"
            cap = re.sub(r"\b([a-z]+)([0-9])", r"\1 \2", cap) #Split words that were misformatted and conjoined together e.g. "tasksProgram"
            ccorpus.append(cap)
        corpus = ccorpus
    else:
        print('clean=false')
    #remove adjectives, adverbs, prepositions etc., unnecessary POS tagging
    if pos is True:
        ccorpus = []
        for txt in corpus:
            tokenize = nltk.wordpunct_tokenize(txt)
            pos_tag = nltk.pos_tag(tokenize)
            remove = ['PRP$','WP$','WP','WRB','WDT','UH','TO','RP','RBS','RBR','RB','PRP','MD','LS','JJS','JJ','JJR','FW','IN','DT','CC']
            out = []
            for tok in pos_tag:
                if tok[1] in remove:
                    pass
                else:
                    out.append(tok[0])
            string = ' '.join(out)
            ccorpus.append(string)
        corpus=ccorpus
    return corpus

def set_stop(corpus, df, add=True, punc=True, loc=True, num=True, company=True, max_df=0.8, min_df=.02, *args, **kwargs):
    #set stop_words
    stop_words = ENGLISH_STOP_WORDS
    stopw = nltk.corpus.stopwords.words('english') #add additional stop words
    stop_words = stop_words.union(stopw) #add punc removal
    #add stop_words unable to be filtered out from other means
    if add is True:
        add_stop=['lab','laboratory','company','inc','technology','computer','institute','public','\r','connect','people','fb','g','ge',
                  'accomadate','sexuality','sex','orientation','orient','gender','race','ethnicity','ethnic','equal','opportunity','minor',
                  'disable','veteran','female','male','employer','employee','network','require','affirm','jp','jpmorgan','chase','usa','america','canada',
                  'career','job','compani', 'work','location','origin','religion','ident','sexual','color','identity','nation','national',
                 'disability','protect','protected','background','screening','screen','drug','diversity','diverse','employment',
                 'employ','affirimative','action','applicant','discrimination','discriminate','apply','application', 'resume','agency','agent',
                 '\r \r', 'proud','inclusive','inclusion','recruit','recruitment','recruiter','hire','submit','agree','agreement',
                 'marital', 'status', 'marriage', 'help','require','perform','duty','duti','provide','accomod', 'authorization','author',
                 'type','time','salary', '00','000 00', '000', 'citizenship','citizen','large','identify','crime','criminal', 
                 'ancestry', "you're","you'r","we're","we'r", 'minority','abuse', 'affirm', 'united', 'states', 'province', 'shift',
                 '’','skill','ability', 'skills','role', 'assist','prepare','office','email','com','hr','contact','require','requir',
                 'benefit','insure','health','vision','dental','plan', 'pay','paid','staff','401','RSP','k','consider','consid','candid','safety','safeti',
                 'u','hour','perform','act','policy','polici', 'compensation','compensate','match','matching','insurance','insur', 'claim'
                 'texas','texa','state','tuition','traffic','million','billion','lunch','coffee','include','use','inform','age','agree','agreement',
                 'law','regard','applic','www','driver','401k','express','vet','veterans','disabilities','eeo','pto','leave','paternity','mat','maternity'
                 'world','join','value','build'] #removal of stop-words that were unable to be filtered out from other methods
        stop_words = stop_words.union(add_stop)
    else:
        print('add=false')
    #remove punc not captured by regex
    if punc is True:
        punct = ['.',',','"','?', '!', ':',';','(',')','[',']','{','}','%','$','#','@','&','*',"'",'-','>','<','/','^', ''] 
        stop_words = stop_words.union(punct)
    else:
        print('punc=false')
    #remove numbers 1 through 10 from stopword removal - keep years experience desired
    if num is True:
        high = range(11,4400,1)
        sw = []
        for item in high:
            sw.append(str(item))
        stop_words = stop_words.union(sw)
    else:
        print('num=false')
    
    #remove company names
    if company is True:
        comp = df.Company.values
        pcom = []
        for item in comp:
            pcom.append(item.lower())
        pnd = list(set(pcom))
        stop_words = stop_words.union(pnd)
    else:
        print('company=false')
    #location removal
    if loc is True:
        location = df.Location.values
        pcom = []
        for item in location:
            w = wordpunct_tokenize(item)
            for itr in w:
                pcom.append(itr.lower())
        pnd = list(set(pcom))
        stop_words = stop_words.union(pnd)
    else:
        print('company=false')
    #add stop_words based on document frequency cutoffs
    cv = CountVectorizer(max_df = max_df, min_df = min_df, stop_words=stop_words, tokenizer=wordpunct_tokenize)
    cvm = cv.fit(corpus)
    swp = cv.stop_words_
    stop_words = stop_words.union(swp)
    #remove recurring sentences
    return stop_words

#call after processing
def gg_tokenize(text):
    nre = re.sub(r"(\n)", r" ", text) #remove "\n" characters
    cap = re.sub(r"\b([a-z0-9]+)([A-Z])", r"\1 \2", nre) #Split words that were misformatted and conjoined together e.g. "tasksProgram"
    cap = re.sub(r"\b([a-z]+)([0-9])", r"\1 \2", cap) #Split words that were misformatted and conjoined together e.g. "tasksProgram"
    punc = re.sub(r"([-./\\}{_*&\"^@#!\)\(?=+])([a-z0-9A-Z])", r"\1 \2", cap) #remove punctuation by replacing with space, allows tokenize to occur more effectively
    tok = re.split(r"[ .*@|\/,<>:;&%$#@\+!)?(\\='^_-]", punc.lower()) #tokenize based on any left over punctuation or spaces
    stem = [stemmer.stem(word) for word in tok]   #stem words after stop_word removal and tokenization
    return stem

def tfidf_get(corpus, stop_words, tokenizer, max_df=.8, min_df=.02, **kwargs):
    tfidf = TfidfVectorizer(max_df=max_df, min_df=min_df, stop_words=stop_words, tokenizer=tokenizer)
    tmatrix = tfidf.fit_transform(corpus)
    return tmatrix

#Feature Engineer with LDA, Topic Modeling
def lda_get(corpus, num_topics=20, random_state=100, update_every=1, 
           chunksize=100,passes=20, alpha='auto',per_word_topics=True, **kwargs):
    id2word = corpora.Dictionary(corpus)
    tdf = [id2word.doc2bow(text) for text in corpus]

    lda_model = gensim.models.ldamodel.LdaModel(corpus=tdf,
                                               id2word=id2word,
                                               num_topics=num_topics, 
                                               random_state=random_state,
                                               update_every=update_every,
                                               chunksize=chunksize,
                                               passes=passes,
                                               alpha=alpha,
                                               per_word_topics=per_word_topics)
    
    label_df = pd.DataFrame()

    # Get main topic in each document
    for row in lda_model[tdf]:
        row = sorted(row[0], key=itemgetter(1), reverse=True)
        # Get the Dominant topic, Perc Contribution and Keywords for each document
        wp = lda_model.show_topic(row[0][0])
        topic_keywords = ", ".join([word for word, prop in wp])
        label_df = label_df.append(pd.Series([int(row[0][0]), round(row[0][1],4), topic_keywords]), ignore_index=True)

    # Add original text to the end of the output
    contents = pd.Series(corpus)
    label_df = pd.concat([label_df, contents], axis=1)
    label_df.columns = ['Cluster Label', 'Perc_Contribution', 'Topic_Keywords', 'Tokenized Text']
    
    top_doc = pd.DataFrame()
    grouped = label_df.groupby('Cluster Label')

    for i, grp in grouped:
        top_doc = pd.concat([top_doc, grp.sort_values(['Perc_Contribution'], ascending=[0]).head(1)], axis=0)
    return lda_model, label_df, top_doc, 

#kmean clustering
def kmeans(matrix,df, n_clusters=10, **kwargs):
    km = KMeans(n_clusters=n_clusters)
    km.fit(matrix)
    dfk = df.copy()
    dfk['Cluster Label'] =km.labels_
    return km, dfk

#graph clusters in 2-D space, choose dimensionality reduction technique    
def graph_cluster(matrix, df, dim='t-SNE', **kwargs):
    dist = 1-cosine_similarity(matrix)
    dfg = df.copy()
    if dim=='t-SNE':
        tsne = TSNE(n_components=2, random_state=2).fit_transform(dist)
        dfg['Dim-1'] = tsne[:,0]
        dfg['Dim-2'] = tsne[:,1]
    elif dim=='PCA':
        tsne = PCA(n_components=2, random_state=2).fit_transform(dist)
        dfg['Dim-1'] = tsne[:,0]
        dfg['Dim-2'] = tsne[:,1]
    elif dim=='MDS':
        tsne = MDS(n_components=2, random_state=2).fit_transform(dist)
        dfg['Dim-1'] = tsne[:,0]
        dfg['Dim-2'] = tsne[:,1]
    else:
        'Dimensionality reduction tool not available. Please choose "t-SNE","PCA", or "MDS"'
    return dfg

#determine top vectors in each cluster
def conv_top(corpus, df, stop_words, max_df=.8, min_df=.02, top=30, **kwargs):
    cluster_top_vectors = {}
    cv = CountVectorizer(max_df=.8, min_df=.02, stop_words=stop_words,tokenizer = wordpunct_tokenize)
    cvm = cv.fit_transform(corpus)
    for i in range(0,len(df['Cluster Label'].unique())):
        dfc = df.loc[df['Cluster Label'] ==i]
        lab = df.index.tolist()
        crn = cvm.toarray()
        labelem = []
        for item, l in zip(crn, lab):
            labelem.append([l,item])
        l1 = [n for n in labelem if n[0] in dfc.index]
        newm = []
        for item in l1:
            newm.append(item[1])
        newmt = np.array(newm).transpose()
        topv = []
        for item,name in zip(newmt,cv.get_feature_names()):
            mn = item.mean()
            topv.append([name,mn])
        topvs = sorted(topv, key=itemgetter(1), reverse=True)
        topn = []
        for item in topvs[0:top]:
            topn.append(item[0])
        cluster_top_vectors[i]=topn
    return cluster_top_vectors

def pipe(df, cluster_num = 8, **kwargs):
    #scrape, store in sql, load into pipe, 
    #tfidf, w2v, or lda
    #kmeans or lda cluster
    #Output tables for data insertion into div
    cleaned = text_process(df)
    stop_words = set_stop(cleaned, df)
    stem_stop = [stemmer.stem(word) for word in stop_words]
    gg_corpus = [gg_tokenize(document) for document in cleaned]
    tmatrix = tfidf_get(cleaned, stem_stop, gg_tokenize)
    km, dfk = kmeans(tmatrix, df, n_clusters=cluster_num)
    dfkg = graph_cluster(tmatrix, dfk)
    top = conv_top(cleaned, dfk, stop_words)
    dfkg['Top Vectors'] = dfkg['Cluster Label'].map(top)
    lad, label_df, top_doc = lda_get(gg_corpus, num_topics=14)
    dflda = pd.merge(df, label_df, left_index=True, right_index=True, how='inner')
    dfldat = graph_cluster(tmatrix, dflda)
    return dfkg, dfldat
