import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, AlertTriangle, Activity, RefreshCw } from "lucide-react";
import * as api from "../../services/api";

interface OIPanelProps {
  onRefresh?: () => void;
}

export function OIPanel({ onRefresh }: OIPanelProps) {
  const [oiData, setOIData] = useState<api.OICurrentData | null>(null);
  const [divergences, setDivergences] = useState<api.OIDivergence[]>([]);
  const [fundingRates, setFundingRates] = useState<api.FundingRatesResponse | null>(null);
  const [ratios, setRatios] = useState<api.LongShortRatiosResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchOIData = async () => {
    try {
      setLoading(true);
      const [currentData, divergenceData, fundingData, ratioData] = await Promise.all([
        api.fetchOICurrent(),
        api.fetchOIDivergences(),
        api.fetchFundingRates(),
        api.fetchLongShortRatios(),
      ]);

      setOIData(currentData);
      setDivergences(divergenceData.divergences);
      setFundingRates(fundingData);
      setRatios(ratioData);
    } catch (error) {
      console.error('Failed to fetch OI data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOIData();

    // Refresh every 30 seconds
    const interval = setInterval(fetchOIData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    fetchOIData();
    onRefresh?.();
  };

  const formatOI = (value: number) => {
    if (value >= 1000000) return `${(value / 1000000).toFixed(2)}M`;
    if (value >= 1000) return `${(value / 1000).toFixed(2)}K`;
    return value.toFixed(2);
  };

  const formatFundingRate = (rate: number) => {
    return `${(rate * 100).toFixed(4)}%`;
  };

  const getFundingRateColor = (rate: number) => {
    const absRate = Math.abs(rate);
    if (absRate > 0.1) return "text-red-400";
    if (absRate > 0.05) return "text-yellow-400";
    return "text-green-400";
  };

  const getRatioColor = (ratio: number) => {
    if (ratio > 3 || ratio < 0.33) return "text-red-400";
    if (ratio > 2 || ratio < 0.5) return "text-yellow-400";
    return "text-green-400";
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high': return 'bg-red-500/20 border-red-500/50 text-red-400';
      case 'medium': return 'bg-yellow-500/20 border-yellow-500/50 text-yellow-400';
      default: return 'bg-blue-500/20 border-blue-500/50 text-blue-400';
    }
  };

  if (loading && !oiData) {
    return (
      <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
        <div className="flex items-center justify-center h-64">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          >
            <RefreshCw className="w-8 h-8 text-white/50" />
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 backdrop-blur-sm bg-purple-500/20 border border-purple-500/30 rounded-xl flex items-center justify-center">
            <Activity className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h3 className="text-white font-medium">Open Interest Derivatives</h3>
            <p className="text-white/50 text-sm">Futures Market Analytics</p>
          </div>
        </div>

        <motion.button
          onClick={handleRefresh}
          whileHover={{ scale: 1.05, rotate: 180 }}
          whileTap={{ scale: 0.95 }}
          className="backdrop-blur-sm bg-white/10 border border-white/20 rounded-xl p-2 text-white/70 hover:text-white transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
        </motion.button>
      </div>

      {/* Divergence Alerts */}
      {divergences.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-4 h-4 text-yellow-400" />
            <h4 className="text-white/90 text-sm font-medium">Active Divergences ({divergences.length})</h4>
          </div>
          <div className="space-y-2">
            {divergences.slice(0, 3).map((div, idx) => (
              <motion.div
                key={div.anomaly_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                className={`backdrop-blur-sm border rounded-xl p-3 ${getSeverityColor(div.severity)}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <span className="text-white/90 font-medium text-sm">{div.symbol}</span>
                  <span className="text-xs px-2 py-0.5 rounded bg-white/10">{div.severity.toUpperCase()}</span>
                </div>
                <p className="text-white/70 text-xs leading-relaxed">{div.explanation}</p>
                <div className="flex items-center gap-3 mt-2 text-xs text-white/50">
                  <span>Confidence: {(div.confidence * 100).toFixed(0)}%</span>
                  <span>•</span>
                  <span>{new Date(div.timestamp).toLocaleTimeString()}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Symbol Data Grid */}
      {oiData && (
        <div className="space-y-4">
          {Object.entries(oiData.data).map(([symbol, data], idx) => (
            <motion.div
              key={symbol}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-xl p-4"
            >
              {/* Symbol Header */}
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-white font-medium">{symbol}</h4>
                {ratios && ratios.ratios[symbol]?.global && (
                  <div className="flex items-center gap-1">
                    {ratios.ratios[symbol].global!.ratio > 1 ? (
                      <TrendingUp className={`w-4 h-4 ${getRatioColor(ratios.ratios[symbol].global!.ratio)}`} />
                    ) : (
                      <TrendingDown className={`w-4 h-4 ${getRatioColor(ratios.ratios[symbol].global!.ratio)}`} />
                    )}
                    <span className={`text-xs ${getRatioColor(ratios.ratios[symbol].global!.ratio)}`}>
                      {ratios.ratios[symbol].global!.ratio.toFixed(2)}:1
                    </span>
                  </div>
                )}
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 gap-3">
                {/* Open Interest */}
                <div className="backdrop-blur-sm bg-white/5 rounded-lg p-3">
                  <div className="text-white/50 text-xs mb-1">Open Interest</div>
                  <div className="text-white font-medium">{data.open_interest ? formatOI(data.open_interest) : 'N/A'}</div>
                </div>

                {/* Funding Rate */}
                {fundingRates && fundingRates.funding_rates[symbol] && (
                  <div className="backdrop-blur-sm bg-white/5 rounded-lg p-3">
                    <div className="text-white/50 text-xs mb-1">Funding Rate</div>
                    <div className={`font-medium ${getFundingRateColor(fundingRates.funding_rates[symbol].rate)}`}>
                      {formatFundingRate(fundingRates.funding_rates[symbol].rate)}
                    </div>
                  </div>
                )}

                {/* Long/Short Ratio */}
                {data.long_short_ratio && (
                  <div className="backdrop-blur-sm bg-white/5 rounded-lg p-3">
                    <div className="text-white/50 text-xs mb-1">L/S Ratio (Global)</div>
                    <div className={`font-medium ${getRatioColor(data.long_short_ratio)}`}>
                      {data.long_short_ratio.toFixed(2)}:1
                    </div>
                  </div>
                )}

                {/* Top Trader Ratio */}
                {data.top_trader_long_short_ratio && (
                  <div className="backdrop-blur-sm bg-white/5 rounded-lg p-3">
                    <div className="text-white/50 text-xs mb-1">L/S Ratio (Top)</div>
                    <div className={`font-medium ${getRatioColor(data.top_trader_long_short_ratio)}`}>
                      {data.top_trader_long_short_ratio.toFixed(2)}:1
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* No Data Message */}
      {!oiData && !loading && (
        <div className="text-center py-8 text-white/50">
          <Activity className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No OI data available</p>
        </div>
      )}
    </div>
  );
}
