//+------------------------------------------------------------------+
//| NLT_SMA_Crossover.mq5                                            |
//| Nature Law Trading - https://naturelawtrading.com                |
//| MIT License - https://github.com/stmastria-data/code             |
//|                                                                  |
//| Fast/slow SMA crossover with ATR stop and risk-based sizing.     |
//| Same rules as pinescript/strategies/nlt_sma_crossover.pine and   |
//| python/examples/sma_crossover.py, so results can be compared.    |
//|                                                                  |
//| Signals are evaluated once per bar on the last CLOSED bar.       |
//| Educational example. Not financial advice. Test on demo first.   |
//+------------------------------------------------------------------+
#property copyright "Nature Law Trading - MIT License"
#property link      "https://naturelawtrading.com"
#property version   "0.10"
#property description "SMA crossover with ATR stop and percent-risk position sizing."

#include <Trade/Trade.mqh>
#include <NatureLaw/RiskManager.mqh>

//--- Inputs
input group "Rules"
input int    InpFastPeriod   = 20;        // Fast SMA period
input int    InpSlowPeriod   = 50;        // Slow SMA period
input bool   InpAllowShort   = false;     // Allow short positions

input group "Risk"
input double InpRiskPercent  = 1.0;       // Risk per trade, % of equity
input int    InpAtrPeriod    = 14;        // ATR period
input double InpAtrMult      = 3.0;       // ATR stop multiple (0 = no stop)
input double InpFixedLots    = 0.10;      // Lots used when there is no stop

input group "Execution"
input ulong  InpMagic        = 20261017;  // Magic number
input int    InpDeviationPts = 10;        // Max slippage, points

//--- Globals
CTrade   g_trade;
int      g_hFast = INVALID_HANDLE;
int      g_hSlow = INVALID_HANDLE;
int      g_hAtr  = INVALID_HANDLE;
datetime g_lastBarTime = 0;

//+------------------------------------------------------------------+
int OnInit()
  {
   if(InpFastPeriod < 1 || InpFastPeriod >= InpSlowPeriod)
     {
      Print("Fast period must be >= 1 and shorter than slow period.");
      return INIT_PARAMETERS_INCORRECT;
     }
   if(InpRiskPercent <= 0.0 || InpAtrMult < 0.0)
     {
      Print("Risk percent must be positive and ATR multiple non-negative.");
      return INIT_PARAMETERS_INCORRECT;
     }

   g_hFast = iMA(_Symbol, _Period, InpFastPeriod, 0, MODE_SMA, PRICE_CLOSE);
   g_hSlow = iMA(_Symbol, _Period, InpSlowPeriod, 0, MODE_SMA, PRICE_CLOSE);
   g_hAtr  = iATR(_Symbol, _Period, InpAtrPeriod);
   if(g_hFast == INVALID_HANDLE || g_hSlow == INVALID_HANDLE || g_hAtr == INVALID_HANDLE)
     {
      Print("Failed to create indicator handles, error ", GetLastError());
      return INIT_FAILED;
     }

   g_trade.SetExpertMagicNumber(InpMagic);
   g_trade.SetDeviationInPoints(InpDeviationPts);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   return INIT_SUCCEEDED;
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(g_hFast != INVALID_HANDLE) IndicatorRelease(g_hFast);
   if(g_hSlow != INVALID_HANDLE) IndicatorRelease(g_hSlow);
   if(g_hAtr  != INVALID_HANDLE) IndicatorRelease(g_hAtr);
  }

//+------------------------------------------------------------------+
//| True once per bar, on the first tick of a new bar.               |
//+------------------------------------------------------------------+
bool IsNewBar()
  {
   const datetime barTime = iTime(_Symbol, _Period, 0);
   if(barTime == 0 || barTime == g_lastBarTime)
      return false;
   g_lastBarTime = barTime;
   return true;
  }

//+------------------------------------------------------------------+
//| +1 long, -1 short, 0 flat for this symbol and magic number.      |
//+------------------------------------------------------------------+
int CurrentDirection()
  {
   for(int i = PositionsTotal() - 1; i >= 0; --i)
     {
      const ulong ticket = PositionGetTicket(i);
      if(ticket == 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != InpMagic)
         continue;
      return PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1;
     }
   return 0;
  }

//+------------------------------------------------------------------+
void CloseOwnPositions()
  {
   for(int i = PositionsTotal() - 1; i >= 0; --i)
     {
      const ulong ticket = PositionGetTicket(i);
      if(ticket == 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != InpMagic)
         continue;
      if(!g_trade.PositionClose(ticket))
         PrintFormat("Close failed for #%I64u: %u %s", ticket,
                     g_trade.ResultRetcode(), g_trade.ResultRetcodeDescription());
     }
  }

//+------------------------------------------------------------------+
void OpenPosition(const bool isLong, const double atr)
  {
   const double price = isLong ? SymbolInfoDouble(_Symbol, SYMBOL_ASK)
                               : SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double sl     = 0.0;
   double volume = CRiskManager::NormalizeVolume(_Symbol, InpFixedLots);

   if(InpAtrMult > 0.0)
     {
      sl     = CRiskManager::AtrStop(_Symbol, price, atr, InpAtrMult, isLong);
      volume = CRiskManager::LotsForRisk(_Symbol, InpRiskPercent, price, sl);
     }

   if(volume <= 0.0)
     {
      Print("Trade skipped: volume below the minimum lot for the requested risk.");
      return;
     }

   const string comment = "NLT SMAx";
   const bool ok = isLong ? g_trade.Buy(volume, _Symbol, 0.0, sl, 0.0, comment)
                          : g_trade.Sell(volume, _Symbol, 0.0, sl, 0.0, comment);
   if(!ok)
      PrintFormat("Order failed: %u %s", g_trade.ResultRetcode(),
                  g_trade.ResultRetcodeDescription());
  }

//+------------------------------------------------------------------+
void OnTick()
  {
   if(!IsNewBar())
      return;

   //--- Index 0 = last closed bar, index 1 = the bar before it.
   double fast[], slow[], atr[];
   ArraySetAsSeries(fast, true);
   ArraySetAsSeries(slow, true);
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(g_hFast, 0, 1, 2, fast) != 2 ||
      CopyBuffer(g_hSlow, 0, 1, 2, slow) != 2 ||
      CopyBuffer(g_hAtr,  0, 1, 1, atr)  != 1)
      return;

   const bool crossUp   = fast[0] > slow[0] && fast[1] <= slow[1];
   const bool crossDown = fast[0] < slow[0] && fast[1] >= slow[1];
   const int  direction = CurrentDirection();

   if(crossUp)
     {
      if(direction < 0)
         CloseOwnPositions();
      if(direction <= 0)
         OpenPosition(true, atr[0]);
     }
   else if(crossDown)
     {
      if(direction > 0)
         CloseOwnPositions();
      if(InpAllowShort && direction >= 0)
         OpenPosition(false, atr[0]);
     }
  }
//+------------------------------------------------------------------+
