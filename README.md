<p align="center"><img src="public/faithforwardlogo.png" alt="Faith Forward crest" width="200"></p>

<h1 align="center">Faith Forward Daily</h1>
<p align="center"><em>A new scripture, prayer, and quote every day · Spiritus Invictus</em></p>

<p align="center">
<a href="https://paulmmoore3416.github.io/faith-forward-daily-quotes/"><img alt="Live" src="https://img.shields.io/badge/daily-live-c9a227?style=for-the-badge"></a>
<a href="https://github.com/paulmmoore3416/faith-forward-daily-quotes/actions/workflows/deploy.yml"><img alt="Deploy" src="https://img.shields.io/github/actions/workflow/status/paulmmoore3416/faith-forward-daily-quotes/deploy.yml?label=deploy&style=for-the-badge"></a>
<a href="https://paulmmoore3416.github.io/faith-forward/"><img alt="Faith Forward" src="https://img.shields.io/badge/faith%20forward-website-1e2a33?style=for-the-badge"></a>
</p>

**Faith Forward Daily** is the daily devotional companion of **[Faith Forward Foundation](https://paulmmoore3416.github.io/faith-forward/)**, a faith-based ministry that provides assistance, resources, supplies, and religious services to displaced and homeless veterans, their families, and the animals who walk beside them in **St. Louis, Missouri**.

Founded by **The Reverend Paul Moore** (Rev. Paul Moore), a disabled three-tour Iraq veteran, ordained minister, and creator and founder of Faith Forward Foundation and **[STL Veterans Hub](https://www.stlveteranshub.com)**.

> **Veteran in crisis?** Call **988 and press 1**, or text **838255**. Free, confidential, 24/7.

## ✨ Features

- 📖 **Daily scripture** from the King James Version (public domain)
- 🙏 **Daily prayer**: 71 prayers, most written for veterans, handlers, families, and outreach teams, plus traditional prayers (St. Michael, Memorare, St. Francis, Anima Christi)
- 💬 **Daily quote** from saints, chaplains, presidents, veterans, and Faith Forward
- 🗓️ **Feast days and holidays**: Veterans Day (St. Martin of Tours), Memorial Day, Pearl Harbor, 9/11, St. Michael, St. Francis (Blessing of the Animals), Advent, Christmas, Ash Wednesday, Holy Week, Easter, Pentecost, and more. Easter is computed each year.
- 🔎 **Search and filter** scripture by theme (courage, healing, brotherhood, hope…), plus prayers and quotes
- 🔥 **Daily streak badges**, **personal greeting**, **dark mode**, **share** (Web Share / Facebook), **listen** (text-to-speech)
- 📱 Installable as an app (web manifest)
- ⚡ No build step: a single static page plus `data/devotional.json`

**Same word everywhere:** the website, the Faith Forward Command Center, and this site all use the same devotional engine (`faith-forward/src/data/devotional.ts`), so everyone in the ministry prays the same scripture and prayer each day.

## 🚀 Run locally

```bash
git clone https://github.com/paulmmoore3416/faith-forward-daily-quotes.git
cd faith-forward-daily-quotes
python3 -m http.server 8000   # http://localhost:8000
```

## 🔄 Updating the devotional data

The data is exported from the main repository so both stay in sync:

```bash
# from a checkout of paulmmoore3416/faith-forward, next to this repo
npx tsx scripts/export-devotional.ts ../faith-forward-daily-quotes/data/devotional.json
```

`data/devotional.json` holds the verse, quote, and prayer pools plus a precomputed schedule for 2026-2030. After 2030 the page falls back to the same rotation the main site uses; re-export to extend the schedule.

## 🗓️ Faith Forward Planner (desktop app)

This repository also contains the **Faith Forward Planner**, a GTK calendar application for Ubuntu/Debian with natural-language events, smart time blocking, a daily reflection widget, and EPUB/Markdown export.

```bash
cd faith_forward_planner
python3 demo.py      # demo
./install.sh         # full install
```

See [faith_forward_planner/README.md](faith_forward_planner/README.md).

## 🌐 Deployment

GitHub Actions deploys the site to GitHub Pages on every push to `main` (`.github/workflows/deploy.yml`). In **Settings → Pages**, set **Source: GitHub Actions**.

## 🤝 Related

| | |
|---|---|
| Faith Forward website | https://paulmmoore3416.github.io/faith-forward/ |
| K9 Handler Training Suite | https://paulmmoore3416.github.io/faith-forward/k9-suite.html |
| Main repository | https://github.com/paulmmoore3416/faith-forward |
| STL Veterans Hub | https://www.stlveteranshub.com |
| Facebook | https://www.facebook.com/profile.php?id=61581209302246 |

---

<p align="center">Scripture: KJV (public domain). Prayers and site © Faith Forward Foundation · St. Louis, Missouri</p>
