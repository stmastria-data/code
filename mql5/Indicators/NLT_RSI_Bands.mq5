//+------------------------------------------------------------------+
//| NLT_RSI_Bands.mq5                                                |
//| Nature Law Trading - https://naturelawtrading.com                |
//| MIT License - https://github.com/stmastria-data/code             |
//|                                                                  |
//| RSI with dynamic overbought/oversold bands: mean +/- k standard  |
//| deviations of the RSI over a lookback. Same logic as             |
//| pinescript/indicators/nlt_rsi_bands.pine.                        |
//+------------------------------------------------------------------+
#property copyright "Nature Law Trading - MIT License"
#property link      "https://naturelawtrading.com"
#property version   "0.10"
#property description "RSI with adaptive bands (mean +/- k standard deviations)."

#property indicator_separate_window
#property indicator_minimum 0
#property indicator_maximum 100
#property indicator_level1  30
#property indicator_level2  70
#property indicator_levelstyle STYLE_DOT
#property indicator_buffers 4
#property indicator_plots   4

#property indicator_label1  "RSI"
#property indicator_type1   DRAW_LINE
#property indicator_color1  clrDodgerBlue
#property indicator_width1  2

#property indicator_label2  "Upper band"
#property indicator_type2   DRAW_LINE
#property indicator_color2  clrIndianRed

#property indicator_label3  "Lower band"
#property indicator_type3   DRAW_LINE
#property indicator_color3  clrSeaGreen

#property indicator_label4  "Band middle"
#property indicator_type4   DRAW_LINE
#property indicator_color4  clrGray
#property indicator_style4  STYLE_DOT

//--- Inputs
input int                InpRsiPeriod  = 14;           // RSI period
input ENUM_APPLIED_PRICE InpPrice      = PRICE_CLOSE;  // Applied price
input int                InpBandPeriod = 100;          // Band lookback
input double             InpBandMult   = 1.5;          // Std-dev multiplier

//--- Buffers
double g_rsi[];
double g_upper[];
double g_lower[];
double g_mid[];

int g_hRsi = INVALID_HANDLE;

//+------------------------------------------------------------------+
int OnInit()
  {
   if(InpRsiPeriod < 2 || InpBandPeriod < 2 || InpBandMult <= 0.0)
     {
      Print("Invalid parameters.");
      return INIT_PARAMETERS_INCORRECT;
     }

   SetIndexBuffer(0, g_rsi,   INDICATOR_DATA);
   SetIndexBuffer(1, g_upper, INDICATOR_DATA);
   SetIndexBuffer(2, g_lower, INDICATOR_DATA);
   SetIndexBuffer(3, g_mid,   INDICATOR_DATA);

   const int bandBegin = InpRsiPeriod + InpBandPeriod - 1;
   PlotIndexSetInteger(0, PLOT_DRAW_BEGIN, InpRsiPeriod);
   for(int p = 1; p <= 3; ++p)
     {
      PlotIndexSetInteger(p, PLOT_DRAW_BEGIN, bandBegin);
      PlotIndexSetDouble(p, PLOT_EMPTY_VALUE, EMPTY_VALUE);
     }

   IndicatorSetString(INDICATOR_SHORTNAME,
                      StringFormat("NLT RSI Bands(%d, %d, %.1f)", InpRsiPeriod, InpBandPeriod, InpBandMult));
   IndicatorSetInteger(INDICATOR_DIGITS, 2);

   g_hRsi = iRSI(_Symbol, _Period, InpRsiPeriod, InpPrice);
   if(g_hRsi == INVALID_HANDLE)
     {
      Print("Failed to create RSI handle, error ", GetLastError());
      return INIT_FAILED;
     }
   return INIT_SUCCEEDED;
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(g_hRsi != INVALID_HANDLE)
      IndicatorRelease(g_hRsi);
  }

//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
  {
   if(rates_total <= InpRsiPeriod)
      return 0;
   if(BarsCalculated(g_hRsi) < rates_total)
      return 0;

   //--- Copy only the bars that changed since the last call.
   const int toCopy = (prev_calculated <= 0 || prev_calculated > rates_total)
                      ? rates_total
                      : rates_total - prev_calculated + 1;
   if(CopyBuffer(g_hRsi, 0, 0, toCopy, g_rsi) <= 0)
      return 0;

   const int bandBegin = InpRsiPeriod + InpBandPeriod - 1;
   const int start     = (prev_calculated <= 0) ? 0 : prev_calculated - 1;

   for(int i = start; i < rates_total; ++i)
     {
      if(i < bandBegin)
        {
         g_upper[i] = EMPTY_VALUE;
         g_lower[i] = EMPTY_VALUE;
         g_mid[i]   = EMPTY_VALUE;
         continue;
        }

      //--- Population mean and standard deviation of the last InpBandPeriod RSI values.
      double sum = 0.0, sumSq = 0.0;
      for(int k = i - InpBandPeriod + 1; k <= i; ++k)
        {
         sum   += g_rsi[k];
         sumSq += g_rsi[k] * g_rsi[k];
        }
      const double mean     = sum / InpBandPeriod;
      const double variance = MathMax(sumSq / InpBandPeriod - mean * mean, 0.0);
      const double dev      = MathSqrt(variance);

      g_mid[i]   = mean;
      g_upper[i] = MathMin(mean + InpBandMult * dev, 100.0);
      g_lower[i] = MathMax(mean - InpBandMult * dev, 0.0);
     }

   return rates_total;
  }
//+------------------------------------------------------------------+
