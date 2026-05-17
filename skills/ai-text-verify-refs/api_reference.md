# API reference for verify-refs

Per-source query syntax and response field paths. Consult this when constructing a query or parsing a response. All examples assume keys live in `~/.claude/skills/verify-refs/.env`.

---

## OpenAlex (free, no API key)

**Endpoint**: `https://api.openalex.org/works`

**Always append** `mailto=<CONTACT_EMAIL>` for the polite pool (higher rate limits, ~100k/day).

### Lookup by DOI

```bash
curl -s "https://api.openalex.org/works/doi:10.1111/j.1540-6261.2006.00885.x?mailto=your.email@example.com" | jq '.'
```

### Search by keywords

```bash
curl -sG "https://api.openalex.org/works" \
    --data-urlencode 'search="investor sentiment" "cross-section"' \
    --data-urlencode "per_page=5" \
    --data-urlencode "mailto=your.email@example.com" | jq '.results[0]'
```

Narrow with filters via `&filter=...` — useful:
- `filter=publication_year:2006`
- `filter=author.id:A5007356898` (specific author OpenAlex ID)
- `filter=authorships.author.display_name.search:baker`

### Key response fields

- Single work result: top-level object (e.g. from `/works/doi:...`).
- Search result: `.results[]`.

Within a work:
- `id` — OpenAlex ID URL (e.g. `https://openalex.org/W2037345987`).
- `doi` — DOI URL; strip the `https://doi.org/` prefix to get the bare DOI.
- `title` — canonical title.
- `publication_year` — integer year.
- `authorships[].author.display_name` — author names (ordered).
- `authorships[].author.id` — OpenAlex author IDs.
- `biblio.volume`, `biblio.issue`, `biblio.first_page`, `biblio.last_page`.
- `primary_location.source.display_name` — journal name.
- `primary_location.source.issn_l` / `primary_location.source.issn` — ISSN(s).
- `type` — e.g. `article`, `book-chapter`.
- `cited_by_count` — citation count.

### Useful jq one-liners

```bash
# Extract the essentials from a work
jq '{doi: (.doi | sub("https://doi.org/"; "")),
     title,
     year: .publication_year,
     authors: [.authorships[].author.display_name],
     journal: .primary_location.source.display_name,
     volume: .biblio.volume, issue: .biblio.issue,
     pages: "\(.biblio.first_page // "")-\(.biblio.last_page // "")"}'
```

---

## Scopus (Elsevier Search API)

**Wrapper**: `~/.claude/skills/verify-refs/helpers/scopus_search.sh "<query>" [STANDARD|COMPLETE]`

**Docs**: https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl

### Query syntax

Scopus uses field-tagged boolean queries. Common tags:

- `DOI(...)` — exact DOI match. Most reliable.
- `TITLE("exact phrase")` — title words/phrases.
- `TITLE-ABS-KEY(...)` — title, abstract, keywords.
- `AUTH("Surname, F.")` or `AUTHLASTNAME(Surname)` — author.
- `PUBYEAR IS 2006` / `PUBYEAR > 2010` / `PUBYEAR AFT 2005 AND PUBYEAR BEF 2011`.
- `SRCTITLE("Journal of Finance")` — journal name.
- `ISSN(0022-1082)` — ISSN.
- Combine with `AND`, `OR`, `AND NOT`.

### Query examples

```bash
# DOI lookup (best)
helpers/scopus_search.sh 'DOI(10.1111/j.1540-6261.2006.00885.x)'

# Title + year
helpers/scopus_search.sh 'TITLE("investor sentiment" AND "cross-section") AND PUBYEAR IS 2006'

# Author + year + title phrase
helpers/scopus_search.sh 'AUTHLASTNAME(Baker) AND TITLE("sentiment") AND PUBYEAR IS 2006'

# Request COMPLETE view to get abstracts, affiliations, author keywords
helpers/scopus_search.sh 'DOI(10.1111/j.1540-6261.2006.00885.x)' COMPLETE
```

### Key response fields

Path: `.search-results.entry[]` — array of hits.

Per hit (note the `prism:` / `dc:` namespaces):

- `.prism:doi` — DOI.
- `.dc:title` — title.
- `.dc:creator` — first author.
- `.author` (array in COMPLETE view) — full author list with `authname`, `surname`, `given-name`, `authid`.
- `.prism:coverDate` — `YYYY-MM-DD`.
- `.prism:publicationName` — journal.
- `.prism:issn` — ISSN.
- `.prism:volume`, `.prism:issueIdentifier`.
- `.prism:pageRange` — e.g. `"1645-1680"`.
- `.citedby-count` — citations.
- `.dc:identifier` — `SCOPUS_ID:...`.
- `.subtypeDescription` — `Article`, `Review`, etc.

Total results at `.search-results.opensearch:totalResults`.

### Useful jq

```bash
jq '.["search-results"].entry[0] |
    {doi: .["prism:doi"],
     title: .["dc:title"],
     year: (.["prism:coverDate"] | split("-")[0]),
     first_author: .["dc:creator"],
     journal: .["prism:publicationName"],
     volume: .["prism:volume"],
     issue: .["prism:issueIdentifier"],
     pages: .["prism:pageRange"],
     issn: .["prism:issn"]}'
```

---

## Web of Science Starter (Clarivate)

**Wrapper**: `~/.claude/skills/verify-refs/helpers/wos_search.sh "<query>"`

**Docs**: https://developer.clarivate.com/apis/wos-starter

### Query syntax

WoS uses its own field tags and simple boolean logic.

- `DO=10.1111/...` — DOI match.
- `TI="exact phrase"` — title.
- `TS=(keyword)` — topic search (title + abstract + keywords).
- `AU=Baker M*` — author (wildcards allowed; surname + initial).
- `PY=2006` / `PY=2000-2010`.
- `SO="Journal of Finance"` — source (journal).
- `ISSN=0022-1082`.
- Combine with `AND`, `OR`, `NOT`.

### Query examples

```bash
# DOI
helpers/wos_search.sh 'DO=10.1111/j.1540-6261.2006.00885.x'

# Title + year
helpers/wos_search.sh 'TI="investor sentiment and the cross-section" AND PY=2006'

# Author + year
helpers/wos_search.sh 'AU=Baker M* AND PY=2006 AND TI=sentiment'
```

### Key response fields

Path: `.hits[]` — array of hits.

Per hit:

- `.uid` — WoS UID (e.g. `WOS:000240019400005`).
- `.title` — title.
- `.source.sourceTitle` — journal.
- `.source.publishYear` — year.
- `.source.volume`, `.source.issue`, `.source.pages.range` (e.g. `"1645-1680"`).
- `.identifiers.doi` — DOI.
- `.identifiers.issn` — ISSN.
- `.names.authors[].displayName` — author names.
- `.citations[0].count` — citation count.
- `.types[]` — document types.

Total at `.metadata.total`.

### Useful jq

```bash
jq '.hits[0] |
    {wos_uid: .uid,
     doi: .identifiers.doi,
     title: .title,
     year: .source.publishYear,
     journal: .source.sourceTitle,
     volume: .source.volume,
     issue: .source.issue,
     pages: .source.pages.range,
     authors: [.names.authors[].displayName]}'
```

---

## Rate limits and etiquette

- **OpenAlex**: ~100k requests/day with `mailto=`. No strict per-second limit but sleep ~0.15s between calls for bulk work.
- **Scopus**: Per-key weekly quota depending on subscription. Sleep ~0.5s between calls.
- **WoS Starter**: 5 req/sec hard limit; watch for `429`. Sleep ~0.25s between calls.

For single-reference verification the limits are never close to binding. For `.bib` files with many entries, process them one at a time in a loop rather than blasting the APIs.
