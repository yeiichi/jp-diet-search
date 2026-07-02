Development
===========

Set up the package in editable mode and run the test suite:

.. code-block:: console

   uv sync --group dev
   uv run --group dev pytest

Build the documentation locally:

.. code-block:: console

   uv run --extra docs sphinx-build -b html -W docs/source docs/build/html
