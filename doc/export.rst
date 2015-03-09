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

    -t DIR, --template-dir DIR
        Specify alternate template directory to use for creating export files.


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

You can add support for new export formats by writing plugins. Honcho discovers
export plugins with the `entry points mechanism`_ of setuptools. Export plugins
take the form of a class with ``render`` and ``get_template_loader`` methods
that inherits from :class:`honcho.export.base.BaseExport`. Inside the
:meth:`~honcho.export.base.BaseExport.render` method, you can fetch templates
using the `~honcho.export.base.BaseExport.get_template` method.

For example, here is a hypothetical exporter that writes out simple shell
scripts for each process:

.. code-block:: python

    import jinja2

    from honcho.export.base import BaseExport

    class SimpleExport(BaseExport):
        def get_template_loader(self):
            return jinja2.PackageLoader(package_name=__package__,
                                        package_path='templates')

        def render(self, processes, context):
            tpl = get_template('run.sh')

            for p in processes:
                filename = 'run-{0}.sh'.format(p.name)
                ctx = context.copy()
                ctx['process'] = p
                script = tpl.render(ctx)

By writing an exporter in this way (specifically, by inheriting
:class:`~honcho.export.base.BaseExport`), you make it possible for users of your
exporter to override the exporter's default templates using the
``--template-dir`` option to ``honcho export``.

In order for your export plugin to be detected by Honcho, you will need to
register your exporter class under the ``honcho_exporters`` entrypoint. If we
were shipping our hypothetical ``SimpleExport`` class in a package called
``honcho_export_simple``, our ``setup.py`` might look something like the
following:

.. code-block:: python

    from setuptools import setup

    setup(
        name='honcho_export_simple',
        ...
        entry_points={
            'honcho_exporters': [
                'simple=honcho_export_simple:SimpleExport',
            ],
        },
    )

After installing the package, the new export format will be shown by the
``honcho export`` command.

.. _`entry points mechanism`: https://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins
