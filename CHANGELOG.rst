Changelog
=========

All notable changes to this project will be documented in this file. This
project endeavours to adhere to `Semantic Versioning`_.

.. _Semantic Versioning: http://semver.org/

Unreleased
----------

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
