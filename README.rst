::

         ___           ___           ___           ___           ___           ___     
        /\__\         /\  \         /\__\         /\  \         /\__\         /\  \    
       /:/  /        /::\  \       /::|  |       /::\  \       /:/  /        /::\  \   
      /:/__/        /:/\:\  \     /:|:|  |      /:/\:\  \     /:/__/        /:/\:\  \  
     /::\  \ ___   /:/  \:\  \   /:/|:|  |__   /:/  \:\  \   /::\  \ ___   /:/  \:\  \ 
    /:/\:\  /\__\ /:/__/ \:\__\ /:/ |:| /\__\ /:/__/ \:\__\ /:/\:\  /\__\ /:/__/ \:\__\
    \/__\:\/:/  / \:\  \ /:/  / \/__|:|/:/  / \:\  \  \/__/ \/__\:\/:/  / \:\  \ /:/  /
         \::/  /   \:\  /:/  /      |:/:/  /   \:\  \            \::/  /   \:\  /:/  / 
         /:/  /     \:\/:/  /       |::/  /     \:\  \           /:/  /     \:\/:/  /  
        /:/  /       \::/  /        /:/  /       \:\__\         /:/  /       \::/  /   
        \/__/         \/__/         \/__/         \/__/         \/__/         \/__/   

|Build Status|

So, uh, honcho is basically Foreman_, but uh, honcho instead.

Seriously? honcho is a Python port of Foreman.

Why a port? Well, only two good reasons, and only one of which you're
going to be interested in:

1. I work in Python-only development environments, where installing Ruby
   just so I can run Procfile apps seems a bit crazy. Python, on the
   other hand, is part of the LSB_, and so even in "Ruby-only"
   environments, Python will still be around.

2. I wanted to learn about `asynchronous I/O`_ `in Python`_.

.. _Foreman: http://ddollar.github.com/foreman
.. _LSB: http://en.wikipedia.org/wiki/Linux_Standard_Base
.. _asynchronous I/O: http://docs.python.org/library/select.html
.. _in Python: http://docs.python.org/library/queue.html

.. |Build Status| image:: https://secure.travis-ci.org/nickstenning/honcho.png?branch=master
   :target: http://travis-ci.org/nickstenning/honcho

How to get honcho
-----------------

::

    pip install honcho

If you're one of those sick people who's into this kind of thing, you
can probably also ``easy_install honcho``. But please, don't: `get with
the program`_.

.. _get with the program: http://www.pip-installer.org/en/latest/index.html

How to use honcho
-----------------

1. Read `the Foreman documentation`_
2. Run ``honcho -h`` and see which bits of Foreman I've got round to
   implementing

Or, the 30-second version:

1. Write `a Procfile`_::

    $ cat >Procfile <<EOM
    web: python serve.py
    redis: redis-server
    EOM

2. *Optional:* write a .env file `to configure your app`_::

    $ cat >.env <<EOM
    PORT=6000
    REDIS_URI=redis://localhost:6789/0
    EOM

3. Run the app with honcho::

    $ honcho start

.. _the Foreman documentation: http://ddollar.github.com/foreman/
.. _a Procfile: https://devcenter.heroku.com/articles/procfile
.. _to configure your app: http://www.12factor.net/config
