# Contributing to BaikeSpider

Thanks for your interest in improving BaikeSpider.

BaikeSpider is maintained as an open-source reference implementation for Scrapy-based structured encyclopedia crawling. Contributions that improve compatibility, reliability, clarity, reproducibility, and responsible operation are especially useful.

## Good contribution areas

- update selectors for current Baidu Baike page structures;
- improve compatibility with current Python and Scrapy versions;
- improve local configuration and secret handling;
- improve dependency pinning or reproducible environment setup;
- improve retry, timeout, and error handling;
- add tests for parsing and persistence logic;
- migrate legacy SQL construction toward parameterized queries;
- simplify legacy/demo code paths;
- improve documentation and examples;
- improve deduplication or large-crawl operational behavior.

## Development setup

1. Fork or clone the repository.
2. Create a focused branch for your change.
3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Configure local database settings using the `BAIKESPIDER_DB_*` environment variables documented in `.env.example`.
5. Make the smallest coherent change that solves the problem.
6. Run the repository checks before opening a pull request:

   ```bash
   python -m compileall -q scrapyspider
   ```

## Before opening a pull request

1. Keep changes focused and easy to review.
2. Explain the problem being solved and the approach taken.
3. If changing crawler behavior, include the Python/Scrapy version you tested with.
4. Do not commit real credentials, private data, cookies, tokens, or large generated crawl outputs.
5. When updating selectors, describe the page structure or example entry used for validation.
6. Update the README when setup, configuration, or user-visible behavior changes.

## Issues

Use the provided GitHub issue templates when possible. Bug reports are most useful when they include:

- Python version;
- Scrapy version;
- operating system;
- command used to run the spider;
- relevant traceback or log excerpt;
- example Baidu Baike page, when applicable.

Please redact credentials, cookies, tokens, and private data before posting logs.

## Pull requests

A good pull request should contain:

- a concise title;
- a short explanation of why the change is needed;
- a summary of the implementation;
- testing or validation notes;
- compatibility notes when behavior depends on a particular Baidu Baike page structure.

Small documentation-only fixes are welcome as well.

Repository-wide ownership is declared in `.github/CODEOWNERS`; the primary maintainer reviews project changes.

## Responsible use

Please keep contributions aligned with responsible crawling practices. Avoid changes whose primary purpose is to bypass access controls, defeat anti-abuse mechanisms, or enable unnecessarily aggressive request behavior.

## License

By contributing to this repository, you agree that your contributions will be licensed under the repository's [MIT License](LICENSE).

## Maintainer

The repository is maintained by [@yangqincheng](https://github.com/yangqincheng).
