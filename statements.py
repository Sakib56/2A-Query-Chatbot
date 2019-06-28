# File: statements.py
# Template file for Informatics 2A Assignment 2:
# 'A Natural Language Query System in Python/NLTK'

# John Longley, November 2012
# Revised November 2013 and November 2014 with help from Nikolay Bogoychev
# Revised November 2015 by Toms Bergmanis
# Revised October 2017 by Chunchuan Lyu


# PART A: Processing statements

def add(lst,item):
    if (item not in lst):
        lst.insert(len(lst),item)

class Lexicon:
    """stores known word stems of various part-of-speech categories"""
    def __init__(self):
        self.lx = []
        self.allowedCats = ['P', 'N', 'A', 'I', 'T']

    def add(self, stem, cat):
        if (cat in self.allowedCats):
            self.lx.append((stem, cat))
        else:
            print(cat+' not accepted')

    def getAll(self, cat):
        if (len(self.lx) != 0):
            output = [s for s, c in (self.lx) if (cat == c)]
            return list(set(output))
        else:
            return []

class FactBase:
    """stores unary and binary relational facts"""
    def __init__(self):
        self.unaryDictionary = []
        self.binaryDictionary = []

    def addUnary(self, pred, e1):
        self.unaryDictionary.append((pred, e1))

    def queryUnary(self, pred, e1):
        return ((pred, e1) in self.unaryDictionary)

    def addBinary(self, pred, e1, e2):
        self.binaryDictionary.append((pred, e1, e2))

    def queryBinary(self, pred, e1, e2):
        return ((pred, e1, e2) in self.binaryDictionary)

import nltk
import re
from nltk.corpus import brown

taggedVerbs = [x for x, y in nltk.corpus.brown.tagged_words() if ((y == 'VBZ') or (y == 'VB'))]

def find3s(s):
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

def verb_stem(s):
    """extracts the stem from the 3sg form of a verb, or returns empty string"""
    hyp = find3s(s)

    if (s == 'are' or s == 'do' or s == 'have'):
        return s
    if (s in taggedVerbs or hyp in taggedVerbs):
        return hyp
    else:
        return ''

def add_proper_name (w,lx):
    """adds a name to a lexicon, checking if first letter is uppercase"""
    if ('A' <= w[0] and w[0] <= 'Z'):
        lx.add(w,'P')
        return ''
    else:
        return (w + " isn't a proper name")

def process_statement (lx,wlist,fb):
    """analyses a statement and updates lexicon and fact base accordingly;
       returns '' if successful, or error message if not."""
    # Grammar for the statement language is:
    #   S  -> P is AR Ns | P is A | P Is | P Ts P
    #   AR -> a | an
    # We parse this in an ad hoc way.
    msg = add_proper_name (wlist[0],lx)
    if (msg == ''):
        if (wlist[1] == 'is'):
            if (wlist[2] in ['a','an']):
                lx.add (wlist[3],'N')
                fb.addUnary ('N_'+wlist[3],wlist[0])
            else:
                lx.add (wlist[2],'A')
                fb.addUnary ('A_'+wlist[2],wlist[0])
        else:
            stem = verb_stem(wlist[1])
            if (len(wlist) == 2):
                lx.add (stem,'I')
                fb.addUnary ('I_'+stem,wlist[0])
            else:
                msg = add_proper_name (wlist[2],lx)
                if (msg == ''):
                    lx.add (stem,'T')
                    fb.addBinary ('T_'+stem,wlist[0],wlist[2])
    return msg
                        
# End of PART A.

