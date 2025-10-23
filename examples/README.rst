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

simple 
---------

.. code-block:: bash

    $ python simple.py

rediscli
-----------------

Use with mock redis server.

.. code-block:: bash
    
    $ python rediscli.py

go to http://localhost:5000/admin/rediscli/

if you want to use real redis server, then do this:

1. First install redis,

.. code-block:: bash

    $ pip install redis

2. Modify code in ``rediscli.py``

.. code-block:: python

    # from flask_exts.views.rediscli.mock_redis import MockRedis as Redis
    from redis import Redis

3. At last, run  ``python rediscli.py``

demo
-----------------

Default admin user is ``admin``, password is ``admin``.

.. code-block:: bash
    
    $ flask --app demo run

fileadmin
-----------------

.. code-block:: bash
    
    $ flask --app fileadmin run

Bootstrap
-----------------

.. code-block:: bash

    $ flask --app bootstrap run

