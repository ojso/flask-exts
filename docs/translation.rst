Translations
============

src
---

pybabel::

    # extract messages from source files and generate a POT file
    pybabel extract -F babel.cfg -o src/flask_exts/translations/admin.pot src/

    # create new message catalogs from a POT file
    pybabel init -i src/flask_exts/translations/admin.pot -d src/flask_exts/translations -D admin -l en
    pybabel init -i src/flask_exts/translations/admin.pot -d src/flask_exts/translations -D admin -l zh_CN

    # update existing message catalogs from a POT file
    pybabel update -i src/flask_exts/translations/admin.pot -d src/flask_exts/translations -D admin 

    # edit
    open the '.po' file

    # compile message catalogs to MO files

    $ pybabel compile -d src/flask_exts/translations -D admin 


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
    open the '.po' file

    # compile message catalogs to MO files

    pybabel compile -d translations





