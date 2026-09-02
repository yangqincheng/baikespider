# BaikeSpider

[![GitHub stars](https://img.shields.io/github/stars/yangqincheng/baikespider?style=flat-square)](https://github.com/yangqincheng/baikespider/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/yangqincheng/baikespider?style=flat-square)](https://github.com/yangqincheng/baikespider/network/members)
[![Python](https://img.shields.io/badge/language-Python-blue?style=flat-square)](https://www.python.org/)

**BaikeSpider** is an open-source Scrapy project for collecting structured data from Baidu Baike. It crawls encyclopedia entities from multiple seed pages, follows related-entry links, extracts structured metadata, records polysemy/synonym information, and can download representative images for collected entities.

The project was created as a practical implementation of large-scale encyclopedia crawling and structured-data preprocessing. It is useful as a reference for Scrapy crawling pipelines, recursive graph-style traversal, entity deduplication, MySQL persistence, and knowledge-base / knowledge-graph data preparation experiments.

> **Project status**
>
> BaikeSpider is maintained as an open-source reference implementation. The current crawler was originally built against an earlier Baidu Baike page structure, so upstream DOM or anti-crawling changes may require selector or dependency updates before production use. Compatibility fixes, documentation improvements, and modernization contributions are welcome.

## Highlights

- **Recursive entity discovery** — starts from multiple seed entries and follows related Baidu Baike links to discover additional entities.
- **Structured extraction** — captures entity name, summary/description, infobox fields, tags, related infobox links, and entry identifiers.
- **Polysemy / synonym modeling** — stores multiple meanings and corresponding entry identifiers in a separate table.
- **Two-layer deduplication** — uses Scrapy request deduplication during crawling and performs an additional database-level check before insertion.
- **MySQL persistence** — stores crawled entities and synonym/polysemy relationships in structured tables.
- **Image crawling pipeline** — downloads representative entry images and associates them with collected entities.
- **Resumable crawling** — supports Scrapy `JOBDIR`, allowing long-running crawling tasks to be stopped and resumed.
- **Bloom filter experiment** — includes a Bloom filter implementation for deduplication-related experiments.

## How it works

BaikeSpider treats Baidu Baike as a graph of connected encyclopedia entries.

```text
Seed entries
    |
    v
Fetch Baidu Baike page
    |
    +--> Extract entity metadata
    |      - name
    |      - description
    |      - infobox
    |      - tags
    |      - related links
    |      - polysemy data
    |
    +--> Persist structured data to MySQL
    |
    +--> Discover /item/... links
             |
             v
        Schedule next entries
```

This traversal continues as Scrapy discovers new entry URLs. Scrapy filters duplicate requests, while the persistence layer performs an additional check by entity identifier before inserting records.

## Data model

The crawler primarily works with two tables.

### `entity_table`

Stores the structured representation of a Baidu Baike entry.

| Field | Description |
| --- | --- |
| `id` | Auto-increment database identifier |
| `oid` | Entry identifier derived from the Baidu Baike URL |
| `name` | Entity / entry name |
| `descrip` | Entry summary |
| `infobox` | Structured infobox fields serialized as text |
| `infolink` | Links discovered from infobox values |
| `tag` | Baidu Baike entry tags |

### `synonym_table`

Stores polysemy / same-name relationships.

| Field | Description |
| --- | --- |
| `id` | Auto-increment database identifier |
| `name` | Shared entity name |
| `descrip` | Meaning / description for the corresponding sense |
| `oid` | Entry identifier for that sense |

The image pipeline can additionally associate downloaded image names with entity records.

## Repository structure

```text
baikespider/
├── README.md
├── scrapy.cfg
└── scrapyspider/
    ├── Bloomfilter.py
    ├── items.py
    ├── middlewares.py
    ├── pipelines.py
    ├── request_seen.py
    ├── settings.py
    ├── picture/
    └── spiders/
        ├── BaiDuSpider.py
        ├── Picture_Spider.py
        ├── douban_spider.py
        └── test_spider.py
```

The main Baidu Baike implementation lives in `scrapyspider/spiders/BaiDuSpider.py`:

- `BaiKeSpider` (`name = "baike"`) crawls and stores structured encyclopedia entries.
- `PicturesSpider` (`name = "pic"`) reads collected entity identifiers and downloads representative images.

`douban_spider.py` and some test code are retained from the project's early Scrapy learning / experimentation stage and are not the primary Baike crawler.

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/yangqincheng/baikespider.git
cd baikespider
```

### 2. Install dependencies

The project uses Scrapy and PyMySQL. `urllib` functionality used by the crawler is provided by Python's standard library.

```bash
pip install scrapy pymysql
```

Because this codebase originated several years ago, newer Scrapy/Python versions may require small compatibility changes. If you run into one, please open an issue or submit a pull request with the environment details.

### 3. Configure MySQL

Create a MySQL database (the original project uses `scrapy_baike`) and configure the connection parameters in `scrapyspider/pipelines.py` before running the crawler.

The pipeline contains helper methods for creating the entity and synonym tables. The expected schemas are documented in the [Data model](#data-model) section above.

> **Security note:** do not commit production database credentials. Replace local-development defaults with credentials appropriate for your own environment.

### 4. Configure image storage

If you want to run the image crawler, configure `IMAGES_STORE` in `scrapyspider/settings.py` to point to the directory where downloaded images should be stored.

### 5. Run the entity crawler

Run commands from the directory containing `scrapy.cfg`.

```bash
scrapy crawl baike -s JOBDIR=loginfo/baike
```

`JOBDIR` stores crawler state so an interrupted crawl can later resume. Use a separate job directory for each spider.

To stop a running crawl gracefully, press `Ctrl+C` and allow Scrapy to finish persisting its state. Restarting with the same `JOBDIR` resumes the crawl.

### 6. Run the image crawler

After entity data has been collected into MySQL:

```bash
scrapy crawl pic -s JOBDIR=loginfo/pic
```

The image crawler reads entity identifiers from `entity_table`, visits the corresponding Baidu Baike pages, downloads representative images, and stores the image mapping through the pipeline.

## Core extraction fields

`BaiKeItem` currently exposes the following fields:

```text
name
 descrip
 infobox
 tag
 oid
 infolink
 polysemy
```

`PicturesItem` tracks image URLs, downloaded image metadata, file paths, image names, counters, and the corresponding entity identifier.

## Design notes

### Recursive crawling

The entity crawler begins with a diverse set of seed entries and then discovers additional `/item/...` links from each fetched page. This turns the crawler into a breadth of connected encyclopedia entries rather than a fixed list scraper.

### Deduplication

Two levels of deduplication are used:

1. Scrapy's request filtering prevents the same URL from being scheduled repeatedly.
2. Before writing to MySQL, the pipeline checks whether the corresponding `oid` is already present.

This is particularly useful when multiple pages lead to the same entity or when polysemous entry names are involved.

### Resumability

Long-running crawls are expected to be interruptible. Scrapy's `JOBDIR` mechanism persists scheduler state, allowing the crawler to resume from the previous run instead of restarting from the seed set.

## Maintenance priorities

The repository is intentionally kept public as a working/reference implementation. Useful future improvements include:

- update selectors for the current Baidu Baike DOM;
- move database configuration fully to environment variables or a local config file;
- add pinned dependency versions and reproducible environment setup;
- improve error handling and retry behavior;
- add automated tests for parsers and persistence logic;
- simplify legacy/demo code paths;
- document larger-scale crawl operational practices.

Contributions in these areas are especially welcome.

## Contributing

Issues and pull requests are welcome. Good contributions include compatibility fixes, parser improvements, documentation corrections, safer configuration, tests, and crawler reliability improvements.

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for a lightweight contribution guide.

## Maintainer

BaikeSpider is owned and maintained by [@yangqincheng](https://github.com/yangqincheng).

The repository has been public since 2018 and has attracted community stars and forks over time. The goal of the current maintenance effort is to preserve the project as a useful, understandable reference for Scrapy-based structured encyclopedia crawling while progressively improving compatibility and maintainability.

## Responsible use

This repository is intended for learning, research, and engineering reference purposes. If you run the crawler against a third-party website, respect the website's terms, robots policies where applicable, rate limits, applicable laws, and the rights of data owners. Avoid unnecessarily aggressive request rates.

## 中文说明

BaikeSpider 是一个基于 Scrapy 的百度百科结构化数据爬虫。项目从多个初始百科词条出发，递归发现相关词条，并提取词条名称、简介、Infobox、标签、相关链接以及多义词信息，最终保存到 MySQL；同时包含词条图片抓取、数据库二次去重和 `JOBDIR` 断点续爬等实现。

这个仓库目前主要作为 **Scrapy 爬虫、百科实体采集和结构化数据预处理的开源参考实现** 进行维护。由于百度百科页面结构可能发生变化，实际运行前可能需要更新 XPath / selector 或依赖版本。如果你发现兼容性问题，欢迎提交 Issue 或 Pull Request。
