.. _index:

jp-diet-search documentation
============================

``jp-diet-search`` is a Python client and command line tool for the
National Diet Library Minutes Search API
(``国会会議録検索システム``).

The package provides:

- an object-oriented client for the ``meeting_list``, ``meeting``, and
  ``speech`` endpoints;
- typed query objects with validation;
- safe pagination with optional total caps;
- optional on-disk response caching;
- JSON output from the command line.

Getting started
---------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   cli

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api/index
   development
   changelog
