from conllu_reader import *

if '\\' in __file__:
    slash = '\\'
else:
    slash = '/'

LANGUAGE = __file__.split(slash)[-1][:-3].replace('HYPHEN', '-')

def possessive(conllu_item, returntype=list):
    """The return type is a dict, the "returntype" argument is a needless remnant of a previous phase of this project.
The point is to avoid crashing if an extra argument is given."""
    try:
        analyses = conllu_item['analyysit']
    except TypeError:
        print(conllu_item)
        return {'dep_marked':[], 'head_marked':[], 'double_marked':[], 'zero_marked':[], 'head_exist':[]}


    sent_id = conllu_item['sent_id']

    def find_head_index(analysis):
        head_str = analysis[6]
        head_i = int(head_str)-1
        return head_i
    
    head_exist = []

    dep_marked = []
    head_marked = []
    double_marked = []
    zero_marked = []

    for a in analyses:

        #pronouns

        if a[3] == 'PRON' and 'Case=Gen' in a[5] and 'PronType=Prs' in a[5] and 'Person=' in a[5] and a[7] == 'nmod':
            head_i = find_head_index(a)
            if head_i >= 0:
                if not any(w[3] == 'ADP' and w[6] == a[0] for w in analyses): # dependent not allowed to be part of an adposition phrase
                    head = analyses[head_i]
                    if head[3] in {'NOUN', 'PROPN'}:
                        dep_marked.append(a)

        if a[3] == 'DET' and 'Case=Gen' in a[5] and 'Poss=Yes' in a[5] and 'PronType=Prs' in a[5] and 'Reflex=Yes' not in a[5] and a[7] == 'nmod':
            head_i = find_head_index(a)
            if head_i >= 0:
                if not any(w[3] == 'ADP' and w[6] == a[0] for w in analyses): # dependent not allowed to be part of an adposition phrase
                    head = analyses[head_i]
                    if head[3] in {'NOUN', 'PROPN'}:
                        dep_marked.append(a)

        #nouns

        if a[3] in {'NOUN', 'PROPN'} and 'Case=Gen' in a[5] and a[7] == 'nmod':
            head_i = find_head_index(a)
            if head_i >= 0:
                if not any(w[3] == 'ADP' and w[6] == a[0] for w in analyses): # dependent not allowed to be part of an adposition phrase
                    head = analyses[head_i]
                    if head[3] in {'NOUN', 'PROPN'}:
                        if a[1].lower() == a[2].lower(): # if the dependent's word form is the same as the lemma, then it's a zero marked example
                            zero_marked.append(a)
                        else:
                            dep_marked.append(a)
        
    
    return {'dep_marked':dep_marked, 'head_marked':head_marked, 'double_marked':double_marked, 'zero_marked':zero_marked, 'head_exist':head_exist}


test = r'''# sent_id = dev-s25
# text = Obniża cenę do połowy, chociaż cena zależy też od stanu podręcznika.
# orig_file_sentence 001#25
1	Obniża	obniżać	VERB	fin:sg:ter:imperf	Aspect=Imp|Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_
2	cenę	cena	NOUN	subst:sg:acc:f	Case=Acc|Gender=Fem|Number=Sing	1	obj	_	_
3	do	do	ADP	prep:gen	AdpType=Prep|Case=Gen	4	case	_	_
4	połowy	połowa	NOUN	subst:sg:gen:f	Case=Gen|Gender=Fem|Number=Sing	1	obl	_	SpaceAfter=No
5	,	,	PUNCT	interp	_	8	punct	_	_
6	chociaż	chociaż	SCONJ	comp	_	8	mark	_	_
7	cena	cena	NOUN	subst:sg:nom:f	Case=Nom|Gender=Fem|Number=Sing	8	nsubj	_	_
8	zależy	zależeć	VERB	fin:sg:ter:imperf	Aspect=Imp|Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	1	advcl	_	_
9	też	też	PART	qub	_	8	advmod	_	_
10	od	od	ADP	prep:gen:nwok	AdpType=Prep|Case=Gen|Variant=Short	11	case	_	_
11	stanu	stan	NOUN	subst:sg:gen:m3	Animacy=Inan|Case=Gen|Gender=Masc|Number=Sing	8	obl:arg	_	_
12	podręcznika	podręcznik	NOUN	subst:sg:gen:m3	Animacy=Inan|Case=Gen|Gender=Masc|Number=Sing	11	nmod	_	SpaceAfter=No
13	.	.	PUNCT	interp	_	1	punct	_	_'''

conllu_item = to_ordered_dict(test)
d = possessive(conllu_item, dict)

if __name__ == '__main__':
    if type(d) == dict:
        for item in d:
            print(item, d[item], len(d[item]))
    else:
        for item in d:
            print(item)


def str2poss(s, returntype=dict):
    conllu_item = to_ordered_dict(s)
    return possessive(conllu_item, returntype)

def str2bea(s, returntype=dict):
    d = str2poss(s, returntype)
    if type(d) == dict:
        for item in d:
            print(item, d[item], len(d[item]))
    else:
        for item in d:
            print(item)

def str2beastr(s):
    d = str2poss(s, dict)
    answer = []
    for item in d:
        answer.append('{} {} {}'.format(item, d[item], len(d[item])))
    return '\n'.join(answer)


def strip_indent(s, i=1):
    c = []
    for j in s.splitlines():
        c.append(j[4*i:])
    return '\n'.join(c)
        
if __name__ == '__main__':
    exec(r'''import os

while 'UDtrack' in os.listdir():
    os.chdir('UDtrack')

folders = [w for w in os.listdir() if LANGUAGE in w and '.' not in w]

rootfolder = os.getcwd()

answer = ''

for folder in folders:
    os.chdir(folder)
    files = os.listdir()
    if folder[3:] + '_THIS.conllu' in files:
        file = folder[3:] + '_THIS.conllu'
        # A final modified file should be have a name that ends with
        # _THIS.conllu
        # e.g. UD_Afrikaans-AfriBooms_THIS.conllu
    else:
        file = folder[3:] + '.conllu'
        # If such a file doesn't exist, just use the original which is named
        # folder without UD_ + '.conllu'

    answer += avaa(file)

    os.chdir(rootfolder)

answer = answer.strip()

g = answer.split('\n\n') # merkkijonot
''')
    g = [w for w in g if w.strip()]
    h = [to_ordered_dict(w) for w in g]
    zero = []
    for sent in h:
        if possessive(sent, dict)['zero_marked']:
            zero.append(sent)
    

