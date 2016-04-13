Changelog
=========

All notable changes to this project will be documented in this file. This
project endeavours to adhere to `Semantic Versioning`_.

.. _Semantic Versioning: http://semver.org/

0.7.1 -- 2016-04-13
-------------------

- FIXED: Honcho now correctly pays attention to the ``-f`` argument when
  provided before a command, fixing a regression introduced in the previous
  version. Thanks to Marc Krull for reporting and fixing.

0.7.0 -- 2016-04-10
-------------------

* ADDED: Honcho can now export to a `runit <http://smarden.org/runit/>`_ service
  directory.
* ADDED: You can now specify the location of the Procfile with a ``PROCFILE``
  environment variable.
* ADDED: Python 3.5 is now a supported environment.
* CHANGED: Python 3.0, 3.1, and 3.2 are no longer supported environments.
* FIXED: The ``run`` command now correctly parses commands which include the
  ``--`` "end of arguments" separator.
* FIXED: Honcho no longer fails to load ``.env`` files if the Procfile is not in
  the application directory.
* FIXED: ANSI colour codes from running programs can no longer interfere with
  Honcho's output.
* FIXED: Export of environment variables containing special characters no longer
  breaks the Upstart exporter.
* FIXED: The supervisord exporter now correctly escapes the % symbol in commands
  and environment variable values.

0.6.6 -- 2015-03-16
-------------------

* FIXED: Environment variables in ``.env`` files can, once again, contain
  backslash escapes.


0.6.5 -- 2015-03-09
-------------------

* ADDED: Exporter templates can now be overridden by the ``--template-dir``
  option to ``honcho export``.
* CHANGED: Colour output is now supported by default on Windows.
* CHANGED: Base port is no longer required to be a multiple of 1000.
* FIXED: Output is no longer buffered on Python 3.
* FIXED: Environment variables in ``.env`` files can now take any POSIX-valid
  values rather than simple alphanumerics only.

0.6.4 -- 2015-02-08
-------------------

* FIXED: Common arguments (``-f``, ``-d``, etc.) given before the subcommand
  (``start``, ``run``, etc.) are no longer ignored on Python 2.7.9.

0.6.3 -- 2015-02-07
-------------------

* CHANGED: The commandline ``-p/--port`` option now takes precedence over all
  other ways of setting the start port.

0.6.2 -- 2015-02-07
-------------------

* ADDED: Colour output is now supported on Windows when the ``colorama``
  package is installed.
* FIXED: Honcho no longer always crashes on Windows. Sorry about that.

0.6.1 -- 2015-02-07
-------------------

* CHANGED: Honcho is now release as a universal wheel package (with support for
  Python 2 and 3).

0.6.0 -- 2015-02-07
-------------------

* ADDED: Started keeping a changelog!
* ADDED: A version command: ``honcho version`` will print the current version.
* CHANGED: Supervisor export now executes commands inside a shell (like other
  exporters and honcho itself).
* CHANGED: Supervisor exports now sets PORT environment variable consistently
  with other exporters and the rest of honcho.
* CHANGED: Supervisor export now takes a directory as the location parameter on
  the command line, e.g. ``honcho export supervisord /etc/supervisord.d``, thus
  making the use consistent with other exporters. N.B. This is a
  backwards-incompatible change!
* FIXED: Addressed numerous text encoding bugs.
* FIXED: Honcho exporters can now be used on Python 3.2
* FIXED: Honcho no longer crashes when all processes are made ``--quiet``.
