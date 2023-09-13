import os
import random
import re
import sys
from copy import deepcopy

DAMPING = 0.85
SAMPLES = 10000

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    # corpus = crawl("corpus2")
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )
    # print(pages)
    return pages


def transition_model(corpus: dict, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    prob = dict()
    N = len(corpus.keys())
    # print(page)
    # print(corpus[page])
    if len(corpus[page])==0:
        probab = 1 / N
        for key in corpus.keys():
            prob[key] = probab

    else:
        addedprobab = (1 - damping_factor) / N
        valueN = len(corpus[page])
        for key in corpus.keys():
            prob[key] = addedprobab
        for link in corpus[page]:
            prob[link] += 0.85/valueN

    return prob
    
        
def sample_pagerank(corpus: dict, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page = random.choice(list(corpus.keys()))
    # print(page)
    rank = dict()
    for key in corpus.keys():
        rank[key] = 0

    for _ in range(n):
        transprob = transition_model(corpus, page, damping_factor)
        pagelist = list(transprob.keys())
        weight = []
        for key in transprob.keys():
            weight.append(transprob[key])

        rank[page] += 1

        plist = random.choices(pagelist, weight)
        page = plist[0] 
    
    for page in rank.keys():
        rank[page] = rank[page] / n

    return rank

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    rank = dict()
    newrank = dict()
    for key in corpus.keys():
        rank[key] = 0
        newrank[key] = 0
    
    N = len(corpus.keys())

    for key in rank:
        rank[key] = 1/N
    # print(rank)

    while True:
        for page_p in corpus.keys():
            prob = 0
            for page_i in corpus.keys():
                if len(corpus[page_i]) == 0:
                    prob += damping_factor*(rank[page_i]/N)
                elif page_p in corpus[page_i]:
                    prob += damping_factor*(rank[page_i]/(len(corpus[page_i]))) 

            prob += (1 - damping_factor) / N
            newrank[page_p] = prob

        differencelist = [abs(newrank[key] - rank[key]) for key in corpus.keys()]
        # print(newrank)
        maxdiff = max(differencelist)

        if maxdiff<0.001:
            break
        
        rank = deepcopy(newrank)
        newrank = dict()
            
    return rank

if __name__ == "__main__":
    main()
