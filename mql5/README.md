# MQL5

Expert Advisors, indicators, scripts and include files for **MetaTrader 5**.

The folders mirror the `MQL5` directory of a MetaTrader 5 terminal, so they can be copied in
as they are.

| Folder | Contents |
| --- | --- |
| `Experts/` | Expert Advisors (`.mq5`) that trade automatically |
| `Indicators/` | Custom indicators (`.mq5`) |
| `Scripts/` | One-shot scripts (`.mq5`) run on a chart |
| `Include/NatureLaw/` | Shared code (`.mqh`) used by the files above |
| `templates/` | Starting points with the standard header and layout |

## Files

| File | Type | What it does |
| --- | --- | --- |
| `Experts/NLT_SMA_Crossover.mq5` | Expert Advisor | SMA crossover with ATR stop and percent-of-equity sizing |
| `Indicators/NLT_RSI_Bands.mq5` | Indicator | RSI with adaptive bands, same logic as the Pine Script version |
| `Scripts/NLT_PositionSizeCalculator.mq5` | Script | Shows the lot size for a given risk and stop distance; places no orders |
| `Include/NatureLaw/RiskManager.mqh` | Include | Volume normalisation, loss per lot, risk-based lots, ATR stops |

## Installation

1. In MetaTrader 5 open **File → Open Data Folder**, then the `MQL5` folder.
2. Copy `Experts`, `Indicators`, `Scripts` and `Include` from this folder into it, merging with
   the existing folders.
3. Open MetaEditor (F4), open each `.mq5` file and press **Compile** (F7).
4. Back in the terminal, refresh the **Navigator** and drag the program onto a chart.

Always run an Expert Advisor in the **Strategy Tester** and on a **demo account** before using
it on a live account.

## Conventions

- **File names** are `PascalCase` with the `NLT_` prefix; shared code lives in
  `Include/NatureLaw/` and is included with `#include <NatureLaw/...>`.
- **Header**: every file starts with the licence block and a short description, plus
  `#property copyright`, `link`, `version` and `description`.
- **ASCII only** in source files, to avoid encoding problems in MetaEditor.
- **Inputs** use the `Inp` prefix, a trailing comment as label, and `input group` sections.
- **Globals** use the `g_` prefix. Indicator handles are created in `OnInit` and released in
  `OnDeinit`.
- **Signals** are read from closed bars (shift 1 or more) once per new bar, so backtests match
  live behaviour.
- **Experts** set a magic number and only manage their own positions.
- **Version**: bump `#property version` when behaviour changes.

## Disclaimer

Educational material, not financial advice. Automated trading carries significant risk.
