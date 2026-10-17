# Contributing

Thanks for helping improve these tools. Contributions of any size are welcome.

## Workflow

1. Fork the repository, or create a branch if you have write access.
2. Make your change in the folder for its platform: `python/`, `pinescript/` or `mql5/`.
3. Follow the conventions in that folder's README and start new files from its `templates/`.
4. Open a pull request describing what changed and how you tested it.

## Checks before opening a pull request

- **Python**: run `ruff check .`, `ruff format --check .` and `pytest` inside `python/`. New
  functions need tests.
- **Pine Script**: the script compiles without errors or warnings in the TradingView Pine
  Editor, and a screenshot of it on a chart is attached to the pull request.
- **MQL5**: the file compiles in MetaEditor with 0 errors and 0 warnings. For Expert Advisors,
  include a short Strategy Tester summary with symbol, timeframe and period.

## What does not belong here

- **No credentials.** API keys, broker logins, account numbers and `.env` files must never be
  committed. Use `python/.env.example` as a reference for local configuration.
- **No proprietary or team-only code.** This repository is public. Private strategies and live
  parameters go in the private team repository.
- **No market data files.** Data may carry licence restrictions; link to the source instead.

## Licence

By contributing you agree that your contributions are released under the MIT License of this
repository.
