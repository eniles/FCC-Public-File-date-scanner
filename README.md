# FCC-Public-File-date-scanner
A python tool for looking for dates (and maybe other strings) in the FCC Public File pages.  This is a WIP!
At this point it's very dumb, it just looks for text strings in the PDF and will help you narrow down what files to look at.
There is no real parsing of the data and it doesn't help figure out which file in a folder is a "good" match when there are multiple revisions.

probably need to run: pip install requests beautifulsoup4 PyPDF2
