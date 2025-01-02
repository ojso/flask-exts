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
    

Run the applications
==========================

Type the command in the terminal, then go to http://localhost:5000.

Start
----------

.. code-block:: bash

    $ flask --app start run --debug --port=5000

Bootstrap 4
-----------------

.. code-block:: bash

    $ flask --app bootstrap4/app.py run

Bootstrap 5
-----------------

.. code-block:: bash
    
    $ flask --app bootstrap5/app.py run

admin
-----------------

.. code-block:: bash
    
    $ flask --app admin/simple run

