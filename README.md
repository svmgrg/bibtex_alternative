# bibtex_alternative

A minimalistic LaTeX package, called **dumbib** for bibliography management.

This repository contains
- the dumbib LaTeX package ``.sty`` file and its documentation ``dumbib_user_guide.pdf``
- the ``create_dumbib_database.py`` Python script, which can be used to create a dumbib database from a BibTeX file, and its helper file called ``venue_list.csv``

**For more information about the dumbib package and how to use it, please see the [documentation](https://github.com/svmgrg/bibtex_alternative/blob/main/dumbib_user_guide.pdf).**

The script can be used as follows:

``$ python create_dumbib_database.py -in <input_bibtex_database.bib> -out <dumbib_database.tex>``

Running this command will extract the publication title, venue, author list, and year of publication from the BibTeX entries and arrange them in an alphabetical order (using the author names) in the dumbib database file. The format used is very close to APA, but has minor differences. The script also produces a log file with the same name as the output file and a ``.log`` extension.

**Warning:** The Python script will write over ``<dumbib_database.tex>`` if it already exists. So if you make any changes manually to ``<dumbib_database.tex>``, and later run the Python script with the same output filename in the arguments, those changes will be lost.

**Acknowledgements:** Thanks to Mohamed Elsayed for providing the initial motivation to write this package and for subsequently testing it; thanks to Rupam Mahmood for additional encouragement; and thanks to Roshan Shariff for technical support with LaTeX.

**List of known bugs:** When a citation splits across a page, then everything in between (such as the footer on the first page and the header on the next page) becomes hyperlinked as well.