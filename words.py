from collections import Counter
from multiprocessing.dummy import Pool
from functools import partial
from time import time
def generate_stripmap():
    "Returns a dictionary (map of keys to values) of punctuation and whitespace characters to be removed from strings. This function uses the constants provided by Python's string module."
    import string
    res={}
    #Where our map of values to delete will go. We will return this value.
    #Add values for punctuation characters to the dictionary, but preserve ' since it is used in English contractions, and convert - to space to count hyphanated phrases as their components.
    for char in string.punctuation:
        if ord(char) != 39 and ord(char) != 45:
            res[ord(char)]=None
    for char in string.whitespace:
        res[ord(char)]=None
    res[45]=32
    return res

def analyze(file,mode=None,stripmap=None):
    "This function analyzes a plane text file, optionally skipping Gutenberg/Wikipedia header and footer, and returns a dictionary (mapping of keys to values) of words to their frequencies. A map of characters to strip from each word may also be provided for efficiency purposes if calling this function multiple times (as we do for this experiment), but if none is provided it will be generated before processing."
    #If we don't have a stripmap, generate one.
    if stripmap==None:
        stripmap=generate_stripmap()
    #We need to determine the character encoding of the file for processing.
    import chardet
    enc=chardet.detect(open(file,'br').read())['encoding']
    #Fin is the file object. We will open it using the detected encoding to collect its text (sans headers if Gutenberg), then close it.
    fin=open(file,encoding=enc,errors='ignore')
    #words is an empty list which we will populate with all words from the source text.
    words=[]
    if mode=='Gutenberg':
        from gutenberg.cleanup import strip_headers
        text=strip_headers(''.join(fin.readlines()))
    elif mode=='Wikipedia':
        text=''
        for line in fin:
            if "<doc" not in line and "</doc" not in line:
                text+=line
    else:
        text=''.join(fin.readlines())
    fin.close()
    #The text we've extracted is full of punctuation, capitalization, and newlines which are undesirable for our purposes. We just want the words.
    for word in text.split():
        words.extend(word.translate(stripmap).lower().split())
    #Analyze words, and generate our frequency map.
    return Counter(words)

def get_top_words(map,max=100,csvpath="out.csv"):
    "Get the most frequently occurring words from a dictionary in the form returned by analyze. By default, it saves its results to out.csv in the current directory, but you may optionally pass a different path. A maximum number of top words to print may also be specified, 100 by default since this experiment will use the top 100 words. Returns None."
    #Set up csv processing
    import csv
    #Create a file object where the csv data will be written
    fout=open(csvpath,'w')
    #And a writer object to write the data in csv format to the file.
    writer=csv.writer(fout)
    writer.writerow(("word","frequency"))
    #Use the most_common method on Counter to generate the list, and write to CSV.
    for word,freq in map.most_common(max):
        writer.writerow((word,str(freq)))
    fout.close()

if __name__ == '__main__':
    import os
    print("Generating stripmap...")
    sm=generate_stripmap()
    pgpaths=[]
    print("Walking Gutenberg directory tree...")
    if not os.path.exists("Gutenberg"):
        raise OSError("Cannot find Gutenberg directory")
    for root,dirs,files in os.walk("Gutenberg"):
        for file in files:
            pgpaths.append(root+"/"+file)
    print("Found",len(pgpaths),"files.")
    wppaths=[]
    print("Walking Wikipedia directory tree...")
    if not os.path.exists("Wikipedia"):
        raise OSError("Cannot find Wikipedia directory")
    for root,dirs,files in os.walk("Wikipedia"):
        for file in files:
            wppaths.append(root+"/"+file)
    print("Found",len(wppaths),"files.")
    #Calculate the total number of files to analyze.
    total=len(pgpaths)+len(wppaths)
    print("A total of",total,"files to analyze. Starting Gutenberg analysis...")
    #Create a Pool for multiprocessing.
    pool=Pool()
    print("In multiprocessing mode, using " + str(pool._processes) + " threads.")
    #Analyze Project Gutenberg
    pgstart=time()
    print("Starting Project Gutenberg Analysis…")
    pgres=pool.map(partial(analyze,mode="Gutenberg",stripmap=sm),pgpaths)
    pgend=time()
    print("Project Gutenberg analysis took " + str(pgend-pgstart) + " seconds. Starting Wikipedia…")
    #Analyze Wikipedia
    wpstart=time()
    wpres=pool.map(partial(analyze,mode="Wikipedia",stripmap=sm),wppaths)
    wpend=time()
    print("Done. Wikipedia analysis took " + str(wpend-wpstart) + " seconds. The experiment in total took " + str(wpend-pgstart) + " seconds.")
    print("Consolidating results...")
    res=Counter()
    for i in pgres:
        res+=i
    for i in wpres:
        res+=i
    print("Generating CSV of top 100 words...")
    get_top_words(res)
    print("Experiment complete.")
