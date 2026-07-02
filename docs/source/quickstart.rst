Quickstart
==========

Create a client, build a query object, and call one of the endpoint objects:

.. code-block:: python

   from jp_diet_search import DietClient
   from jp_diet_search.queries import SpeechQuery

   client = DietClient(cache_dir=".cache")

   query = SpeechQuery(
       any="科学技術",
       maximum_records=100,
   )

   result = client.speech.search(query, limit_total=5)

   print(result["numberOfRecords"])
   for record in result.get("records", []):
       print(record.get("speaker"), record.get("date"))

Endpoints
---------

The client exposes one object per API endpoint:

.. code-block:: python

   client.meeting_list.search(MeetingListQuery(...))
   client.meeting.search(MeetingQuery(...))
   client.speech.search(SpeechQuery(...))

Search methods return raw JSON dictionaries aggregated across pages.
