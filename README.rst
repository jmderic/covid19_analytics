
###############
Covid Analytics
###############

This project processes data from the `John's Hopkins CSSE Covid-19
GitHub repository <https://github.com/CSSEGISandData/COVID-19>`_ and
creates plots and json data for publication on the `Covid-19 section
of the DericNet website <http://www.dericnet.com/covid7>`_.

It works in conjunction with a separate `Sphinx Covid project
<https://github.com/jmderic/sphinx_covid>`_.  That project consumes
the plots and json data created by this project and builds a `Sphinx
<https://www.sphinx-doc.org/>`_ website with data tables made from the
json and the plots.

The single command that engages both projects and generates the
website is the `update_website.sh script
<https://github.com/jmderic/covid19_analytics/blob/master/update_website.sh>`_
in this project.  

The script is full of hard-coded locations that are specific to this
author's directory structure; so the project is not currently well
productized.  It is published here for reference in the hope of
evolving a more generic, user friendly Python package.  And,
potentially one that combines it with the project in the second
paragraph.
