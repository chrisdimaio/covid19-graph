#! /usr/bin/sh

# A temporary way to build Lambda zip without exceeding 10mb.

cd ../venv/lib/python3.7/site-packages/

zip -r9 ${OLDPWD}/covid19_graph.zip requests*
zip -r9 ${OLDPWD}/covid19_graph.zip chardet*
zip -r9 ${OLDPWD}/covid19_graph.zip certifi*
zip -r9 ${OLDPWD}/covid19_graph.zip idna*

cd $OLDPWD
zip -g covid19_graph.zip lambda_function.py