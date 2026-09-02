# Contributing to BaikeSpider

Thanks for your interest in improving BaikeSpider.

BaikeSpider is maintained as an open-source reference implementation for Scrapy-based structured encyclopedia crawling. Contributions that improve compatibility, reliability, clarity, and reproducibility are especially useful.

## Good contribution areas

- update selectors for current Baidu Baike page structures;
- improve compatibility with current Python and Scrapy versions;
- move local configuration and credentials out of source code;
- add dependency pinning or reproducible environment setup;
- improve retry, timeout, and error handling;
- add tests for parsing and persistence logic;
- simplify legacy/demo code paths;
- improve documentation and examples;
- improve deduplication or large-crawl operational behavior.

## Before opening a pull request

1. Keep changes focused and easy to review.
2. Explain the problem being solved and the approach taken.
3. If changing crawler behavior, include the Python/Scrapy version you tested with.
4. Do not commit real credentials, private data, or large generated crawl outputs.
5. When updating selectors, describe the page structure or example entry used for validation.

## Issues

Bug reports are most useful when they include:

- Python version;
- Scrapy version;
- operating system;
- command used to run the spider;
- relevant traceback or log excerpt;
- example Baidu Baike page, when applicable.

## Pull requests

A good pull request should contain:

- a concise title;
- a short explanation of why the change is needed;
- a summary of the implementation;
- testing or validation notes.

Small documentation-only fixes are welcome as well.

## Responsible use

Please keep contributions aligned with responsible crawling practices. Avoid changes whose primary purpose is to bypass access controls or enable unnecessarily aggressive request behavior.

## Maintainer

The repository is maintained by [@yangqincheng](https://github.com/yangqincheng).
