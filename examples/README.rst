========================
Examples
========================

Download
=========

Type these commands in the terminal:

.. code-block:: bash

    $ git clone https://github.com/ojso/flask-exts.git
    $ cd flask-exts/examples
    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip install flask-exts

Run the examples
===============================

Type the command in the terminal, then go to http://localhost:5000.

Start
----------

simple 
---------

run only one file.

.. code-block:: bash

    $ python simple.py

demo
-----------------

With sqlite db.

.. code-block:: bash
    
    $ flask --app demo run --debug --port=5000

fileadmin
-----------------

.. code-block:: bash
    
    $ flask --app fileadmin run

rediscli
-----------------

First install redis,

.. code-block:: bash

    $ pip install redis

then run:

.. code-block:: bash
    
    $ flask --app rediscli run

go to http://localhost:5000/admin/rediscli/

Bootstrap 4
-----------------

.. code-block:: bash

    $ flask --app bootstrap4/app.py run

Bootstrap 5
-----------------

.. code-block:: bash
    
    $ flask --app bootstrap5/app.py run


