Command Line
============

The package installs the ``jp-diet-search`` command.

Examples
--------

Search speeches and print JSON to standard output:

.. code-block:: console

   jp-diet-search speech --any "科学技術" --limit-total 5 --no-ascii

Search meetings and write JSON to a file:

.. code-block:: console

   jp-diet-search meeting --any "予算" --limit-total 10 --output meetings.json

Commands
--------

``jp-diet-search`` provides subcommands for the supported API endpoints:

- ``meeting-list``
- ``meeting``
- ``speech``

Run ``jp-diet-search --help`` or ``jp-diet-search <command> --help`` for the
full set of options.
