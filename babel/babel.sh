#!/bin/sh
pybabel extract -F babel.cfg -o messages.pot --project Flask-Exts ../src/flask_exts
pybabel compile -f -D messages -d ../src/flask_exts/translations/

# docs
cd ..
make gettext
cp build/locale/*.pot babel/
sphinx-intl update -p build/locale/ -d flask_exts/translations/
