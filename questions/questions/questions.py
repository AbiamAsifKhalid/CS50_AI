import nltk
import sys
import os
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1
# nltk.download('stopwords')

def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """

    filedict =  dict()
    for files in os.listdir(directory):
        with open(os.path.join(directory,files), "r", encoding="utf8") as data:
            filedict[files]=data.read()
    
    return filedict

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    words = nltk.tokenize.word_tokenize(document)
    wordlist =[]
    for word in words:
        if word.isalpha():
            if word not in nltk.corpus.stopwords.words("english"):
                wordlist.append(word.lower())
    return wordlist


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    idf_values =  dict()
    totaldocuments = len(documents.keys())
    setofwords = set()
    for words in documents.values():
        for word in words:
            setofwords.add(word)

    for word in setofwords:
        count = 0
        for document in documents.keys():
            if word in documents[document]:
                count+=1

        idf_values[word] = math.log(totaldocuments/count)

    return idf_values

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    topfiledict = dict()
    for document in files.keys():
        sentscore = 0
        for word in files[document]:
            if word in query:
                wordcount = files[document].count(word)
                sentscore += wordcount * idfs[word]

            if sentscore:
                topfiledict[document] = sentscore
        
    
    sortedlist = [k for k, v in sorted(topfiledict.items(), key= lambda x: x[1], reverse=True)]
    
    return sortedlist[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    topsentdict = dict()
    for sentence in sentences.keys():
        sentscore = 0
        for word in sentences[sentence]:
            if word in query:
                sentscore += idfs[word]

            if sentscore:
                countlist = [sentences[sentence].count(x) for x in query]
                density = sum(countlist)/ len(sentences[sentence])
                topsentdict[sentence] = (sentscore,density)
        
    
    sortedlist = [k for k, v in sorted(topsentdict.items(), key= lambda x: (x[1][0], x[1][1]), reverse=True)]
    return sortedlist[:n]

if __name__ == "__main__":
    main()
