# File: pos_tagging.py
# Template file for Informatics 2A Assignment 2:
# 'A Natural Language Query System in Python/NLTK'

# John Longley, November 2012
# Revised November 2013 and November 2014 with help from Nikolay Bogoychev
# Revised November 2015 by Toms Bergmanis


# PART B: POS tagging

from statements import *

# The tagset we shall use is:
# P  A  Ns  Np  Is  Ip  Ts  Tp  BEs  BEp  DOs  DOp  AR  AND  WHO  WHICH  ?

# Tags for words playing a special role in the grammar:

function_words_tags = [('a','AR'), ('an','AR'), ('and','AND'),
     ('is','BEs'), ('are','BEp'), ('does','DOs'), ('do','DOp'), 
     ('who','WHO'), ('which','WHICH'), ('Who','WHO'), ('Which','WHICH'), ('?','?')]
     # upper or lowercase tolerated at start of question.

function_words = [p[0] for p in function_words_tags]

def unchanging_plurals():
    with open('sentences.txt', 'r') as f:
        nN = []
        nNS= []
        for line in f:
            for phrase in line.split():
                words = phrase.split('|')
                if (words[1] == 'NNS'):
                    nNS.append(words[0])
                if (words[1] == 'NN'):
                    nN.append(words[0])
        return (list(set(nN) & set(nNS)))

unchanging_plurals_list = unchanging_plurals()

def noun_stem_find3s(s):
    lengthOfString = len(s)

    if (lengthOfString>=1):
        lastLetter = s[-1]
    if (lengthOfString>=2):
        lastTwo = s[-2:]
    if (lengthOfString>=3):
        lastThree = s[-3:]
    if (lengthOfString>=4):
        lastFour = s[-4:]

    # is have, its 3s form is has.
    if (lengthOfString==4 and s == 'have'):
        return 'has'

    if (lengthOfString==4 and s == 'unties'):
        return 'untie'

    # ends Xie where X is a single letter other than a vowel, simply add s
    endsInIE = 'ie'
    precNonVowel = '(a|e|i|o|u)'
    if (lengthOfString==4 and re.match(endsInIE, lastThree[:-1]) and not re.match(precNonVowel, s[0])):
        return (s[:-1]) 

    # ends in y preceded by a non-vowel and contains at least three letters, change the y to ies  
    endsInIES = 'ies'
    if (lengthOfString>=3 and re.match(endsInIES, lastThree) and not re.match(precNonVowel, lastFour[:-3])):
        return (s[:-3]+'y')

    # ends in anything except s,x,y,z,ch,sh or a vowel, simply add s
    endsInSXYZChShOrVowel = '(.a|.e|.i|.o|.u|.s|.x|.y|.z|ch|sh)'
    endsInS = 's'
    if (lengthOfString>=3 and not re.match(endsInSXYZChShOrVowel, lastThree[:-1]) and re.match(endsInS, lastLetter)):
        return (s[:-1])

    # ends in y preceded by a vowel, simply add s
    endsVowelY = '(a|e|i|o|u)y'
    if (lengthOfString>=3 and re.match(endsVowelY, lastThree[:-1])):
        return (s[:-1])

    # ends in se or ze but not in sse or zze, add s
    endsInSseZze = '(sse|zze)'
    endsInSeZe = '(se|ze)'
    if (lengthOfString>=4 and not re.match(endsInSseZze, lastFour[:-1]) and re.match(endsInSeZe, lastThree[:-1])):
        return (s[:-1])

    # ends in o,x,ch,sh,ss or zz, add es
    endsInOXChShSsZz = '(.o|.x|ch|sh|ss|zz)'
    if (lengthOfString>=4 and re.match(endsInOXChShSsZz, lastFour[:-2])):
        return (s[:-2])

    # ends in e not preceded by i,o,s,x,z,ch,sh, just add s
    precIOSXZChSh = '(.i|.o|.s|.x|.z|ch|sh)'
    endsInE = 'e'
    if (lengthOfString>=4 and not re.match(precIOSXZChSh, lastFour[:-2]) and re.match(endsInE, lastTwo[:-1])):
        return (s[:-1])

    else:
        return ''

def noun_stem (s):
    """extracts the stem from a plural noun, or returns empty string"""   
    lengthOfString = len(s)

    # if word is an unchanging plural, then just return s
    if (lengthOfString>=3):
        lastThree = s[-3:]
    if (s in unchanging_plurals()):
        return s

    # if s ends in 'men' then replace 'men' with 'man' for singular
    endsInMen = 'men'
    if (lengthOfString>=3 and re.match(endsInMen, lastThree)):
        return (s[:-2]+'an')

    # Otherwise, use rules from part A
    else:
        nounStem = noun_stem_find3s(s)
        if (nounStem.strip() == ''):
            return s
        else:
            return nounStem

def tag_word (lx,wd):
    """returns a list of all possible tags for wd relative to lx"""
    taggedWords = []
    verbStems = verb_stem(wd)
    nounStem = noun_stem(wd)

    # gets tag from function_words
    if wd in function_words:
        for w, t in function_words_tags:
            if (w == wd):
                taggedWords.append(t)

    # gets P and A from lx
    ProperNounsAdj = ['P', 'A']
    for cat in ProperNounsAdj:
        if (wd in lx.getAll(cat)):
            taggedWords.append(cat)

    # gets N from lx as Singular and Plural
    if (wd in unchanging_plurals_list):
        if nounStem in lx.getAll('N'):
            taggedWords.append('Ns')
            taggedWords.append('Np')
        else:
            if (not(wd == nounStem)):
                taggedWords.append('Np')
            else:
                taggedWords.append('Ns')
    if nounStem in lx.getAll('N'):
        if (wd in unchanging_plurals_list):
            taggedWords.append('Np')
            taggedWords.append('Ns')
        else:
            if (nounStem != wd): 
                taggedWords.append('Np')
            else:
                taggedWords.append('Ns')

    # gets T and I from lx and taggedWords as Singular and Plural 
    IntrasAndTras = ['I','T']
    for cat in IntrasAndTras:
        if (wd in lx.getAll(cat)) or (verbStems in lx.getAll(cat)):
            if verbStems != wd:
                taggedWords.append(cat +'s')
            else:
                taggedWords.append(cat +'p')

    return list(set(taggedWords))

def tag_words (lx, wds):
    """returns a list of all possible taggings for a list of words"""
    if (wds == []):
        return [[]]
    else:
        tag_first = tag_word (lx, wds[0])
        tag_rest = tag_words (lx, wds[1:])
        return [[fst] + rst for fst in tag_first for rst in tag_rest]

# End of PART B.