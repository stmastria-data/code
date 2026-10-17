# Nature Law Trading · Open-source code

**The official open-source code space of the [Nature Law Trading](https://naturelawtrading.com)
project.**

[English](#about-the-project) · [Italiano](#il-progetto)

Indicators, strategies and quantitative tools from
[naturelawtrading.com](https://naturelawtrading.com), organised by platform.

| Folder | Platform | Contents |
| --- | --- | --- |
| [`python/`](python/) | Python 3.10+ | `quanttools` package: data loading, indicators, vectorised backtests, risk metrics, portfolio weights |
| [`pinescript/`](pinescript/) | TradingView, Pine Script v6 | Indicators, strategies and libraries |
| [`mql5/`](mql5/) | MetaTrader 5 | Expert Advisors, indicators, scripts and shared include files |

The same ideas appear on each platform where it makes sense. For example, the SMA crossover
exists as a Python example, a Pine Script strategy and an MQL5 Expert Advisor with the same
rules, so results can be cross-checked.

## About the project

This repository is where the [Nature Law Trading](https://naturelawtrading.com) project
publishes its code. The tools, indicators and strategies discussed on
[naturelawtrading.com](https://naturelawtrading.com) are released here so that anyone can read
how they work, use them on their own charts and suggest improvements.

- **Website**: [naturelawtrading.com](https://naturelawtrading.com) is the home of the project.
- **Code**: this repository holds the open-source implementations, for TradingView, MetaTrader 5
  and Python.
- **Questions and bug reports**: open an
  [issue](https://github.com/stmastria-data/code/issues) on this repository.

## Il progetto

Questo repository è lo spazio in cui il progetto
[Nature Law Trading](https://naturelawtrading.com) pubblica il proprio codice. Gli strumenti,
gli indicatori e le strategie di cui si parla su
[naturelawtrading.com](https://naturelawtrading.com) vengono rilasciati qui, così chiunque può
vedere come funzionano, usarli sui propri grafici e proporre miglioramenti.

- **Sito**: [naturelawtrading.com](https://naturelawtrading.com) è la casa del progetto.
- **Codice**: questo repository contiene le implementazioni open source per TradingView,
  MetaTrader 5 e Python.
- **Domande e segnalazioni**: apri una
  [issue](https://github.com/stmastria-data/code/issues) su questo repository.

Il codice è rilasciato con licenza MIT. È materiale didattico e non costituisce consulenza
finanziaria.

## Quick start

**Python**

```bash
cd python
pip install -e ".[dev]"
pytest
python examples/sma_crossover.py
```

**Pine Script**: open a `.pine` file, paste it into the TradingView Pine Editor and click
*Add to chart*. See [`pinescript/README.md`](pinescript/README.md).

**MQL5**: copy the folders into your terminal's `MQL5` data folder and compile in MetaEditor.
See [`mql5/README.md`](mql5/README.md).

## Repository layout

```
.
├── python/            quanttools package, tests and examples
│   ├── src/quanttools/
│   ├── tests/
│   └── examples/
├── pinescript/
│   ├── indicators/
│   ├── strategies/
│   ├── libraries/
│   └── templates/
├── mql5/
│   ├── Experts/
│   ├── Indicators/
│   ├── Scripts/
│   ├── Include/NatureLaw/
│   └── templates/
├── CONTRIBUTING.md
└── LICENSE            MIT
```

## Public and team-only code

Everything in this repository is **public**. Proprietary strategies, live parameters and
anything meant only for the working team belong in a separate private repository, never here:
visibility on GitHub is per repository, and anything pushed here can be copied immediately
and stays in the git history.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Licence and disclaimer

Released under the [MIT License](LICENSE).

This code is educational material, not financial advice. Trading involves substantial risk of
loss. Backtest results do not guarantee future performance. Test everything on demo accounts
first.
