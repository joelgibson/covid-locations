# COVID Case Locations

See it live at <https://www.jgibson.id.au/articles/covid-locations/>.

This is a quick visualisation I mocked up of the spread of the latest (as of June 2021) COVID-19 outbreak in NSW.
It is not intended to prove any kind of point, I just thought it would be interesting to look at the data.

Its dependencies are minimal: the only run-time dependency is [leaflet](https://leafletjs.com/) for drawing the maps,
with [Vite](https://vitejs.dev) as the dev server and build tool.


## Building

I use `pnpm`, but `npm` probably works too.

    pnpm install      # Download dependencies
    pnpx vite         # Launches dev server
    pnpx vite build   # Creates a static build under dist/

The case data comes from <https://data.nsw.gov.au/nsw-covid-19-data/case-locations>.
After downloading more case data, remove the byte order mark (eg open the JSON file in vim, type `:set nobomb` and save), and then update the JSON import in `index.ts`.
