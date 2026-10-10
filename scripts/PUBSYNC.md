# Weekly publication sync

Keeps `_pages/publications.md` in step with Google Scholar / arXiv.
Run by a weekly scheduled task; can also be run by hand.

## 1. Find differences

```bash
python3 scripts/pubsync.py
```

- `new_preprints`: arXiv records not yet on the page.
- `now_published`: entries under **Preprints** whose arXiv record now has a journal ref or DOI.
- `still_preprint`: every arXiv ID still under **Preprints**. arXiv's journal fields are
  often never updated by authors, so also look each title up on Crossref
  (`https://api.crossref.org/works?query.bibliographic=<title>&rows=3`) and in any
  Google Scholar alert emails (sender `scholaralerts-noreply@google.com`).
  Only treat a paper as published when the DOI's title and author list match.

Google Scholar itself blocks automated access, so it is not queried directly.

## 2. New preprint → new row at the top of `## Preprints`

Row template (one line, newest first):

```
| <img src="/assets/images/<IMAGE>" width="200" alt="" align="center" style="display:block;margin-bottom:10px;margin-top:10px;margin-left:0px;margin-right:0px;padding-left:5px;padding-right:5px;" /> | **<Title in sentence case>** <br> _with <co-authors, Oxford comma, Brendan omitted>_ <br> arXiv: <ID> [<primary category>] [[preprint](https://arxiv.org/abs/<ID>)] |
```

Choosing the image:
1. Download the source: `https://arxiv.org/src/<ID>` (a gzipped tarball, occasionally a bare gzipped .tex).
2. Render every figure (`pdftoppm -png -r 80`), look at them, and prefer, in order:
   a 2D/3D solution or geometry plot (colourful, readable at 200 px) → a single-panel
   convergence/comparison plot with a legend → one panel cropped from a multi-panel figure.
   Avoid schematics that are mostly text, tables, and multi-panel grids at full size.
3. Crop to the content (`convert -trim`), resize to at most 600 px wide, strip metadata,
   and save as `assets/images/<short_descriptive_name>.png`.
4. If the source has no usable figure, use `paper.gif` and the grey-background style
   used by the "isometry constraint" row.

## 3. Published preprint → move to `## Peer-Reviewed Scientific Articles`

Remove the row from Preprints and insert it in Peer-Reviewed, ordered by year
(to-appear entries first). Keep the image cell. Replace the venue line with:

```
<Full journal name> (<year>) [[preprint](https://arxiv.org/abs/<ID>)] [[journal doi](https://doi.org/<DOI>)]
```

Accepted-but-not-yet-online papers use `<Journal> (to appear, <year>)` and get the DOI later.
Keep any existing `[[code]]` links.

## 4. Deliver

Open a pull request against `master` titled `Publications sync <YYYY-MM-DD>` listing each
change and, for every new row, which figure was chosen and the runner-up. If nothing changed,
do nothing.
