=======
Develop
=======

English / 中文
----------------
This page is provided in English with a Chinese summary for easier reading.
中文说明：本页面保留英文原文，并附带中文说明，便于中英文对照阅读。

English summary: This guide explains how to install the project for development, run the test suite, build the docs, and manage translations with Babel.
中文说明：本指南说明如何在开发环境中安装项目、运行测试、构建文档以及使用 Babel 管理国际化翻译。

Install
=======

.. code-block:: console

    $ pip install -e .
    $ pip install -r requirements/develop.in

Test
====
Tests are run with `pytest <https://pytest.org/>`_.
To run the tests, from the project directory:

.. code-block:: console

    # requirements
    $ pip install -r requirements/test.in    

    # update translation
    $ pybabel compile -d src/flask_exts/translations -D messages
    $ pybabel compile -d tests/translations
    
    # test
    $ pytest

Docs
====

.. code-block:: console

    $ pip install -r docs/requirements.txt
    $ cd docs
    $ make html

Publish
=======

.. code-block:: console

    $ pip install -r requirements/build.in
    $ python -m build

Translation
=============

pybabel
-------------

.. code-block:: console

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
