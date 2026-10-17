//+------------------------------------------------------------------+
//| NLT_PositionSizeCalculator.mq5                                   |
//| Nature Law Trading - https://naturelawtrading.com                |
//| MIT License - https://github.com/stmastria-data/code             |
//|                                                                  |
//| Drop on a chart: shows the lot size that risks a given percent   |
//| of equity for a stop at the given distance. Places no orders.    |
//+------------------------------------------------------------------+
#property copyright "Nature Law Trading - MIT License"
#property link      "https://naturelawtrading.com"
#property version   "0.10"
#property description "Lot size for a percent-of-equity risk. Places no orders."
#property script_show_inputs

#include <NatureLaw/RiskManager.mqh>

input double InpRiskPercent = 1.0;    // Risk per trade, % of equity
input int    InpStopPoints  = 200;    // Stop distance, points
input bool   InpIsLong      = true;   // Long (true) or short (false)

//+------------------------------------------------------------------+
void OnStart()
  {
   if(InpStopPoints <= 0 || InpRiskPercent <= 0.0)
     {
      Alert("Stop distance and risk percent must be positive.");
      return;
     }

   const double entry = InpIsLong ? SymbolInfoDouble(_Symbol, SYMBOL_ASK)
                                  : SymbolInfoDouble(_Symbol, SYMBOL_BID);
   const double stop  = InpIsLong ? entry - InpStopPoints * _Point
                                  : entry + InpStopPoints * _Point;

   const double equity     = AccountInfoDouble(ACCOUNT_EQUITY);
   const double lossPerLot = CRiskManager::LossPerLot(_Symbol, entry, stop);
   const double lots       = CRiskManager::LotsForRisk(_Symbol, InpRiskPercent, entry, stop);
   const string currency   = AccountInfoString(ACCOUNT_CURRENCY);

   string text = StringFormat(
      "%s %s\nEntry: %s   Stop: %s (%d points)\nEquity: %.2f %s   Risk: %.2f%% = %.2f %s\n"
      "Loss per 1.0 lot: %.2f %s\n\nLot size: %s",
      _Symbol, InpIsLong ? "LONG" : "SHORT",
      DoubleToString(entry, _Digits), DoubleToString(stop, _Digits), InpStopPoints,
      equity, currency, InpRiskPercent, equity * InpRiskPercent / 100.0, currency,
      lossPerLot, currency,
      lots > 0.0 ? DoubleToString(lots, 2) : "below minimum lot");

   Print(text);
   MessageBox(text, "NLT Position size", MB_OK | MB_ICONINFORMATION);
  }
//+------------------------------------------------------------------+
