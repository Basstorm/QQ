//+------------------------------------------------------------------+
//| QuantumQueenApproxNonRisky.mq5                                   |
//| Approximate non-risky Quantum Queen strategies for MT5 backtest.  |
//+------------------------------------------------------------------+
#property strict
#property version "0.12"

#include <Trade/Trade.mqh>

input ulong  MagicBase        = 26061001;
input double BalancePer001Lot = 400.0;
input int    SlippagePoints   = 30;
input double TpSpreadCompensationPoints    = 0.30;
input double AddOnSpreadCompensationPoints = 0.30;
input bool   RequireCurrentM15Confirmation = true;
input bool   UseS01           = true;
input bool   UseS03           = true;
input bool   UseS04           = true;
input bool   UseS08           = true;
input bool   UseS09           = true;

CTrade trade;
datetime lastM15Bar = 0;
datetime lastM1Bar = 0;
bool PreviousSignal[5];

struct StrategyConfig
{
   string Name;
   bool Enabled;
   int MagicOffset;
   int MaxLayers;
};

StrategyConfig Strategies[5];

int OnInit()
{
   trade.SetDeviationInPoints(SlippagePoints);
   Strategies[0].Name = "T1/S01"; Strategies[0].Enabled = UseS01; Strategies[0].MagicOffset = 101; Strategies[0].MaxLayers = 8;
   Strategies[1].Name = "T2/S03"; Strategies[1].Enabled = UseS03; Strategies[1].MagicOffset = 203; Strategies[1].MaxLayers = 8;
   Strategies[2].Name = "T2/S04"; Strategies[2].Enabled = UseS04; Strategies[2].MagicOffset = 204; Strategies[2].MaxLayers = 6;
   Strategies[3].Name = "T4/S08"; Strategies[3].Enabled = UseS08; Strategies[3].MagicOffset = 408; Strategies[3].MaxLayers = 4;
   Strategies[4].Name = "T5/S09"; Strategies[4].Enabled = UseS09; Strategies[4].MagicOffset = 509; Strategies[4].MaxLayers = 3;
   return INIT_SUCCEEDED;
}

void OnTick()
{
   datetime m1 = iTime(_Symbol, PERIOD_M1, 0);
   if(m1 != lastM1Bar)
   {
      lastM1Bar = m1;
      ManageOpenBaskets();
   }

   datetime m15 = iTime(_Symbol, PERIOD_M15, 0);
   if(m15 != lastM15Bar)
   {
      lastM15Bar = m15;
      CheckEntries();
   }
}

void CheckEntries()
{
   for(int i = 0; i < ArraySize(Strategies); i++)
   {
      if(!Strategies[i].Enabled) continue;
      bool closedBarSignal = EntrySignal(Strategies[i].Name, 1);
      bool currentSignal = closedBarSignal && (!RequireCurrentM15Confirmation || EntrySignal(Strategies[i].Name, 0));
      bool edge = SignalRisingEdge(i, currentSignal);
      if(CountBasketPositions(Strategies[i].MagicOffset) > 0) continue;
      if(edge)
         OpenInitial(Strategies[i]);
   }
}

bool SignalRisingEdge(const int strategyIndex, const bool currentSignal)
{
   bool edge = currentSignal && !PreviousSignal[strategyIndex];
   PreviousSignal[strategyIndex] = currentSignal;
   return edge;
}

void ManageOpenBaskets()
{
   for(int i = 0; i < ArraySize(Strategies); i++)
   {
      if(!Strategies[i].Enabled) continue;
      MaybeCloseBasket(Strategies[i]);
      MaybeOpenAddOn(Strategies[i]);
   }
}

bool EntrySignal(const string name, const int shift)
{
   if(name == "T1/S01")
      return CCI(20, shift) >= 130.5291 && DIMinus(7, shift) <= 8.1907 && DIPlus(7, shift) >= 33.2559;
   if(name == "T2/S03")
      return MASlope(MODE_LWMA, 50, 4, shift) >= 1.3709 && WMA(21, shift) - WMA(50, shift) >= 3.9578 && MASlope(MODE_SMA, 21, 4, shift) >= 1.8114;
   if(name == "T2/S04")
      return DIMinus(21, shift) <= 11.2552 && ROC(34, shift) >= 0.8966 && MASlope(MODE_SMA, 21, 4, shift) >= 2.3986;
   if(name == "T4/S08")
      return ADXMain(21, shift) >= 50.6542 && iClose(_Symbol, PERIOD_M15, shift) - EMA(50, shift) >= 15.5052;
   if(name == "T5/S09")
      return CMO(14, shift) >= 70.0936 && CMO(21, shift) >= 59.3097 && CHOP(14, shift) <= 28.5623;
   return false;
}

void OpenInitial(const StrategyConfig &cfg)
{
   double lot = BaseLot();
   if(lot <= 0.0) return;
   trade.SetExpertMagicNumber(MagicBase + cfg.MagicOffset);
   trade.Buy(lot, _Symbol, 0.0, 0.0, 0.0, "QQApprox " + cfg.Name);
}

void MaybeOpenAddOn(const StrategyConfig &cfg)
{
   int layers = CountBasketPositions(cfg.MagicOffset);
   if(layers <= 0 || layers >= cfg.MaxLayers) return;

   double threshold = 0.0;
   double minMinutes = 0.0;
   if(!AddOnRule(cfg.Name, layers, threshold, minMinutes)) return;

   double lastPrice = 0.0;
   datetime lastTime = 0;
   if(!LastEntry(cfg.MagicOffset, lastPrice, lastTime)) return;

   double close = iClose(_Symbol, PERIOD_M1, 1);
   double adverse = lastPrice - close - AddOnSpreadCompensationPoints;
   double minutes = (TimeCurrent() - lastTime) / 60.0;
   if(adverse >= threshold && minutes >= minMinutes)
   {
      double lot = BaseLot();
      if(lot <= 0.0) return;
      trade.SetExpertMagicNumber(MagicBase + cfg.MagicOffset);
      trade.Buy(lot, _Symbol, 0.0, 0.0, 0.0, "QQApprox add " + cfg.Name);
   }
}

void MaybeCloseBasket(const StrategyConfig &cfg)
{
   int layers = CountBasketPositions(cfg.MagicOffset);
   if(layers <= 0) return;

   double tp = MathMax(0.01, ExitTp(cfg.Name, layers) - TpSpreadCompensationPoints);
   if(tp <= 0.0) return;
   double vwap = BasketVwap(cfg.MagicOffset);
   double close = iClose(_Symbol, PERIOD_M1, 1);
   if(close - vwap >= tp)
      CloseBasket(cfg.MagicOffset);
}

double BaseLot()
{
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double raw = MathFloor(balance / BalancePer001Lot) * 0.01;
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   if(raw < minLot) raw = minLot;
   if(raw > maxLot) raw = maxLot;
   return MathFloor(raw / step) * step;
}

bool AddOnRule(const string name, const int layers, double &threshold, double &minMinutes)
{
   threshold = 0.0;
   minMinutes = 0.0;
   if(name == "T1/S01")
   {
      if(layers == 1){ threshold = 1.46; minMinutes = 0.0; return true; }
      if(layers == 2){ threshold = 1.685; minMinutes = 0.0; return true; }
      if(layers == 3){ threshold = 1.52; minMinutes = 0.0; return true; }
      if(layers == 4){ threshold = 1.67; minMinutes = 5.0; return true; }
      if(layers == 5){ threshold = 1.835; minMinutes = 0.0; return true; }
      if(layers == 6){ threshold = 1.4125; minMinutes = 0.0; return true; }
      if(layers >= 7){ threshold = 1.77; minMinutes = 0.0; return true; }
   }
   if(name == "T2/S03")
   {
      if(layers == 1){ threshold = 1.62; minMinutes = 0.0; return true; }
      if(layers == 2){ threshold = 1.70; minMinutes = 0.0; return true; }
      if(layers == 3){ threshold = 1.64; minMinutes = 5.0; return true; }
      if(layers == 4){ threshold = 1.57; minMinutes = 5.2; return true; }
      if(layers == 5){ threshold = 1.48; minMinutes = 0.0; return true; }
      if(layers == 6){ threshold = 1.6975; minMinutes = 0.0; return true; }
      if(layers >= 7){ threshold = 1.50; minMinutes = 0.0; return true; }
   }
   if(name == "T2/S04")
   {
      if(layers == 1){ threshold = 1.745; minMinutes = 0.0; return true; }
      if(layers == 2){ threshold = 1.645; minMinutes = 0.0; return true; }
      if(layers == 3){ threshold = 1.91; minMinutes = 3.8; return true; }
      if(layers == 4){ threshold = 1.77; minMinutes = 2.7; return true; }
      if(layers == 5){ threshold = 1.77; minMinutes = 5.0; return true; }
      if(layers >= 6){ threshold = 1.955; minMinutes = 8.75; return true; }
   }
   if(name == "T4/S08")
   {
      if(layers == 1){ threshold = 1.64; minMinutes = 3.0; return true; }
      if(layers == 2){ threshold = 1.69; minMinutes = 7.0; return true; }
      if(layers == 3){ threshold = 1.82; minMinutes = 0.0; return true; }
      if(layers >= 4){ threshold = 1.80; minMinutes = 0.0; return true; }
   }
   if(name == "T5/S09")
   {
      if(layers == 1){ threshold = 5.57; minMinutes = 0.0; return true; }
      if(layers == 2){ threshold = 5.39; minMinutes = 0.0; return true; }
      if(layers >= 3){ threshold = 5.49; minMinutes = 33.0; return true; }
   }
   return false;
}

double ExitTp(const string name, const int layers)
{
   if(name == "T1/S01")
   {
      if(layers == 1) return 0.56;
      if(layers == 2) return 0.34;
      if(layers == 3) return 0.51;
      if(layers == 4) return 0.20;
      if(layers == 5) return 4.15;
      if(layers == 6) return 0.52;
      if(layers == 7) return 1.95;
      return 0.80;
   }
   if(name == "T2/S03")
   {
      if(layers == 1) return 0.49;
      if(layers == 2) return 0.51;
      if(layers == 3) return 0.53;
      if(layers == 4) return 0.11;
      if(layers == 5) return 0.67;
      if(layers == 6) return 0.54;
      return 0.73;
   }
   if(name == "T2/S04")
   {
      if(layers == 1) return 0.43;
      if(layers == 2) return 0.35;
      if(layers == 3) return 0.32;
      if(layers == 4) return 0.59;
      if(layers == 5) return 0.75;
      return 0.55;
   }
   if(name == "T4/S08")
   {
      if(layers == 1) return 1.78;
      return 1.40;
   }
   if(name == "T5/S09")
   {
      if(layers == 1) return 1.86;
      return 2.29;
   }
   return 0.0;
}

int CountBasketPositions(const int magicOffset)
{
   int count = 0;
   ulong magic = MagicBase + magicOffset;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol && (ulong)PositionGetInteger(POSITION_MAGIC) == magic)
         count++;
   }
   return count;
}

double BasketVwap(const int magicOffset)
{
   double volume = 0.0;
   double weighted = 0.0;
   ulong magic = MagicBase + magicOffset;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol || (ulong)PositionGetInteger(POSITION_MAGIC) != magic) continue;
      double lot = PositionGetDouble(POSITION_VOLUME);
      volume += lot;
      weighted += lot * PositionGetDouble(POSITION_PRICE_OPEN);
   }
   if(volume <= 0.0) return 0.0;
   return weighted / volume;
}

bool LastEntry(const int magicOffset, double &price, datetime &entryTime)
{
   bool found = false;
   entryTime = 0;
   ulong magic = MagicBase + magicOffset;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol || (ulong)PositionGetInteger(POSITION_MAGIC) != magic) continue;
      datetime t = (datetime)PositionGetInteger(POSITION_TIME);
      if(!found || t > entryTime)
      {
         entryTime = t;
         price = PositionGetDouble(POSITION_PRICE_OPEN);
         found = true;
      }
   }
   return found;
}

void CloseBasket(const int magicOffset)
{
   ulong magic = MagicBase + magicOffset;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol && (ulong)PositionGetInteger(POSITION_MAGIC) == magic)
         trade.PositionClose(ticket);
   }
}

double IndicatorBuffer(const int handle, const int buffer, const int shift)
{
   if(handle == INVALID_HANDLE) return 0.0;
   double values[];
   ArraySetAsSeries(values, true);
   if(CopyBuffer(handle, buffer, shift, 1, values) != 1)
   {
      IndicatorRelease(handle);
      return 0.0;
   }
   IndicatorRelease(handle);
   return values[0];
}

double CCI(const int period, const int shift)
{
   return IndicatorBuffer(iCCI(_Symbol, PERIOD_M15, period, PRICE_TYPICAL), 0, shift);
}

double ADXMain(const int period, const int shift)
{
   return IndicatorBuffer(iADX(_Symbol, PERIOD_M15, period), 0, shift);
}

double DIPlus(const int period, const int shift)
{
   return IndicatorBuffer(iADX(_Symbol, PERIOD_M15, period), 1, shift);
}

double DIMinus(const int period, const int shift)
{
   return IndicatorBuffer(iADX(_Symbol, PERIOD_M15, period), 2, shift);
}

double MA(const ENUM_MA_METHOD method, const int period, const int shift)
{
   return IndicatorBuffer(iMA(_Symbol, PERIOD_M15, period, 0, method, PRICE_CLOSE), 0, shift);
}

double SMA(const int period, const int shift)
{
   return MA(MODE_SMA, period, shift);
}

double EMA(const int period, const int shift)
{
   return MA(MODE_EMA, period, shift);
}

double WMA(const int period, const int shift)
{
   return MA(MODE_LWMA, period, shift);
}

double MASlope(const ENUM_MA_METHOD method, const int period, const int bars, const int shift)
{
   return MA(method, period, shift) - MA(method, period, shift + bars);
}

double ROC(const int period, const int shift)
{
   if(iBars(_Symbol, PERIOD_M15) <= shift + period) return 0.0;
   double current = iClose(_Symbol, PERIOD_M15, shift);
   double previous = iClose(_Symbol, PERIOD_M15, shift + period);
   if(previous == 0.0) return 0.0;
   return (current / previous - 1.0) * 100.0;
}

double CMO(const int period, const int shift)
{
   if(iBars(_Symbol, PERIOD_M15) <= shift + period + 1) return 0.0;
   double up = 0.0;
   double down = 0.0;
   for(int i = shift; i < shift + period; i++)
   {
      double diff = iClose(_Symbol, PERIOD_M15, i) - iClose(_Symbol, PERIOD_M15, i + 1);
      if(diff > 0.0) up += diff;
      else down -= diff;
   }
   double denom = up + down;
   if(denom == 0.0) return 0.0;
   return 100.0 * (up - down) / denom;
}

double CHOP(const int period, const int shift)
{
   if(iBars(_Symbol, PERIOD_M15) <= shift + period + 1) return 100.0;
   double trSum = 0.0;
   double highest = -DBL_MAX;
   double lowest = DBL_MAX;
   for(int i = shift; i < shift + period; i++)
   {
      double high = iHigh(_Symbol, PERIOD_M15, i);
      double low = iLow(_Symbol, PERIOD_M15, i);
      double prevClose = iClose(_Symbol, PERIOD_M15, i + 1);
      double tr = MathMax(high - low, MathMax(MathAbs(high - prevClose), MathAbs(low - prevClose)));
      trSum += tr;
      highest = MathMax(highest, high);
      lowest = MathMin(lowest, low);
   }
   double range = highest - lowest;
   if(range <= 0.0 || trSum <= 0.0) return 100.0;
   return 100.0 * MathLog10(trSum / range) / MathLog10((double)period);
}
