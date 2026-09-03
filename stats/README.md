# What we can and cannot measure

## What is here

| File | What it holds |
|---|---|
| `SUMMARY.md` | The readable report. Start here. |
| `downloads.csv` | Cumulative downloads per release asset, one row per day. |
| `traffic.csv` | Page views, unique visitors, clones and unique cloners, per day. |
| `referrers.csv` | Which sites sent people here, snapshotted daily. |
| `collect.py` | The collector. Run it by hand with a token, or let the Action do it. |

`.github/workflows/stats.yml` runs the collector every morning and commits the result.

## Two things worth knowing

**GitHub forgets traffic after fourteen days.** Views, clones and referrers are a
rolling two-week window with no history and no way to ask for the past. That is the
entire reason this directory exists: if nobody writes the numbers down each day,
they are gone. Download counts are not on that clock, but see below.

**Deleting a release destroys its download count, permanently.** The count lives on
the release, so removing a superseded release also removes the record of how many
people took it. Keep old releases and mark them superseded in the notes instead.
`SUMMARY.md` will show a negative day if this ever happens again.

**Clone counts are mostly us.** `installer\Publish-Release.ps1` clones this repository on
every single publish, so `clones` and `unique_cloners` largely measure our own release
automation rather than anybody's interest. Read `views`, `unique_visitors` and the
download counts; treat clones as noise.

## The honest position on geography

**GitHub exposes no country or region data at all.** Not for downloads, not for
views, not for clones. Release assets are served straight from GitHub's CDN, so the
request never touches anything we control and there is nothing to record.

The referrer list in `SUMMARY.md` answers a different question - *which site linked
them here* - and is the closest thing available out of the box. It is useful, but it
is not a map.

Measuring where downloads actually come from needs a redirect that we own sitting in
front of the file, so the request passes through something that can see the request's
country before handing over the MSI:

    Download button  ->  our redirect  ->  records country + version  ->  GitHub asset

A Cloudflare Worker is the usual way to do this: the free tier is sufficient at this
scale, it reports the country of each request without any third-party tracking
script, and it adds a single redirect hop that nobody notices. The alternative is
having ScreenInk itself report in after installation, which would additionally
reveal how many installs are *active* rather than merely downloaded - but that is
telemetry, and it should be opt-out, disclosed, and anonymous if it is done at all.

Neither is set up. Both are decisions to be made deliberately rather than by
accident, which is why this file says so instead of quietly adding a tracker.

## Running the collector by hand

```bash
GITHUB_TOKEN=<token with push access> python stats/collect.py
GITHUB_TOKEN=<token> python stats/collect.py --dry-run   # look, don't write
```
