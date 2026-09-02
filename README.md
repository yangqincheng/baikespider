# BaikeSpider

[![CI](https://github.com/yangqincheng/baikespider/actions/workflows/ci.yml/badge.svg)](https://github.com/yangqincheng/baikespider/actions/workflows/ci.yml)
[![GitHub stars](https://img.shields.io/github/stars/yangqincheng/baikespider?style=flat-square)](https://github.com/yangqincheng/baikespider/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/yangqincheng/baikespider?style=flat-square)](https://github.com/yangqincheng/baikespider/network/members)
[![License](https://img.shields.io/github/license/yangqincheng/baikespider?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/language-Python-blue?style=flat-square)](https://www.python.org/)
[![Scrapy](https://img.shields.io/badge/framework-Scrapy-60A839?style=flat-square)](https://scrapy.org/)

**BaikeSpider** is an open-source Scrapy project for collecting structured data from Baidu Baike. It starts from multiple seed entries, follows related-entry links, extracts structured metadata, records polysemy/synonym information, persists data to MySQL, and can download representative images for collected entities.

The project is intended as a practical reference for **recursive web crawling, structured encyclopedia extraction, entity deduplication, Scrapy pipelines, MySQL persistence, and knowledge-base / knowledge-graph data preparation**.

> **Project status**
>
> BaikeSpider is maintained as an open-source reference implementation. The crawler was originally built against an earlier Baidu Baike page structure, so upstream DOM or anti-crawling changes may require selector or dependency updates before production use. Compatibility fixes, documentation improvements, tests, and modernization contributions are welcome.

## At a glance

| Area | Current implementation |
| --- | --- |
| Language | Python |
| Crawling framework | Scrapy |
| Primary spider | `baike` |
| Image spider | `pic` |
| Persistence | MySQL via PyMySQL |
| Deduplication | Scrapy request filtering + database-level entity checks |
| Long-running crawl support | Scrapy `JOBDIR` |
| Optional distributed-crawl components | `scrapy-redis` |
| Maintainer | [@yangqincheng](https://github.com/yangqincheng) |
| License | MIT |

## Highlights

- **Recursive entity discovery** — starts from multiple seed entries and follows related Baidu Baike links.
- **Structured extraction** — captures names, summaries, infobox fields, tags, related links, and entry identifiers.
- **Polysemy / synonym modeling** — stores multiple meanings and corresponding entry identifiers separately.
- **Two-layer deduplication** — combines Scrapy request filtering with database-level checks before insertion.
- **MySQL persistence** — stores entities and synonym/polysemy relationships in structured tables.
- **Image crawling pipeline** — downloads representative entry images and associates them with collected entities.
- **Resumable crawling** — supports Scrapy `JOBDIR` for interruptible long-running tasks.
- **Bloom filter experiment** — includes a Bloom filter implementation for deduplication-related experiments.
- **Open-source maintenance workflow** — includes CI, contribution guidance, issue/PR templates, and explicit code ownership.

## How it works

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

Scrapy filters duplicate requests during traversal, while the persistence layer checks entity identifiers before inserting records into MySQL.

## Data model

### `entity_table`

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
├── .env.example
├── .github/
│   ├── CODEOWNERS
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── requirements.txt
├── scrapy.cfg
└── scrapyspider/
    ├── Bloomfilter.py
    ├── items.py
    ├── middlewares.py
    ├── pipelines.py
    ├── request_seen.py
    ├── settings.py
    └── spiders/
        ├── BaiDuSpider.py
        ├── Picture_Spider.py
        ├── douban_spider.py
        └── test_spider.py
```

The primary Baidu Baike implementation lives in `scrapyspider/spiders/BaiDuSpider.py`:

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

```bash
python -m pip install -r requirements.txt
```

The declared dependencies are Scrapy, PyMySQL, and `scrapy-redis`. Because this codebase originated several years ago, newer Python/Scrapy versions may still require compatibility changes. If you encounter one, please open an issue with your environment details.

### 3. Configure MySQL

BaikeSpider does not keep database credentials in source code. Configure the connection with environment variables:

```bash
export BAIKESPIDER_DB_HOST=127.0.0.1
export BAIKESPIDER_DB_PORT=3306
export BAIKESPIDER_DB_USER=root
export BAIKESPIDER_DB_PASSWORD='your-password'
export BAIKESPIDER_DB_NAME=scrapy_baike
```

See `.env.example` for the full set of variables. The code uses local-development defaults for host, port, username, and database name, while the password defaults to an empty value.

> Do not commit real credentials or production configuration.

### 4. Configure image storage

If you want to run the image crawler, configure `IMAGES_STORE` in `scrapyspider/settings.py`. The current default is a repository-local pictures directory, which is ignored by Git.

### 5. Run the entity crawler

Run commands from the directory containing `scrapy.cfg`:

```bash
scrapy crawl baike -s JOBDIR=loginfo/baike
```

`JOBDIR` stores crawler state so an interrupted crawl can later resume. Use a separate job directory for each spider.

To stop a running crawl gracefully, press `Ctrl+C` and allow Scrapy to persist its state. Restarting with the same `JOBDIR` resumes the crawl.

### 6. Run the image crawler

After entity data has been collected into MySQL:

```bash
scrapy crawl pic -s JOBDIR=loginfo/pic
```

The image crawler reads entity identifiers from `entity_table`, visits the corresponding Baidu Baike pages, downloads representative images, and stores the image mapping through the pipeline.

## Core extraction fields

`BaiKeItem` currently exposes:

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

The entity crawler starts from a diverse set of seed entries and discovers additional `/item/...` links from each fetched page, turning the crawl into a traversal of connected encyclopedia entries rather than a fixed-list scraper.

### Deduplication

Two levels of deduplication are used:

1. Scrapy's request filtering prevents repeated scheduling of the same URL.
2. Before writing to MySQL, the pipeline checks whether the corresponding entity identifier is already present.

### Persistence

The MySQL pipeline executes generated SQL statements, commits successful operations, and closes the database connection after each operation. Database connection settings are read from `BAIKESPIDER_DB_*` environment variables so local credentials do not need to live in the repository.

### Resumability

Scrapy's `JOBDIR` mechanism persists scheduler state, allowing the crawler to resume after an intentional stop instead of restarting from the seed set.

## Maintenance and open-source workflow

BaikeSpider has been public since 2018. The current maintenance effort is focused on making the repository easier to understand, run, review, and contribute to while preserving the original project and its history.

Repository maintenance now includes:

- a documented dependency set;
- environment-based local database configuration;
- GitHub Actions syntax/dependency checks;
- `CODEOWNERS` identifying the primary maintainer;
- structured bug and improvement issue templates;
- a pull request template and contribution guide;
- an explicit MIT open-source license.

### Current priorities

- update selectors for the current Baidu Baike DOM;
- verify and document supported Python/Scrapy versions;
- add parser and persistence tests;
- migrate legacy SQL construction toward parameterized queries;
- improve retry, timeout, and error handling;
- simplify legacy/demo code paths;
- document larger-scale crawl operational practices.

## Contributing

Issues and pull requests are welcome. Good contributions include compatibility fixes, parser improvements, documentation corrections, safer configuration, tests, and crawler reliability improvements.

See [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a larger change. GitHub issue and pull request templates are provided to keep reports reproducible and changes easy to review.

## Maintainer

BaikeSpider is owned and maintained by [@yangqincheng](https://github.com/yangqincheng). Repository-wide ownership is also declared in [`.github/CODEOWNERS`](.github/CODEOWNERS).

The repository has attracted community stars and forks over time. The maintenance goal is to keep it useful as an understandable open-source reference for Scrapy-based structured encyclopedia crawling while progressively improving compatibility, configuration safety, testing, and maintainability.

## Responsible use

This repository is intended for learning, research, and engineering reference purposes. If you run the crawler against a third-party website, respect the website's terms, robots policies where applicable, rate limits, applicable laws, and the rights of data owners. Avoid unnecessarily aggressive request rates.

## License

BaikeSpider is released under the [MIT License](LICENSE).

## 中文说明

BaikeSpider 是一个基于 Scrapy 的百度百科结构化数据爬虫。项目从多个初始百科词条出发，递归发现相关词条，并提取词条名称、简介、Infobox、标签、相关链接以及多义词信息，最终保存到 MySQL；同时包含词条图片抓取、数据库二次去重和 `JOBDIR` 断点续爬等实现。

当前仓库主要作为 **Scrapy 爬虫、百科实体采集和结构化数据预处理的开源参考实现** 进行维护。近期维护已补充 MIT License、CI、CODEOWNERS、贡献指南、Issue/PR 模板、依赖声明和更安全的数据库配置，并修复了持久化流程中的明显问题。由于百度百科页面结构可能发生变化，实际运行前仍可能需要更新 XPath / selector 或依赖版本。
