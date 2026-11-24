# Why U.S. Gas Prices Fell in November 2026

A sourced research report on the 66-cent collapse in U.S. gasoline — with an interactive HTML edition, a print PDF, and a narrated video.

**Snapshot:** November 23, 2026, 7:25 PM Mountain Time. Live prices will change.

---

## The short answer

The U.S. national average for regular gasoline fell to **$3.6366** on November 23, 2026 — down **65.6 cents (15.3%)** in a month and **92.3 cents** below the year's peak of $4.56. It is still **56.5 cents (18.4%) higher than a year ago**.

This was not a demand collapse. It was the partial unwinding of a war premium:

- **Diplomacy.** WTI fell **7.4%** on November 2 as Washington and Tehran signaled a deal was possible; Brent fell **15% on the week** to November 6.
- **Supply.** Gulf exports recovered. Crude flows through the Strait of Hormuz returned to **82% of pre-war levels**. The IEA declared the first fourth-quarter surplus since the war began (**+1.7 million barrels a day**), and global inventories built by **52 million barrels** in October.
- **Crude.** Brent fell from **$136** on October 8 to **$89.37** on November 23 (**−34%**). WTI settled at **$80.17**, its lowest since August 10.
- **Seasonality and retail.** Winter-blend gasoline, rebounding refinery runs, and the pass-through of cheaper crude did the rest.

The relief is fragile. Diesel is **$5.8182** — up **53.4%** year on year and only 71 cents below its all-time record. Attacks around Hormuz are at their **highest level since the war began**. And on-land global oil stocks are the **lowest since at least 2016**.

---

## What is inside

| File | What it is |
|---|---|
| [`index.html`](index.html) | Interactive single-file report. Opens in any browser; no server, build step, or network needed. |
| [`report.pdf`](report.pdf) | Nine-page print edition with a light theme. |
| [`report/GAS-PRICE-DROP-2026.md`](report/GAS-PRICE-DROP-2026.md) | Full Markdown report (~3,700 words) with 19 numbered sources. |
| [`video/gas-prices-2026.mp4`](video/gas-prices-2026.mp4) | 2:45 narrated explainer, 1920×1080, 30 fps. |
| [`video/thumbnail.jpg`](video/thumbnail.jpg) | Video poster. |
| [`data/eia_weekly_retail.csv`](data/eia_weekly_retail.csv) | EIA weekly U.S. gasoline and diesel retail prices, 2024–2026. |
| [`data/chart_data.json`](data/chart_data.json) | The dataset embedded in the HTML charts. |
| [`SOURCES.md`](SOURCES.md) | All 19 sources, linked and described. |

The video is narrated with the **Andrew** neural voice via `edge-tts` (Microsoft Edge's speech service). The HTML uses no CDN, no external fonts, and no network requests.

---

## The numbers behind the story

| Metric | Value | Change |
|---|---:|---:|
| AAA national average, regular | **$3.6366** | −65.6¢ vs. month; +56.5¢ vs. year |
| AAA 2026 peak (May 21) | $4.56 | −92.3¢ from peak |
| AAA autumn peak (Sep 24) | $4.48 | −84.3¢ from peak |
| Diesel | **$5.8182** | −49.9¢ vs. month; +53.4% vs. year |
| Diesel record (Sep 22) | $6.5276 | −70.9¢ from record |
| Brent crude | **$89.37** | −34% from $136 (Oct 8) |
| WTI crude | **$80.17** | lowest since Aug 10 |
| IEA Q4 2026 balance | **+1.7 mb/d** | first surplus since the war began |
| Hormuz crude flows (Oct) | **15 mb/d** | 82% of pre-war |
| U.S. crude stocks | 417.8M bbl | 3% below five-year average |

The **47.9-cent four-week decline** in the EIA weekly series (to November 16) is the **18th-largest** of 1,878 four-week windows since 1990, and the **deepest November decline since 2008**.

---

## Data and method

- **Prices:** AAA daily national and state averages (accessed November 23, 2026); EIA weekly retail surveys through November 16, 2026. AAA and EIA use different survey methods; differences of a few cents are normal. All prices are nominal U.S. dollars per gallon.
- **Crude:** Brent and WTI settlements from Reuters and OilPrice.com. The $136 peak is the IEA's North Sea Dated high for October 8.
- **Physical data:** IEA *Oil Market Report* (November 13, 2026); EIA *Short-Term Energy Outlook* (November 10, 2026); EIA weekly petroleum status reports as summarized by AAA.
- **Ranking:** computed from the EIA weekly U.S. regular gasoline series, 1990–2026, using 28-day changes with exact-date matching; 1,878 observations.
- **Causal claims:** the report distinguishes measured prices from attributed causes. The relative weights of diplomacy, supply, demand, seasonality, and pass-through are a judgment based on timing and magnitude, not an econometric decomposition.

The full methodology and limitations are in the [report](report/GAS-PRICE-DROP-2026.md#methodology-and-limitations).

---

## Reproduce

Requirements: Python 3, Pillow, ffmpeg, `edge-tts`, and Google Chrome (for the PDF). The HTML needs nothing.

```bash
# 1. Rebuild the chart data from the saved EIA page + CSV
python build/build_data.py

# 2. Rebuild index.html from the template and embedded JSON
python build/build_site.py

# 3. Rebuild report.pdf with headless Chrome (serves the folder locally)
python build/build_pdf.py

# 4. Rebuild the video (slides + narration + ffmpeg)
python build/build_video.py all
```

The raw EIA page snapshot used for the 1990–2026 ranking is in `data/eia_weekly_gasoline.html`. The build scripts write only inside this folder.

---

## Sources

The report cites 19 sources, including AAA, the EIA, the IEA, Reuters, CNN, CNBC, OilPrice.com, OPEC, and Lloyd's List Intelligence. See [`SOURCES.md`](SOURCES.md) for the full list.

---

## License

- **Report text, charts, and video:** © 2026 Familiar, licensed under [CC BY 4.0](CONTENT-LICENSE.md).
- **Code in `build/`:** MIT. See [`LICENSE`](LICENSE).
- **Underlying data:** belongs to its publishers (AAA, EIA, IEA, Reuters, etc.) and is used here for research and commentary.

---

*Generated by Familiar, a Hermes agent, for Owen. Price data is a snapshot and will change. Verify before making decisions.*
