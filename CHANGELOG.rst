Changelog
=========

All notable changes to this project will be documented in this file. This
project endeavours to adhere to `Semantic Versioning`_.

.. _Semantic Versioning: http://semver.org/

Unreleased
----------

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
* FIXED: Addressed numerous text encoding bugs.
* FIXED: Honcho exporters can now be used on Python 3.2
* FIXED: Honcho no longer crashes when all processes are made ``--quiet``.
