"""Words That Can't be Strangled
Copyright 2015-2016 William Dengler
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""
from collections import Counter
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

def get_cache_filename(file):
    "Gets the cache filename for a file path."
    import os
    return os.path.join(os.path.split(file)[0],os.path.splitext(os.path.split(file)[1])[0])+".cache"
def analyze(file,mode=None,stripmap=None,verbose=False,nocache=False):
    "This function analyzes a plane text file, optionally skipping Gutenberg/Wikipedia header and footer, and returns a dictionary (mapping of keys to values) of words to their frequencies. A map of characters to strip from each word may also be provided for efficiency purposes if calling this function multiple times (as we do for this experiment), but if none is provided it will be generated before processing. Passing \'verbose=True\' will print the path of the file that is currently being analyzed, useful for interactive mode. Passing \'nocache=True\' disables caching with pickle."
    if not nocache:
        import pickle
        if os.path.exists(get_cache_filename(file)):
            #Cache already exists.
            if verbose:
                print("Loading cache from " + get_cache_filename(file))
            with open(get_cache_filename(file),"rb") as fin:
                return pickle.load(fin)
    if verbose:
        print("Analyzing",file)
    #If we don't have a stripmap, generate one.
    if stripmap==None:
        stripmap=generate_stripmap()
    #We need to determine the character encoding of the file for processing.
    import chardet
    enc=chardet.detect(open(file,'br').read())['encoding']
    #Fin is the file object. We will open it using the detected encoding to collect its text (sans headers if Gutenberg), then close it.
    with open(file,encoding=enc,errors='ignore') as fin:
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
    #The text we've extracted is full of punctuation, capitalization, and newlines which are undesirable for our purposes. We just want the words.
    for word in text.split():
        words.extend(word.translate(stripmap).lower().split())
    #Analyze words, and generate our frequency map.
    res = Counter(words)
    if not nocache:
        import pickle
        with open(get_cache_filename(file),"wb") as cam:
            pickle.dump(res,cam)
    return res
def get_top_words(map,max=100,csvpath="out.csv"    "Get the most frequently occurring words from a dictionary in the form returned by analyze. By default, it saves its results to out.csv in the current directory, but you may optionally pass a different path. A maximum number of top words to print may also be specified, 100 by default since this experiment will use the top 100 words (pass \'0\' for all words). Returns None."
    #handle max=0
    if max == 0:
        max=None
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
    #parse command-line arguments
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("-w","--words",help="specify the number of words to include in the csv file, \'0\' for all.",default=100,type=int)
    parser.add_argument("-r","--workers",help="The number of processes/threads to spawn when in parallel mode. Default is number of processor cores.",type=int)
    parser.add_argument("-nc", "--no-cache", help="do not store caches.",action="store_true")
    threadgroup=parser.add_mutually_exclusive_group()
    threadgroup.add_argument("-t","--threaded",help="Run analysis in multiple threads (for efficiency).",action="store_const",dest="parallel",const="threaded")
    threadgroup.add_argument("-p","--parallel",help="Run analysis in multiple processes (for efficiency).",action="store_const",dest="parallel",const="parallel")
    threadgroup.add_argument("-n","--no-parallelism",help="Run analysis one-at-a-time (slower).",action="store_const",dest="parallel",const=None)
    parser.set_defaults(parallel='threaded')
    args=parser.parse_args()
    if not args.no_cache:
        import pickle
    if args.parallel == "threaded":
        from multiprocessing.dummy import Pool
    if args.parallel == "parallel":
        from multiprocessing import Pool
    #Print copyright notice
    print("Words That Can't be Strangled\nCopyright 2015-2016 William Dengler\nThis program is free software: you can redistribute it and/or modify\nit under the terms of the GNU General Public License as published by\nthe Free Software Foundation, either version 3 of the License, or\n(at your option) any later version.\nThis program is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\nGNU General Public License for more details.\nYou should have received a copy of the GNU General Public License\nalong with this program.  If not, see <http://www.gnu.org/licenses/>.")
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
    print("A total of",total,"files to analyze.")
    #Create a Pool for multiprocessing.
    if not args.parallel ==None:
        if args.workers != None:
            pool=Pool(args.workers)
        else:
            pool=Pool()
        if args.parallel == "threaded":
            unit="threads"
        elif args.parallel == "parallel":
            unit="processes"
        print("In parallel mode, using " + str(pool._processes) + " " + unit + ".")
    if args.no_cache:
        print("Caching disabled.")
    else:
        print("Caching enabled.")
    #Analyze Project Gutenberg
    pgstart=time()
    print("Starting Project Gutenberg Analysis…")
    if args.parallel == None:
        map_func=map
    else:
        map_func=pool.map
    pgres=map_func(partial(analyze,mode="Gutenberg",stripmap=sm,verbose=True,nocache=args.no_cache),pgpaths)
    pgend=time()
    print("Project Gutenberg analysis took " + str(pgend-pgstart) + " seconds. Starting Wikipedia…")
    #Analyze Wikipedia
    wpstart=time()
    wpres=map_func(partial(analyze,mode="Wikipedia",stripmap=sm,verbose=True,nocache=args.no_cache),wppaths)
    wpend=time()
    print("Done. Wikipedia analysis took " + str(wpend-wpstart) + " seconds. The experiment in total took " + str(wpend-pgstart) + " seconds.")
    print("Consolidating results...")
    res=Counter()
    pgtotal=len(pgres)
    pgcount=0
    while len(pgres) > 0:
        i=pgres.pop()
        pgcount+=1
        print("Consolidating",pgcount,"of",pgtotal,"Project Gutenberg files.")
        res+=i
    print("Project Gutenberg consolidation complete.")
    wptotal=len(wpres)
    wpcount=0
    while len(wpres) > 0:
        i=wpres.pop()
        wpcount+=1
        print("Analyzing",wpcount,"of",wptotal)
        res+=i
    print("Generating CSV...")
    get_top_words(res,max=args.words)
    print("Experiment complete.")
