//+------------------------------------------------------------------+
//| RiskManager.mqh                                                  |
//| Nature Law Trading - https://naturelawtrading.com                |
//| MIT License - https://github.com/stmastria-data/code             |
//|                                                                  |
//| Position sizing helpers shared by Experts and Scripts.           |
//| Include with:  #include <NatureLaw/RiskManager.mqh>              |
//+------------------------------------------------------------------+
#ifndef NATURELAW_RISKMANAGER_MQH
#define NATURELAW_RISKMANAGER_MQH

class CRiskManager
  {
public:
   //--- Round a volume down to the symbol's volume step and clamp it to the
   //--- allowed range. Returns 0 when the volume is below the minimum lot,
   //--- so callers never silently take more risk than requested.
   static double     NormalizeVolume(const string symbol, double volume)
     {
      const double minVolume = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
      const double maxVolume = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
      const double step      = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
      if(step <= 0.0 || volume <= 0.0)
         return 0.0;

      volume = MathFloor(volume / step + 1e-9) * step;
      if(volume < minVolume)
         return 0.0;
      volume = MathMin(volume, maxVolume);

      const int digits = (int)MathMax(0.0, MathCeil(-MathLog10(step)));
      return NormalizeDouble(volume, digits);
     }

   //--- Money lost by 1.0 lot if price moves from entry to stop.
   static double     LossPerLot(const string symbol, const double entry, const double stop)
     {
      const double tickSize  = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
      const double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE_LOSS);
      const double distance  = MathAbs(entry - stop);
      if(tickSize <= 0.0 || tickValue <= 0.0 || distance <= 0.0)
         return 0.0;
      return distance / tickSize * tickValue;
     }

   //--- Lots such that hitting the stop loses riskPercent % of equity.
   //--- Returns 0 when the trade cannot be sized within the risk budget.
   static double     LotsForRisk(const string symbol, const double riskPercent,
                                 const double entry, const double stop)
     {
      const double lossPerLot = LossPerLot(symbol, entry, stop);
      if(lossPerLot <= 0.0 || riskPercent <= 0.0)
         return 0.0;
      const double riskMoney = AccountInfoDouble(ACCOUNT_EQUITY) * riskPercent / 100.0;
      return NormalizeVolume(symbol, riskMoney / lossPerLot);
     }

   //--- Stop price 'mult' ATRs away from entry on the losing side, rounded
   //--- to the symbol's digits.
   static double     AtrStop(const string symbol, const double entry, const double atr,
                             const double mult, const bool isLong)
     {
      const int digits = (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS);
      const double stop = isLong ? entry - mult * atr : entry + mult * atr;
      return NormalizeDouble(stop, digits);
     }
  };

#endif // NATURELAW_RISKMANAGER_MQH
