Translations
============

src
---

pybabel::

    # extract messages from source files and generate a POT file
    pybabel extract -F babel.cfg -o babel/messages.pot src/

    # create new message catalogs from a POT file
    pybabel init -i babel/messages.pot -d src/flask_exts/translations -D messages -l en
    pybabel init -i babel/messages.pot -d src/flask_exts/translations -D messages -l zh_CN

    # update existing message catalogs from a POT file
    pybabel update -i babel/messages.pot -d src/flask_exts/translations -D messages 

    # edit
    # open the '.po' file

    # compile message catalogs to MO files

    $ pybabel compile -d src/flask_exts/translations -D messages 


tests
-----

pybabel::


    cd tests/

    # extract messages from source files and generate a POT file
    pybabel extract -o translations/messages.pot .

    # create new message catalogs from a POT file
    pybabel init -i translations/messages.pot -d translations -l en
    pybabel init -i translations/messages.pot -d translations -l zh_CN

    # update existing message catalogs from a POT file
    pybabel update -i translations/messages.pot -d translations

    # edit
    # open the '.po' file

    # compile message catalogs to MO files

    pybabel compile -d translations





