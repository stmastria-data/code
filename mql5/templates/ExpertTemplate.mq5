//+------------------------------------------------------------------+
//| <Name>.mq5                                                       |
//| Nature Law Trading - https://naturelawtrading.com                |
//| MIT License - https://github.com/stmastria-data/code             |
//|                                                                  |
//| <One or two sentences describing entry and exit rules.>          |
//| Educational example. Not financial advice. Test on demo first.   |
//+------------------------------------------------------------------+
#property copyright "Nature Law Trading - MIT License"
#property link      "https://naturelawtrading.com"
#property version   "0.10"
#property description "<Short description shown in the terminal.>"

#include <Trade/Trade.mqh>
#include <NatureLaw/RiskManager.mqh>

//--- Inputs
input group "Rules"
input int    InpPeriod      = 20;        // Main period

input group "Risk"
input double InpRiskPercent = 1.0;       // Risk per trade, % of equity

input group "Execution"
input ulong  InpMagic       = 0;         // Magic number (set a unique value)

//--- Globals
CTrade   g_trade;
datetime g_lastBarTime = 0;

//+------------------------------------------------------------------+
int OnInit()
  {
   //--- Validate inputs, create indicator handles here.
   g_trade.SetExpertMagicNumber(InpMagic);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   return INIT_SUCCEEDED;
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   //--- Release indicator handles here.
  }

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
void OnTick()
  {
   if(!IsNewBar())
      return;
   //--- Read indicator values on closed bars (shift >= 1), then trade.
  }
//+------------------------------------------------------------------+
