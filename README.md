# news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/xiacai520/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/xiacai520/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

Sum up 26 November's world news in one image: a 1024x1024 newspaper front page
("THE WORLD IN ONE PAGE") covering six major stories from Thursday 26 November 2026,
each verified against Reuters (and Al Jazeera for the ECB story):

1. US unveils sweeping new tariffs on 14 trading partners (15%-35%)
2. Drone strike in Kuwait kills two Italians; Italy blames Iran
3. Russia hits Kyiv with ballistic missiles and grain ships near Odesa
4. Cairo tanker fire kills 31 on the Ring Road
5. Ebola in DR Congo tops 12,000 cases (12,021 confirmed, 5,904 dead)
6. Spain's Pablo Hernandez de Cos picked to lead the European Central Bank

`main.py` is pure Python standard library: a hand-rolled PNG encoder
(zlib + struct), a hand-drawn 5x7 bitmap font, and all artwork (bar chart,
drone, rocket, tanker fire, virus, bank) drawn from drawing primitives.
Deterministic: no clock, no randomness, no network. Running it writes
`entry.png` (1024x1024) into `$MAKEFUN_OUTPUT_DIR` (default `/output`).

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/c/news-image-20261126) · AI age
