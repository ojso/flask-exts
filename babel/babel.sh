# extract messages from source files and generate a POT file
pybabel extract -F babel/babel.cfg -k lazy_gettext -o babel/messages.pot --project Flask-Exts src/flask_exts/ tests/

# update PO files from a POT file
pybabel update -i babel/messages.pot -d src/flask_exts/translations -D messages

# compile message catalogs to MO files
pybabel compile -f -D messages -d src/flask_exts/translations/

