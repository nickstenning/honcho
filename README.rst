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

Honcho is a Python port of Foreman_, a tool for managing Procfile-based applications.

`Why a port? <//honcho.readthedocs.org/en/latest/#why-did-you-port-foreman>`_

.. _Foreman: http://ddollar.github.com/foreman

.. |Build Status| image:: https://secure.travis-ci.org/nickstenning/honcho.png?branch=master
   :target: http://travis-ci.org/nickstenning/honcho

Installing Honcho
-----------------

::

    pip install honcho

If you're one of those sick people who's into this kind of thing, you
can probably also ``easy_install honcho``. But please, don't: `get with
the program`_.

.. _get with the program: http://www.pip-installer.org/en/latest/index.html

How to use Honcho
-----------------

The 30-second version:

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

3. Run the app with Honcho::

    $ honcho start

.. _a Procfile: https://devcenter.heroku.com/articles/procfile
.. _to configure your app: http://www.12factor.net/config

For more detail and an explanation of the circumstances in which Honcho might
be useful, consult the `Honcho documentation`_.

.. _Honcho documentation: //honcho.readthedocs.org/

License
-------

Honcho is released under the terms of the MIT license, a copy of which can be
found in ``LICENSE``.
