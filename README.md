#Words That Can't Be Strangled
Words That Can't Be Strangled was a project entered into the [Sea Island Regional Science Fair](http://sirsf.org). The purpose of the project was to determine the top 100 most frequently used English words, based on the text of [Project Gutenberg](http://gutenberg.org) and the [English Wikipedia](http://en.wikipedia.org). This repository contains the program I wrote to run the experiment and instructions to reproduce the experiment using your own setup.

I have released this program as [free software](http://www.gnu.org/philosophy/free-sw.en.html) in the hope that it will be useful, but without warranty of any kind. See [the license](copying.txt) for more information. If you make improvements to this program, I encourage you to fork this repository and send me a pull request with your changes.

##Things you'll need
* Computer with sufficient resources to run the analysis uninterrupted (I used a dedicated cloud instance from [Vultr](http://vultr.com)) running [Ubuntu GNU/Linux](http://ubuntu.com) 14.04.
* [Python](http://python.org) interpreter, both version 2 and 3 (this program is written in Python 3, but Wikiextractor is written in 2)
* A clone of this repository.
* Complete contents of [Project Gutenberg](http://gutenberg.org), several gigabytes in size.
* `gutenberg` and `chardet` packages for Python 3
* [A database dump of the English Wikipedia](http://dumps.wikimedia.org/enwiki) (I used the September 1, 2015  dump), again, several gigabytes in size.
* Spreadsheet software capable of reading files in .csv format.
* `zip` and `unzip` packages

##running the experiment
These instructions have been written for [Debian](http://debian.org)-based Gnu/Linux distributions such as [Ubuntu](http://ubuntu.com), but these procedures could easily be run on any platform, as long as the necessary software is available.
###Cloning the repository
1. Clone the repository using `git` with the following command:

		git clone https://github.com/codeofdusk/words.git

2. Change to the `words` directory with the following command (we will be working inside this directory from now on):

		cd words

####A note on branches
The `master` branch of this repository contains `words.py` with some improvements, notably multithreading support and the usage of the built-in `Counter` datatype as opposed to the `dict` datatype with manual counting. The `master` branch has not been extensively tested. The `original` branch contains the code originally entered into the [Sea Island Regional Science Fair](http://sirsf.org) which has only been modified to show a GPL3 notice on launch.

To use the `original` branch, run the following command from inside the `words` directory:

	git checkout original

By default, `git` will checkout the `master` branch, so no additional commands are necessary to proceed on that branch. Of course, doing a `git checkout master` will switch to the master branch if you are on another.

###Preparing Wikipedia data
1. Download the Wikipedia database dump taken on September 1, 2015 using the following command:

		wget -b http://dumps.wikimedia.org/enwiki/20150901/enwiki-20150901-pages-articles.xml.bz2
The -b switch causes the download to run in the background, as it takes a while and is several gigabytes in size. Run `tail -f wget-log` to monitor progress. Run `rm wget-log` when the download completes to remove the log file as it is not part of the data to be analyzed.
2. Decompress the Wikipedia database dump with the following command:

		bunzip2 enwiki-20150901-pages-articles.xml.bz2
3. Download WikiExtractor, a script which extracts text from Wikipedia dumps, with the following command:

		wget http://medialab.di.unipi.it/Project/SemaWiki/Tools/WikiExtractor.py
4. Run the script (using nohup so it can run even while disconnected from SSH as it takes a while) with the following command:

		nohup python2 Wikiextractor.py --output Wikipedia --no-templates enwiki-20150901-pages-articles.xml &
Monitor the log with tail:

		tail -f nohup.out
And when it has stopped, delete the log as it is not part of the data to be analyzed:

		rm nohup.out
5. Delete the Wikipedia xml dump (since the text has already been extracted) with the following command:

		rm enwiki-20150901-pages-articles.xml
and WikiExtractor:

		rm WikiExtractor.py

###Preparing Project Gutenberg texts for analysis
1. Download all English texts from Project Gutenberg (very large) with the following command (based on an example from [here](http://www.gutenberg.org/wiki/Gutenberg:Information_About_Robot_Access_to_our_Pages)):

		wget -w 0.5 -b -m -H "http://www.gutenberg.org/robot/harvest?filetypes[]=txt&langs[]=en"
This download will run in the background, run `tail -f wget-log` to monitor progress. Run `rm wget-log` when the download completes to remove the log file as it is not part of the data to be analyzed.
2. Remove the indexes (as they are not part of the data to be analyzed) with the following command:

		rm -rf www.gutenberg.org
3. Create a directory for the Gutenberg files with the following command:

		mkdir Gutenberg
4. Install unzip with the following command:

		apt-get install unzip
5. Change to the Gutenberg zips directory and recursively unzip its archives into words/Gutenberg. Run with nohup as a shell script, so it can unzip files in the background (based on [this Stack Overflow answer](http://stackoverflow.com/a/107999)):

		cd www.gutenberg.lib.md.us
		echo "find . -type f -name "*.zip" -print0 | xargs -0 -I{} unzip {} -d ../Gutenberg/" > unzip.sh
		chmod +x unzip.sh
		nohup ./unzip.sh &
Monitor progress with `tail -f nohup.out` and run `rm nohup.out` when done to delete log file as it is not part of the data to be analyzed.
6. Delete the zip archives as they are no longer needed:

		rm -rf www.gutenberg.lib.md.us

###Data analysis
1. Install the gutenberg and chardet package with the following commands:

		apt-get install python3-pip
		pip3 install Gutenberg chardet
2. Make words.py executable:

		chmod +x words.py
3. Run the program with the following command:

		nohup python3 -u words.py &
4. Copy the output file, "out.csv", to a machine with spreadsheet software and open it to view the results.

###Determining experiment start and end times
Note : if you are using the `master` branch, the program will print the duration of each analysis, so just view `nohup.out`. If you are using the `original` branch, the following steps apply:
1. Determine the experiment start time by finding the modified time of words.py with the following command (times will be in UTC unless system time is changed):

		stat words.py
2. Determine the experiment end time by finding the modified time of the final log file written by nohup with the following command (times will be in UTC unless system time is changed):

		stat nohup.out