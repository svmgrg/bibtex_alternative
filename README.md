# bibtex_alternative

A very simple LaTeX package, called **dumbib** for bibliography management.

This repository contains
- the dumbib LaTeX package ``.sty`` file
- the ``create_dumbib_database.py`` Python script, which can be used to create a dumbib database from a BibTeX file, and its helper file called ``venue_list.csv``

For more information about the dumbib package and how to use it, please see its documentation file ``dumbib_user_guide.pdf``.

The script can be used as follows:

``$ python create_dumbib_database.py -in <input_bibtex_database.bib> -out <dumbib_database.tex>``

Running this command will extract the publication title, venue, author list, and year of publication from the BibTeX entries and arrange them in an alphabetical order (using the author names) in the dumbib database file. The format used is very close to APA, but has minor differences. The script also produces a log file with the same name as the output file and a ``.log`` extension.