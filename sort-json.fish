#!/usr/bin/env fish

for f in src/*.json
    cat $f | jq '.data.monitor | sort_by([.Venue, .Address, .Date, .Time])' > $f.sorted
end