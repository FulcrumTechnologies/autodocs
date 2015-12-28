[This is a WIP. Direct all related "this readme is terrible" hatemail to your local IT intern.]

Confluence Writer updates Confluence wiki pages for Skytap environments (configurations) and their appropriate VMs.

Commands are run from the terminal:
- To write any/all pages for environments not currently written, run "python update.py write".
- To store any information written into user-modifiable fields, run "python update.py store". This will ensure preservation of user-written notes and data.
- To check for recent changes to environments/VMs and update the pages to reflect them, run "python update.py check".

It's recommended to run these in the order of write->store->check.

The "JSONS" directory holds important information for every environment and VM which currently has a page written.
They are named in the format of "[Skytap ID].json".

The "storage" directory holds information that will be printed to their relevant fields in the next page update.
This ensures preservation of important information such as username/password combinations, etc.

Han shot first.
