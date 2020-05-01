import re
from functools import reduce

import spacy
import string
import collections

from random import randint
from gensim.models import Word2Vec
from nltk.corpus import stopwords
from difflib import SequenceMatcher
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from spacy.matcher import PhraseMatcher

key_line = []
student_line = []
return_match_scores = []

num_cols_of_interest = 4

corpus = []
word2vec = []
sentences = []

name = []
lines = []
first = ''
second =''
third = ''
fourth = ''
result = []
answer_key = []
entire_line = []

word4 = ''
result_word = ''
d = collections.defaultdict(list)

student_list = []

word_list = ["a", "also", "an", "and", "are", "as",
             "for", "in", "is", "of", "on", "to", "the", "thereby",
             "which"]

sp = spacy.load('en_core_web_sm')
phrase_matcher = PhraseMatcher(sp.vocab)


# key file name is key.txt, with tab-separated lines, one per drug
#  (see get_key_file_column for attributes of interest)
# student file name is <drug name>.txt, with tab-separated lines
#  (student id, student response)

def return_matches(key_file_name, student_file_name):
    global key_line, student_line, return_match_scores, num_cols_of_interest
    return_match_string = ''
    kf = open(key_file_name, 'r', encoding="utf8")
    for key_file_line in kf:
        key_line = key_file_line.split()
        if is_correct_key_line(key_line[0], student_file_name):
            create_corpus(key_file_line)  # find key sentences/phrases
            sf = open(student_file_name, 'r', encoding="utf8")
            for student_file_line in sf:
                student_line = student_file_line.split()
                # process
                for i in range(1, num_cols_of_interest + 1):
                    # /*
                    # sp_key_line = sp(key_line[i])  # loop through key's contents
                    # sp_student_line = sp(student_line[1])
                    # for key_word in sp_key_line:
                    #     print(key_word.text, key_word.pos_, key_word.dep_)
                    # for student_word in sp_student_line.sents:
                    #     print(student_word.text)
                    # */
                    # match against the attribute of interest (current key column)
                    col_name = get_key_file_column(i)
                    pattern = [sp(text) for text in key_line[i]]
                    phrase_matcher.add(col_name, None, *pattern)
                    # use the entire student entry to find the portion that is for
                    #  the current key attribute of interest
                    # phrase_match = phrase_matcher(student_line[1])
                    return_match_string = return_match_string + '\n' + \
                        'for student ' + student_line[0] + ', ' + \
                        'for drug ' + key_line[0] + ', ' + \
                        'for ' + col_name + '; ' + \
                        'score: ' + str(randint(0, 100))
                    phrase_matcher.remove(col_name)
            sf.close()
        return_match_scores.append(return_match_string)
    kf.close()

    parse_key_four_part(key_file_name, student_file_name)
    # separate_student(student_file_name)
    return return_match_scores


def is_correct_key_line(key_line_key, student_file_name):
    # ensure that key entry is for the drug of interest
    if student_file_name.lower().find(key_line_key.lower()) >= 0:
        return 1
    return 0


def get_key_file_column(i):
    if i == 0:
        return 'drug name'
    elif i == 1:
        return 'pharmacologic role'
    elif i == 2:
        return 'drug target and primary localization'
    elif i == 3:
        return "target's role in normal physiology"
    elif i == 4:
        return 'outcomes necessary for therapeutic activities'
    else:
        return ''


def create_corpus(key_file_line):
    from nltk.corpus import wordnet
    synonyms = []
    antonyms = []
    for syn in wordnet.synsets("active"):
        for l in syn.lemmas():
            synonyms.append(l.name())
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())
    print(set(synonyms))
    print(set(antonyms))
    # use the key file line to create a word2vec model
    # first omit the first word (drug name)
    # next clean the text,
    #  - convert all text to lowercase
    #  - keep digits & special characters
    #  - remove extra spaces and then stop words
    global sentences, corpus, word2vec
    new_words = strip_first_value(key_file_line)
    new_words = new_words.lower().strip()
    # new_words = re.sub('[^a-zA-Z]', ' ', new_words)
    new_words = re.sub(r'\s+', ' ', new_words)
    sentences = sent_tokenize(new_words)
    corpus = [word_tokenize(sent) for sent in sentences]
    for i in range(len(corpus)):
        corpus[i] = [w for w in corpus[i] if w not in stopwords.words('english')]
    word2vec = Word2Vec(corpus, min_count=1)


def strip_first_value(in_line):
    # return substring after the first tab
    j = 0
    tmp = ''
    for i in range(len(in_line)):
        if in_line[i] == '\t':
            j = i + 1
            break
    for i in range(j, len(in_line)):
        tmp += in_line[i]
    return tmp


def parse_key_four_part(file1,file2):
    global result_word, first, second, third, fourth
    file1 = open(file1, 'r')

    data = file1.readlines()

    for line in data:
        table = str.maketrans(dict.fromkeys(string.punctuation))
        new_line = line.translate(table)  # clear all punctuation
        lines.append(new_line)

        for whole_line in lines:
            wordx = whole_line.split('\t')
            first = wordx[1]
            second = wordx[2]
            third = wordx[3]
            fourth = wordx[4]
            separate_student(file2)
    return


def separate_student(student_file_name):
    global first, second, third, fourth
    sf = open(student_file_name, 'r', encoding="utf8")
    for student_file_line in sf:
        student_line = student_file_line.split('\t')
        printsentence = 'for student {}\n'.format(student_line[0])
        return_match_scores.append(printsentence)
        for i in student_line:
            if i.find('.') > 0:
                student_line1 = i.split('.')
                if (len(student_line1) < 5):
                    comparison(first, student_line1[0])
                    comparison(second, student_line1[1])
                    comparison(third+fourth, student_line1[2])
                    # comparison(forth, student_line1[3])
                elif (len(student_line1) == 5):
                    comparison(first, student_line1[0])
                    comparison(second, student_line1[1])
                    comparison(third, student_line1[2])
                    comparison(fourth, student_line1[3])
                elif (len(student_line1) == 6):
                    student_line1[0: 2] = [''.join(student_line1[0: 2])]
                    student_line1[2: 4] = [''.join(student_line1[2: 4])]
                    comparison(first, student_line1[0])
                    comparison(second, student_line1[1])
                    comparison(third, student_line1[2])
                    comparison(fourth, student_line1[3])
                elif (len(student_line1) == 7):
                    student_line1[0: 2] = ''.join(student_line1[0: 2])
                    student_line1[2: 4] = ''.join(student_line1[2: 5])
                    student_line1[4: 6] = [''.join(student_line1[4: 6])]
                    comparison(first, student_line1[0])
                    comparison(second, student_line1[1])
                    comparison(third, student_line1[2])
                    comparison(fourth, student_line1[3])
                elif (len(student_line1) == 8):
                    # [student_line1[i] + student_line1[i + 1] for i in range(0, len(student_line1), 2)]
                    student_line1[0:2] = [''.join(student_line1[0:2])]
                    student_line1[2:4] = [''.join(student_line1[2:4])]
                    student_line1[4:7] = [''.join(student_line1[4:7])]
                    student_list.append(student_line1)
                    comparison(first, student_line1[0])
                    comparison(second, student_line1[1])
                    comparison(third, student_line1[2])
                    comparison(fourth, student_line1[3])
                elif (len(student_line1) == 9):
                    student_line1[0:3] = [''.join(student_line1[0:3])]
                    student_line1[3:5] = [''.join(student_line1[3:5])]
                    student_line1[5:8] = [''.join(student_line1[5:8])]
                    comparison(first, student_line1[0])
                    comparison(second, student_line1[1])
                    comparison(third, student_line1[2])
                    comparison(fourth, student_line1[3])
                else:
                    student_line1[0:3] = [''.join(student_line1[0:3])]
                    student_line1[3:5] = [''.join(student_line1[3:5])]
                    student_line1[5:9] = [''.join(student_line1[5:9])]
                    comparison(first, student_line1[0])
                    comparison(second, student_line1[1])
                    comparison(third, student_line1[2])
                    comparison(fourth, student_line1[3])
    return

def comparison(key_string,student_string):
    ratio = SequenceMatcher(None, key_string, student_string).ratio()
    printsentence = 'ratio: {}.\n'.format(ratio)
    return_match_scores.append(printsentence)


def main_comparison(key_string, input_string):
    words = set(key_string)
    with open('outfile.txt', 'a') as output:
        for word in words:
            output.write(
                '{} appears {} times in key file and {} times in student file.\n'.format(word, key_string.count(word),
                                                                                         input_string.count(word)))
    output.close()


def parse_key(file1):
    global result_word
    data = file1.readlines()

    for line in data:
        table = str.maketrans(dict.fromkeys(string.punctuation))
        new_line = line.translate(table)  # clear all punctuation
        new_line = new_line.replace('\t', ' ')
        words = new_line.replace('\n', '')
        lines.append(words)

        for whole_line in lines:
            word = whole_line.split()
            result_word = [w for w in word if w.lower() not in word_list]
            result_word = ' '.join(result_word)
        result_word = result_word.split(' ', 1)[1]
    compare()


def parse_student(file2):
    global result_word
    data = file2.readlines()
    for line in data:
        table = str.maketrans(dict.fromkeys(string.punctuation))
        new_line = line.translate(table)  # clear all punctuation
        word = new_line.split()
        result_word = [w for w in word if w.lower() not in word_list]  # clear some words not need
        result_word = ' '.join(result_word)
        student_id = result_word.split(' ', 1)[0]  # get student id
        student_answer = result_word.split(' ', 1)[1]  # get student answer
        d[student_id].append(
            student_answer)  # using dict method(key:value) student_id is the key, the student answer is value.
    return

# compare word by word
# compare with one line
def compare():
    global result_word
    word1 = result_word.split()

    for key, value in d.items():
        for word3 in value:
            word = word3.split()
            with open('outfile.txt', 'a') as output:
                output.write('\nstudent id: {}\n'.format(key))
                output.write('combine key_string in one line:\n')
            main_comparison(word1, word)
            ratio = SequenceMatcher(None, result_word, word3).ratio()
            with open('outfile.txt', 'a') as output:
                output.write('ratio of two sentece are {}.\n'.format(ratio))


def student_id():
    global word4
    for key, value in d.items():
        with open('outfile.txt', 'a') as output:
            output.write('\nstudent id: {}\n'.format(key))
        for word in value:
            word4 = word.split()
            compare_four_part()


def compare_four_part():
    global part1, part2, part3, part4, word4

    for word_i in part1:
        with open('outfile.txt', 'a') as output:
            output.write('part 1: \n')
        main_comparison(word_i, word4)
    for word_i in part2:
        with open('outfile.txt', 'a') as output:
            output.write('part 2: \n')
        main_comparison(word_i, word4)
    for word_i in part3:
        with open('outfile.txt', 'a') as output:
            output.write('part 3: \n')
        main_comparison(word_i, word4)
    for word_i in part4:
        with open('outfile.txt', 'a') as output:
            output.write('part 4: \n')
        main_comparison(word_i, word4)

    # return student_id()


def set_output_path(path1, path2):
    if path1.lower().find('key') >= 0:
        return path2.replace('.txt', '.student-diff-from-key.txt')
    elif path2.lower().find('key') >= 0:
        return path1.replace('.txt', '.student-diff-from-key.txt')
    else:
        return ''
