# Knowledge source candidates

Researched 2026-09-25 (before Step 11). Nothing here has been downloaded or ingested yet.
Licenses were checked on publisher pages or publisher-supplied metadata (Europe PMC full-text XML, Crossref).
Items marked UNVERIFIED need a manual check before use. This is not legal advice.

## Why licenses decide what we can use

The repo is meant to become a public portfolio. Ingesting a document means extracting, chunking,
and storing its text, and possibly committing it. So each source falls into one of four groups:

| Group | Licenses | What we can do |
|---|---|---|
| **A. Free to reuse** | US federal public domain, UK Open Government Licence v3.0, CC BY 4.0 | Ingest; processed text may be committed. Attribute (title, author, link, license, "text extracted and chunked"). |
| **B. Reuse with conditions** | CC BY-NC, CC BY-SA, CC BY-NC-SA | Ingest with attribution. NC: never in a commercial product, so tag every chunk with its license so it can be filtered out. SA: committed derived text must keep the same license, in its own folder. |
| **C. Read-only for the pipeline** | CC BY-NC-ND | Sharing adapted versions is not allowed. Safest: don't commit processed text, or skip. |
| **D. Study and cite only** | All rights reserved (NSCA, Human Kinetics, Wolters Kluwer journals) | Do not ingest. Read, then write original notes in your own words, citing the source. Wolters Kluwer (JSCR) explicitly reserves "text and data mining and artificial intelligence training." |

Project rule (CLAUDE.md), quoted exactly: "Exercise data is original, author-written content. No scraped material." Importing a licensed dataset such as wger into the exercise table would require changing that rule first.

## 1. Government and public-sector guidelines

| Source | Year | Link | File | License | Covers | Fit |
|---|---|---|---|---|---|---|
| **Physical Activity Guidelines for Americans, 2nd ed.** (HHS/ODPHP) | 2018 (current; 3rd ed. not expected before 2028) | [landing page](https://odphp.health.gov/our-work/nutrition-physical-activity/physical-activity-guidelines/current-guidelines) | [PDF](https://odphp.health.gov/sites/default/files/2019-09/Physical_Activity_Guidelines_2nd_edition.pdf), 15,360,711 bytes (~14.7 MB) | **A.** Public domain: ODPHP copyright policy says site information "is in the public domain… may be freely distributed and copied," with a link and acknowledgment requested. Third-party images may be copyrighted. | Aerobic, muscle-strengthening, bone, balance; all ages, pregnancy, chronic conditions | **High. Chosen first document.** Dose guidance, little how-to |
| **ATP 7-22.02 Holistic Health and Fitness Drills and Exercises** (US Army) | 2020, Change 1 ≈ Sept 2025 | [record](https://armypubs.army.mil/ProductMaps/PubForm/Details.aspx?PUB_ID=1020967) | [PDF](https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN45013-ATP_7-22.02-001-WEB-4.pdf), ~15.5 MB | **A.** "Approved for public release; distribution unlimited" (from search snippets; confirm in the PDF) | Step-by-step drills: preparation/recovery, calisthenics, strength circuits, conditioning, mobility | **High.** Richest exercise-description source found |
| **FM 7-22 Holistic Health and Fitness** (US Army) | 2020, incl. Change 2 | [record](https://armypubs.army.mil/ProductMaps/PubForm/Details.aspx?PUB_ID=1020968) | [PDF](https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN44522-FM_7-22-002-WEB-7.pdf), ~4.1 MB | **A.** Same statement (UNVERIFIED in the PDF itself) | Training principles and programming, nutrition, sleep, mental readiness | **High** |
| **UK CMOs' Physical Activity Guidelines** | 2019, updated 10 Jul 2026 | [gov.uk](https://www.gov.uk/government/publications/physical-activity-guidelines-uk-chief-medical-officers-report) | HTML only, ~33,000 words | **A.** "licensed under the terms of the Open Government Licence v3.0 except where otherwise stated" | All ages incl. strength and balance for older adults | **High.** Recent, easy HTML |
| **Growing Stronger: Strength Training for Older Adults** (CDC + Tufts) | 2002 | [CDC Stacks](https://stacks.cdc.gov/view/cdc/11447) | PDF ~500 KB, 126 pp | **A.** CDC Stacks "Rights Status: Public Domain" (Tufts co-authored; check front matter) | 12-week progressive program with exercise instructions | High, but old |
| **NIA Exercise and Physical Activity** (NIH) | 2023–2025 | [NIA](https://www.nia.nih.gov/health/exercise-and-physical-activity) | PDFs (bot-protected; download by hand) | **A.** Public domain per NIA policy (UNVERIFIED directly); credit "National Institute on Aging, NIH" | Endurance, strength, balance, flexibility for older adults | Medium-high |
| **Dietary Guidelines for Americans 2025–2030** | Jan 2026 | [realfood.gov](https://realfood.gov) | [PDF](https://cdn.realfood.gov/DGA.pdf), ~3.4 MB | **A.** by federal-work rule (no statement on page, UNVERIFIED) | General-population nutrition, not sports | Medium. New edition was contested |
| **WHO Guidelines on Physical Activity and Sedentary Behaviour** | 2020 | [WHO](https://www.who.int/publications/i/item/9789240015128) | PDF ~4.0 MB | **B.** CC BY-NC-SA 3.0 IGO | All ages, sedentary behaviour | Medium-high content, restrictive license |
| **Warfighter Nutrition Guide** (HPRC, DoD) | current | [HPRC](https://www.hprc-online.org/nutrition/warfighter-nutrition-guide) | HTML chapters | Unclear: asks for attribution; no explicit license (UNVERIFIED) | Sports and military nutrition | Medium; clarify license first |
| NOFFS (US Navy, with EXOS) | 2009+ | [navyfitness.org](https://www.navyfitness.org/fitness/noffs/) | PDFs | No statement; private co-developer. **Avoid in public repo** | Movement library, programs | Private reference only |

## 2. NSCA (study and cite only, group D)

None of this can be ingested. NSCA's Terms of Use forbid republishing its material or using it on
"any other Web site or networked computer environment." Plan: read these, then write **original notes
in your own words** that cite them (ideas and facts aren't copyrightable; wording, tables, and figures are).

| Item | Access | Use |
|---|---|---|
| *Essentials of Strength Training and Conditioning*, 5th ed. (Haff & Triplett, Human Kinetics, 2026) | Paid book | Core reference. Most relevant chapters: 15 Performance Preparation, Mobility, and Flexibility; 18 Program Design for Resistance Training; 19 Plyometric Training; 20 Speed and Agility; 21 Aerobic Endurance and Metabolic Training; 22 Periodization; 24 Overreaching, Overtraining, and Recovery |
| Position statement: Weightlifting for Sports Performance (Comfort et al., 2023) | Free PDF on [nsca.com position statements](https://www.nsca.com/about-us/position-statements/) | Notes |
| Position statement: Long-Term Athletic Development (Lloyd et al., 2016) | Free | Notes |
| Position statement: Resistance Training for Older Adults (Fragala et al., 2019) | Free | Notes |
| Position statement: Youth Resistance Training (Faigenbaum et al., 2009) | Free (older; pair with LTAD) | Notes |
| Kinetic Select free excerpts: Plyometric Training; Sprinting Mechanics and Technique; Designing Speed Training Sessions; Energy System Training; Program Design for Training Seasons | Free on [nsca.com](https://www.nsca.com/education/articles/kinetic-select/) (Human Kinetics excerpts) | Notes |
| NSCA Coach: plyometrics for high school athletes (2025) | Members only | Only with membership |

## 3. Open-access research (license verified per article)

Prefer position stands and large meta-analyses as core evidence. Journals: Sports Medicine – Open and
Sports Medicine OA articles (Springer), Frontiers in Physiology, PLOS ONE, MDPI Sports, JISSN.

| Topic | Article | Year | Link | License |
|---|---|---|---|---|
| Strength | Loading recommendations: the repetition continuum re-examined (Schoenfeld et al.) | 2021 | [doi](https://doi.org/10.3390/sports9020032) | **A** CC BY. **Ingested 2026-09-30** (`schoenfeld2021-loading`) |
| Rest intervals | Give it a rest: inter-set rest and hypertrophy, Bayesian MA (Singer et al.) | 2024 | [doi](https://doi.org/10.3389/fspor.2024.1429789) | **A** CC BY. **Ingested 2026-09-30** (`singer2024-rest`) |
| Strength | RT prescription for strength & hypertrophy, Bayesian network MA (Currier et al., BJSM) | 2023 | [doi](https://doi.org/10.1136/bjsports-2023-106807) | **B** CC BY-NC |
| Strength | ACSM Position Stand: RT prescription (Med Sci Sports Exerc) | 2026 | [doi](https://doi.org/10.1249/mss.0000000000003897) | **C** CC BY-NC-ND |
| Strength (youth) | Dose-response of RT in youth athletes (Lesinski et al., BJSM) | 2016 | [doi](https://doi.org/10.1136/bjsports-2015-095497) | **B** CC BY-NC |
| Strength volume | Weekly volume & frequency dose-response (Pelland et al.) **preprint only** | 2024 | [SportRxiv](https://sportrxiv.org/index.php/server/preprint/view/460) | **A** CC BY (published version is not open). **Preprint v2 ingested 2026-09-30** (`pelland2024-volume`), labeled not peer reviewed |
| Plyometrics | Effects of plyometric training: umbrella review | 2023 | [doi](https://doi.org/10.1186/s40798-022-00550-8) | **A** CC BY |
| Plyometrics (youth) | Plyometric-jump training by maturity (Ramirez-Campillo et al.) | 2023 | [doi](https://doi.org/10.1186/s40798-023-00568-6) | **A** CC BY |
| Power | Strength vs power training in youth (Behm et al.) | 2017 | [doi](https://doi.org/10.3389/fphys.2017.00423) | **A** CC BY |
| Power | PAP vs PAPE (Blazevich & Babault) | 2019 | [doi](https://doi.org/10.3389/fphys.2019.01359) | **A** CC BY |
| Speed | Training & development of elite sprint performance (Haugen et al.) | 2019 | [doi](https://doi.org/10.1186/s40798-019-0221-0) | **A** CC BY |
| Speed | Short-distance sprint training in football codes, SR/MA (Nicholson et al.) | 2020 | [doi](https://doi.org/10.1007/s40279-020-01372-y) | **A** CC BY |
| Conditioning | HIIT in young athletes, SR/MA (Engel et al.) | 2018 | [doi](https://doi.org/10.3389/fphys.2018.01012) | **A** CC BY |
| Conditioning | Training intensity distribution in elite endurance (Stöggl & Sperlich) | 2015 | [doi](https://doi.org/10.3389/fphys.2015.00295) | **A** CC BY |
| Conditioning | HIIT in male team-sport athletes, SR/MA (Yuan et al.) | 2024 | [doi](https://doi.org/10.1371/journal.pone.0310955) | **A** CC BY |
| Stretching | Acute effects of stretching techniques on ROM, SR/MA (Behm et al.) | 2023 | [doi](https://doi.org/10.1186/s40798-023-00652-x) | **A** CC BY |
| Stretching | Chronic static stretching on strength & power (Arntz et al.) | 2023 | [doi](https://doi.org/10.1007/s40279-022-01806-9) | **A** CC BY |
| Mobility | Resistance training improves ROM, SR/MA (Alizadeh et al.) | 2023 | [doi](https://doi.org/10.1007/s40279-022-01804-x) | **A** CC BY |
| Stretching | Stretch-induced force deficit, multilevel MA (J Sport Health Sci) | 2024 | [doi](https://doi.org/10.1016/j.jshs.2024.05.002) | **C** CC BY-NC-ND |
| Weightlifting | Weightlifting vs RT vs plyometrics, SR/MA (Morris et al.) | 2022 | [doi](https://doi.org/10.1007/s40279-021-01627-2) | **A** CC BY |
| Weightlifting | Overhead pressing derivatives (Soriano et al.) | 2019 | [doi](https://doi.org/10.1007/s40279-019-01096-8) | **A** CC BY |
| Nutrition | ISSN position stand: protein and exercise | 2017 | [doi](https://doi.org/10.1186/s12970-017-0177-8) | **A** CC BY |
| Nutrition | ISSN: creatine safety & efficacy | 2017 | [doi](https://doi.org/10.1186/s12970-017-0173-z) | **A** CC BY |
| Nutrition | ISSN: nutrient timing | 2017 | [doi](https://doi.org/10.1186/s12970-017-0189-4) | **A** CC BY |
| Nutrition | ISSN: caffeine and exercise performance | 2021 | [doi](https://doi.org/10.1186/s12970-020-00383-4) | **A** CC BY |
| Nutrition | ISSN exercise & sports nutrition review update | 2018 | [doi](https://doi.org/10.1186/s12970-018-0242-y) | **A** CC BY |
| Nutrition | IOC consensus: dietary supplements (BJSM) | 2018 | [doi](https://doi.org/10.1136/bjsports-2018-099027) | **B** CC BY-NC |

Not every ISSN stand is CC BY: the 2023 female athlete and 2024 ketogenic diet stands are CC BY-NC.
Well-known but paywalled (cite only): Suchomel "Importance of Muscular Strength," IOC youth athletic
development (2015), IOC load and injury (2016), Behm 2016 stretching review, ACSM 2009 progression-models
position stand, Moesgaard 2022 periodization (Sports Medicine). The last two were checked and rejected for
program design on 2026-09-30.

## 4. Open textbooks

| Title | License | Relevant parts | Fit |
|---|---|---|---|
| **Introduction to Exercise Science for Fitness Professionals** (Shelton, MHCC Pressbooks, 2021) | **A** CC BY 4.0 "except where otherwise noted" | Flexibility, core & balance, **plyometrics/SAQ**, resistance training | **High**: best coach-oriented match |
| **Biomechanics of Human Movement** (Hamm, BCcampus, 2020) | **A** CC BY 4.0 | Kinematics, kinetics, movement analysis | High |
| Health and Fitness for Life (Markell & Peterson, MHCC) | **A** CC BY 4.0 | FITT, stretching program design | High |
| A Guide to Physical Activity (Kramer, U. Minnesota) | **A** CC BY 4.0 | Resistance and flexibility guidelines | Medium-high |
| Human Nutrition 2020 (U. Hawai'i) | **A** CC BY 4.0 | Ch 16 Performance Nutrition | Medium |
| OpenStax Anatomy & Physiology 2e | **B** CC BY-NC-SA 4.0 (changed from CC BY) | Joints, muscle tissue, muscular system | High content, restrictive license |
| Open Textbook of Exercise Physiology (MacIntosh et al.) | **B** CC BY-NC | Exercise physiology | Medium-high |
| The Physiology of Exercise 3e (Lanphere, 2025) | **B** CC BY-NC | Energy systems, adaptations | Medium-high |

## 5. Exercise datasets (to grow the exercise table)

| Dataset | License | Size | Verdict |
|---|---|---|---|
| **wger** | **B** per-exercise Creative Commons, mostly CC BY-SA 4.0, with author per record | ~912 exercises, 33 languages | Only large option that's clean. Keep per-record author and license; SA data in its own folder. No difficulty field |
| Everkinetic data | **B** CC BY-SA 4.0 | 289 | Clean, small |
| longhaul-fitness/exercises | MIT | ~349 strength + cardio + flexibility | Possible; authorship method unclear |
| free-exercise-db | Unlicense, but images scraped (traced to bodybuilding.com), text origin unknown | ~876 | **Excluded** by the no-scraped-material rule |
| ExerciseDB and mirrors | Proprietary; DMCA takedown of a mirror (Apr 2026) | 1,300–11,000 | **Do not use** |
| Kaggle "megaGym" | Self-described as scraped | ~2,500 | **Do not use** |

## Recommended ingestion order

1. **Step 11 to 13: Physical Activity Guidelines for Americans, 2nd ed.** Public domain, one PDF, authoritative.
2. Next documents (all group A): ATP 7-22.02 (drills), the plyometric umbrella review, Behm 2023 stretching,
   Haugen 2019 sprint, ISSN protein, and *Introduction to Exercise Science for Fitness Professionals*.
3. NSCA-based notes written by the developer, ingested as original content with citations.
4. Group B sources only with per-chunk license tags; group C only locally; group D never.

Engineering pattern: commit a **source manifest** (URL, license, attribution) and the ingestion script;
keep downloaded files in a git-ignored `data/raw/`. Store `source_url` and `license` on every chunk so
answers can cite and attribute correctly, and restricted chunks can be filtered out.
