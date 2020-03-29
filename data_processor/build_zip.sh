#! /usr/bin/sh

cd ../venv/lib/python3.7/site-packages/

zip -r9 ${OLDPWD}/covid19_graph2.zip requests*
zip -r9 ${OLDPWD}/covid19_graph2.zip chardet*
zip -r9 ${OLDPWD}/covid19_graph2.zip certifi*
zip -r9 ${OLDPWD}/covid19_graph2.zip idna*

cd $OLDPWD
zip -g covid19_graph2.zip lambda_function.py