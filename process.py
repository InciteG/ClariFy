import nltk
import re
from nltk.tokenize import wordpunct_tokenize
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

def set_stop(add=True, punc=True, num=True, *args, **kwargs):
    #set stop_words
    stop_words = frozenset(['a','about','above','across','after','afterwards','again','against','ain','all','almost','alone','along','already','also','although','always',
    'am','among','amongst','amoungst','amount','an','and','another','any','anyhow','anyone','anything','anyway','anywhere','are','aren','around','as','at','back','be','became','because','become','becomes',
    'becoming','been','before','beforehand','behind','being','below','beside','besides','between','beyond','bill','both','bottom','but','by','call','can','cannot','cant','co','con','could',
    'couldn','couldnt','cry','d','de','describe','detail','did','didn','do','does','doesn','doing','don''done','down','due','during','each','eg','eight','either','eleven',
    'else','elsewhere','empty','enough','etc','even','ever','every','everyone','everything','everywhere','except','few',
    'fifteen',
    'fify',
    'fill',
    'find',
    'fire',
    'first',
    'five',
    'for',
    'former',
    'formerly',
    'forty',
    'found',
    'four',
    'from',
    'front',
    'full',
    'further',
    'get',
    'give',
    'go',
    'had',
    'hadn',
    'has',
    'hasn',
    'hasnt',
    'have',
    'haven',
    'having',
    'he',
    'hence',
    'her',
    'here',
    'hereafter',
    'hereby',
    'herein',
    'hereupon',
    'hers',
    'herself',
    'him',
    'himself',
    'his',
    'how',
    'however',
    'hundred',
    'i',
    'ie',
    'if',
    'in',
    'inc',
    'indeed',
    'interest',
    'into',
    'is',
    'isn',
    'it',
    'its',
    'itself',
    'just',
    'keep',
    'last',
    'latter',
    'latterly',
    'least',
    'less',
    'll',
    'ltd',
    'm',
    'ma',
    'made',
    'many',
    'may',
    'me',
    'meanwhile',
    'might',
    'mightn',
    'mill',
    'mine',
    'more',
    'moreover',
    'most',
    'mostly',
    'move',
    'much',
    'must',
    'mustn',
    'my',
    'myself',
    'name',
    'namely',
    'needn',
    'neither',
    'never',
    'nevertheless',
    'next',
    'nine',
    'no',
    'nobody',
    'none',
    'noone',
    'nor',
    'not',
    'nothing',
    'now',
    'nowhere',
    'o',
    'of',
    'off',
    'often',
    'on',
    'once',
    'one',
    'only',
    'onto',
    'or',
    'other',
    'others',
    'otherwise',
    'our',
    'ours',
    'ourselves',
    'out',
    'over',
    'own',
    'part',
    'per',
    'perhaps',
    'please',
    'put',
    'rather',
    're',
    's',
    'same',
    'see',
    'seem',
    'seemed',
    'seeming',
    'seems',
    'serious',
    'several',
    'shan',
    'she',
    'should',
    'shouldn',
    'show',
    'side',
    'since',
    'sincere',
    'six',
    'sixty',
    'so',
    'some',
    'somehow',
    'someone',
    'something',
    'sometime',
    'sometimes',
    'somewhere',
    'still',
    'such',
    'system',
    't',
    'take',
    'ten',
    'than',
    'that',
    'the',
    'their',
    'theirs',
    'them',
    'themselves',
    'then',
    'thence',
    'there',
    'thereafter',
    'thereby',
    'therefore',
    'therein',
    'thereupon',
    'these',
    'they',
    'thick',
    'thin',
    'third',
    'this',
    'those',
    'though',
    'three',
    'through',
    'throughout',
    'thru',
    'thus',
    'to',
    'together',
    'too',
    'top',
    'toward',
    'towards',
    'twelve',
    'twenty',
    'two',
    'un',
    'under',
    'until',
    'up',
    'upon',
    'us',
    've',
    'very',
    'via',
    'was',
    'wasn',
    'we',
    'well',
    'were',
    'weren',
    'what',
    'whatever',
    'when',
    'whence',
    'whenever',
    'where',
    'whereafter',
    'whereas',
    'whereby',
    'wherein',
    'whereupon',
    'wherever',
    'whether',
    'which',
    'while',
    'whither',
    'who',
    'whoever',
    'whole',
    'whom',
    'whose',
    'why',
    'will',
    'with',
    'within',
    'without',
    'won',
    'would',
    'wouldn',
    'y',
    'yet',
    'you',
    'your',
    'yours',
    'yourself',
    'yourselves'
])
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
    return stop_words

#call after processing
def gg_tokenize(text, stop_words, pos= True, stop=True, stem=True, **kwargs):
    nre = re.sub(r"(\n)", r" ", text) #remove "\n" characters
    cap = re.sub(r"\b([a-z0-9]+)([A-Z])", r"\1 \2", nre) #Split words that were misformatted and conjoined together e.g. "tasksProgram"
    cap = re.sub(r"\b([a-z]+)([0-9])", r"\1 \2", cap) #Split words that were misformatted and conjoined together e.g. "tasksProgram"
    if pos is True:
        tokenize = nltk.wordpunct_tokenize(cap)
        pos_tag = nltk.pos_tag(tokenize)
        remove = ['PRP$','WP$','WP','WRB','WDT','UH','TO','RP','RBS','RBR','RB','PRP','MD','LS','JJS','JJ','JJR','FW','IN','DT','CC']
        out = []
        for tok in pos_tag:
            if tok[1] in remove:
                pass
            else:
                out.append(tok[0])
        cap = ' '.join(out)
    else:
        pass
    punc = re.sub(r"([-./\\}{_*&\"^@#!\)\(?=+])([a-z0-9A-Z])", r"\1 \2", cap) #remove punctuation by replacing with space, allows tokenize to occur more effectively
    tok = re.split(r"[ .*@|\/,<>:;&%$#@\+!)?(\\='^_-]", punc.lower()) #tokenize based on any left over punctuation or spaces
    if stop is True:
        h = [n for n in tok if not n in stop_words] #remove stop_words after tokenization, leftovers will be removed with stem stop_words
    else:
        h = tok 
    if stem is True:
        stemmer = SnowballStemmer('english')
        stemm = [stemmer.stem(word) for word in h]   #stem words after stop_word removal and tokenization
        return stemm
    else:
        return h

def wp_tokenize(text, stop_words, pos= True, stop=True, stem=True,  **kwargs):
    tokenize = nltk.wordpunct_tokenize(text)
    if pos is True:
        pos_tag = nltk.pos_tag(tokenize)
        remove = ['PRP$','WP$','WP','WRB','WDT','UH','TO','RP','RBS','RBR','RB','PRP','MD','LS','JJS','JJ','JJR','FW','IN','DT','CC']
        tokenize = []
        for tok in pos_tag:
            if tok[1] in remove:
                pass
            else:
                tokenize.append(tok[0])
    else:
        pass

    if stop is True:
        tokenize = [n for n in tokenize if not n in stop_words] #remove stop_words after tokenization, leftovers will be removed with stem stop_words
    else:
        pass
    if stem is True:
        stemmer = SnowballStemmer('english')
        stemm = [stemmer.stem(word) for word in tokenize]   #stem words after stop_word removal and tokenization
        return stemm
    else:
        return tokenize

