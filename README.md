Reprocess Socorro Crashes
=========================

Advanced tooling for what you have to process
[Socorro](https://crash-stats.mozilla.com) crashes that were saved
but never processed.


What You Need
-------------

* AWS credentials to the Socorro production S3 bucket where crashes are
saved.

* An [API Token](https://crash-stats.mozilla.com/api/tokens/) that
contains the `Reprocess Crashes` permission.


How It Works
------------

You need a list of dates (or just one) you know there might be crashes missing.
E.g. `20160915`. Note the date format.

You start by querying S3 for ALL crashes that were saved in that day.
That will create a file called `uuids.txt`

Next, this list is likely going to be huge and for convenience it's
easier to split this up into multiple files so you can run the next
step in multiple terminals at the same time since the next step is
highly network I/O bound.

Once you have the list of uuids files you query S3 for each UUID to
see if we have it processed. This will fill up a file called `haves.txt`
and `havenots.txt`.

Lastly you will, in batches to avoid overloading, take UUIDs out of
`havenots.txt` and send them in for processing.


A Note on "Processing" vs. "Reprocessing"
-----------------------------------------

When we send in crashes for processing we, confusingly, use the API endpoint
called `/api/Reprocessing/`. There is no API endpoint where you send a UUID
and it first does a conditional check.

This might change but it's unlikely since it's rare.


A Note On Dates
---------------

If you, for example, know that a bunch of crashes failed to be processed
on September 15 but you know it only failed during the window of
10:00:00 UTC to 13:45:00 UTC. You **can not filter by the hour** so
you have to query for the *whole day*.


Working Example
---------------

First figure out which dates you need and create the master list. Suppose
it was Sep 15-16 2016:

    $ python list.py AWS_ACCESS_KEY AWS_ACCESS_SECRET 20160915 201609

This creates a file called `uuids.txt`:

    $ wc -l uuids.txt
    373495 uuids.txt

Now let's break up this file in chunks of 50,000:

    $ python breakup.py uuids.txt 50000
    uuids-0-50000.txt
    uuids-50000-100000.txt
    uuids-100000-150000.txt
    uuids-150000-200000.txt
    uuids-200000-250000.txt
    uuids-250000-300000.txt
    uuids-300000-350000.txt
    uuids-350000-400000.txt

Check that each file is 50,000 lines long:

    $  wc -l uuids-0-50000.txt
   50000 uuids-0-50000.txt

Now open multiple terminals and get ready to process one of these at a time:

    $ python reduce.py uuids-0-50000.txt AWS_ACCESS_KEY AWS_ACCESS_SECRET
        1/50000/0%	01200139-cd1a-49ac-a864-99a962160915	YAY
        2/50000/0%	012004f1-800b-4c77-92b2-6f2d22160915	YAY
        3/50000/0%	01200666-6d16-4858-81a0-6703f2160915	YAY
        4/50000/0%	012011f2-1f43-4ef3-af7a-e05742160915	YAY
        5/50000/0%	012014ac-ca82-4cdc-b1c4-de7c42160915	YAY
        6/50000/0%	01202c4a-a4a1-45fe-8790-55ef32160915	YAY
        7/50000/0%	012035f6-17fc-4ca5-a3b3-051f22160915	YAY
        8/50000/0%	01203c45-7612-4ea5-b1f7-692062160915	YAY
        9/50000/0%	01205c46-aafb-4862-8fb4-94f5e2160915	NEJ
       10/50000/0%	012074e7-f62d-4015-9761-11c6a2160915	YAY
       11/50000/0%	01208738-2f61-4cb4-941b-6b3be2160915	YAY
       12/50000/0%	0120955b-3b1c-4c93-9413-244152160915	YAY
    ...

Lines that end in `YAY` will append to `haves.txt` and lines that end
in `NEJ` will append to `havenots.txt`.

Note that it does **not** check for duplicates in these files. If you
start the above mentioned script repeatedly it will start over for each
file and potentially write repeated UUIDs.

*Whilst* this is going, keep an eye on the file `havenots.txt`. It should
be slowly growing. When there's at least 1,000 lines in there you can start
the reprocessing script:

    $ wc -l havenots.txt
    627 havenots.txt

The script `reprocess.py` reads from `havenots.txt`, and sends a list of
these (in batches) to `/api/Reprocessing/` and notes which ones it has sent
in into `reprocessed.txt`:

    $ python reprocess.py AUTH_TOKEN
