Exporting
=========

Honcho allows you to export your Procfile configuration into other formats::

  $ honcho export OPTIONS FORMAT LOCATION

Currently only ``upstart`` and ``supervisord`` formats are supported.

Options
-------

::

    -s SHELL, --shell SHELL
        Specify the shell that should run the application.
        Only used for upstart.

    -u USER, --user USER
        Specify the user the application should be run as.

    -a APP, --app APP
        Specify the name of the application you are going to export.

    -c process=num,process=num, --concurrency process=num,process=num
        Specify the number of each process type to run.

    -p N, --port N
        Specify which port to use as the base for this application.
        Should be a multiple of 1000.

    -l DIR, --log DIR
        Specify the directory to place process logs in.

    -t TEMPLATE, --template TEMPLATE
        Specify alternate template to use for creating export files.


Examples
--------

Before exporting, you need to make sure that your user has an access to
:file:`/var/log/{APP}` folder.

The following command will create a :file:`honcho.conf` file in the :file:`/etc/supervisor/conf.d/` directory.

::

    $ honcho export -c web=1,worker=2,worker_low=1 -a honcho supervisord /etc/supervisor/conf.d/ 

When exporting to upstart, each process gets its own .conf file.

::

    $ honcho export -c web=1,worker=2,worker_low=1 -a honcho upstart /etc/init


Adding New Export Format Support
--------------------------------

You can support new export formats by writing plugins. Honcho discovers
export plugins with the `entry points mechanism`_ of setuptools.

First, you need to write a class inherited from :class:`honcho.export.base.BaseExport`
and override the :meth:`~honcho.export.base.BaseExport.render` method. Inside
the :meth:`~honcho.export.base.BaseExport.render` method, you could locate your
Jinja2 template file using something like:

.. code-block:: python

    self.get_template('foo.html', __package__, 'data/templates')

There are some existing export classes which could be consulted -- e.g.:

* :class:`honcho.export.supervisord.Export`
* :class:`honcho.export.upstart.Export`

Next, you can create a :file:`setup.py` file for building a package, and specify
the new export classes in the ``entry_points`` section. For
example:

.. code-block:: python

    from setuptools import setup

    setup(
        name='honcho-foo',
        ...
        entry_points={
            'honcho_exporters': [
                'honcho_foo.export.foo:FooExport',
                'honcho_foo.export.foobar:FooBarExport',
            ],
        },
    )

After installing the package, the new export format will be shown by the
``honcho export`` command.

.. _`entry points mechanism`: https://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins
