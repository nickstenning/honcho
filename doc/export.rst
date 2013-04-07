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
