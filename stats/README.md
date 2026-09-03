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

### Traffic needs a token the Action does not have by default

GitHub's traffic endpoints refuse the automatic `GITHUB_TOKEN`: they want a user token
with push access. Download counts collect fine without it, so the job still runs and
`SUMMARY.md` says openly when traffic is being refused rather than recording a false
quiet day.

To switch traffic collection on, create a **fine-grained personal access token** at
<https://github.com/settings/personal-access-tokens/new>:

- **Repository access:** only `alexusa75/ScreenInk-releases`
- **Permissions:** `Contents` → read, `Administration` → read *(this is the one the
  traffic endpoints check)*
- Give it a long expiry, or expect to replace it

Then add it to the repository as a secret named `STATS_PAT`:

```powershell
gh secret set STATS_PAT --repo alexusa75/ScreenInk-releases
```

Scoping it to this one repository matters. A classic token, or anything broader, would
give a workflow in a public repository far more reach than counting page views deserves.

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

**The Cloudflare Worker is now live.** The download button on the README points at
`screenink-download.screenink.workers.dev/download`, which records the country and
redirects to the asset. It stores a country, region, version, referring host and date,
and no IP address, user-agent, cookie or identifier of anything. It is disclosed in the
README under "Questions", and anyone who would rather avoid it can take the file from
the releases page instead.

Two caveats that matter when reading those numbers:

* Downloads taken straight from the releases page bypass the redirect, so GitHub's
  count remains the authoritative total and the Worker's is a sample of it.
* The in-app updater deliberately does not go through the redirect, so these figures
  measure new downloads rather than existing users updating.

The country breakdown is not published here. At current volumes a single download from
a small country is effectively one identifiable person, which is precisely what the
"no identifiers" rule above exists to prevent.

## Running the collector by hand

```bash
GITHUB_TOKEN=<token with push access> python stats/collect.py
GITHUB_TOKEN=<token> python stats/collect.py --dry-run   # look, don't write
```
