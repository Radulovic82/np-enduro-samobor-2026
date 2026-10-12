# NP Enduro Samobor 2026 results

Line charts comparing every rider stage by stage at NP Enduro Samobor 2026 (11 Oct 2026). Pick a category, highlight riders against the field, and share the URL (the selection is kept in the hash).

Live page: https://radulovic82.github.io/np-enduro-samobor-2026/

Data comes from https://my.raceresult.com/426482/. This page is unofficial.

Not every category rides every stage (U15 skips S3 and S5, Kadeti/Juniori and Open skip S5), so gaps are computed per category over the stages that category rode.

The Overall view ranks everyone who rode all 5 stages together (E-bike, M1, M2, M3). Riders from the shorter categories are not in it.

## Updating

```
python3 scripts/fetch_results.py
git add data/results.json
git commit -m "results"
git push
```

## Local preview

```
python3 -m http.server 8000
```
