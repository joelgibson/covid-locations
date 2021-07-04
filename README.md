# COVID Case Locations

See it live at <https://www.jgibson.id.au/articles/covid-locations/>.

This is a quick visualisation I mocked up of the spread of the latest (as of June 2021) COVID-19 outbreak in NSW.
It is not intended to prove any kind of point, I just thought it would be interesting to look at the data.

Its dependencies are minimal: the only run-time dependency is [leaflet](https://leafletjs.com/) for drawing the maps,
with [Vite](https://vitejs.dev) as the dev server and build tool.


## Running and building the frontend

I use `pnpm`, but `npm` probably works too.

    pnpm install      # Download dependencies
    pnpx vite         # Launches dev server
    pnpx vite build   # Creates a static build under site/dist/

The only files needed to build the frontend are those in `site/`, however `site/cases.json` is generated from the data collection process below.


## Collecting and cleaning data

The case data comes from <https://data.nsw.gov.au/nsw-covid-19-data/case-locations>.
There is a metadata file which we check every 20 minutes to see if there is a new data file available.
This data file is sometimes a bit funky (it seems to be in UTF-8, but still sometimes has a byte order mark that needs to be removed) but is otherwise perfectly good JSON.
Run the automatic downloader using

    python3 monitor_for_updates.py | tee -a update_log

New JSON files will be saved to `json/`. This is all that is really needed - one of these JSON files could be copied almost straight to `site/cases.json` (it needs some
regex scrubbing around to generate a start and end datetime). The data stuff that follows is mostly for my own interest - I find it interesting to see how these things
change over time - as well as a little spelunking through older files to resurrect cases that were removed only because they were 14 days old.

To see better what has changed between different JSON files, we turn each into a compact one-line-per-record file stored under `casefiles/`. These records contain only
the fields I am interested in (Venue, Address, Suburb, Time, Date, Lon, Lat), and are sorted first by date and then by venue. This sorting order seems to be the "best"
for looking at what has changed with a file diff tool like `tkdiff`. To go through all the files in `json/` and generate any new case files to `casefiles/`, run

    python3 generate_casefiles.py

Then to use a heuristic to find any retired cases, run

    python3 collect_retired.py > retired

Each new entry should be checked visually using a diffing tool, for example `tkdiff casefiles/2021-07-02T12:28 casefiles/2021-07-02T14:30`.
Finally, the retired cases can be combined with the last casefile by running

    python3 generate_clean_json.py retired casefiles/2021-07-04T23:00 > ../site/cases.json

