#!/usr/bin/python

import sys

description = '''
Find repeated subwords in the input.
'''

kRepeatThresh = 8

def SuffixArray(T):
    # FIXME: Do it in O(n).
    #        http://www.cs.helsinki.fi/u/tpkarkka/publications/icalp03.pdf
    return sorted(list(range(len(T))), key=lambda i: T[i:])

def SharedChars(T, Pos1, Pos2):
    Len = 0
    while Pos1 + Len < len(T) and \
          Pos2 + Len < len(T) and \
          T[Pos1 + Len] == T[Pos2 + Len]:
        Len += 1
    return Len

def FindLongestRepeatedSubstr(T):
    SA = SuffixArray(T)
    SkipTo = 0
    for i in range(len(SA) - 1):
        if i < SkipTo:
            continue

        # Find the largest repeated prefix in these suffixes.
        j = i + 1
        while j < len(SA) and SharedChars(T, SA[i], SA[j]) > 0:
            j += 1
        SkipTo = j
        j -= 1

        Len = SharedChars(T, SA[i], SA[j])
        if i != j and Len > kRepeatThresh:
            yield Len, SA[i], SA[j], j - i + 1
 
def WordsToTokens(T):
    Dictionary = {}
    InverseDictionary = []
    Tokens = []
    for Word in T.split():
        if Word not in Dictionary:
            Dictionary[Word] = len(InverseDictionary)
            InverseDictionary.append(Word)
        Tokens.append(Dictionary[Word])
    return Tokens, InverseDictionary

def ReprTokenRange(Tokens, InverseDictionary, Pos, Len):
    return ' '.join(InverseDictionary[Tokens[Pos + i]] for i in range(Len))

def VerifyRepetition(Len, Pos1, Pos2, Tokens):
    assert Pos1 != Pos2
    for i in range(Len):
        assert Tokens[Pos1 + i] == Tokens[Pos2 + i]

if __name__ == '__main__':
    T = sys.stdin.read()
    Tokens, InverseDictionary = WordsToTokens(T)

    for Len, Pos1, Pos2, RepeatCount in FindLongestRepeatedSubstr(Tokens):
        VerifyRepetition(Len, Pos1, Pos2, Tokens)

        print "Repeated {} times @ ({}, {}), Len={}:".format(
                RepeatCount, Pos1, Pos2, Len)
        print ReprTokenRange(Tokens, InverseDictionary, Pos1, Len)
