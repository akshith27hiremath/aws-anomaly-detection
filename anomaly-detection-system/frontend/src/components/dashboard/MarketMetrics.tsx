import { motion } from "framer-motion";
import { BarChart3, TrendingUp, TrendingDown, Activity } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell } from "recharts";

const volumeData = [
  { name: "BTC", value: 28000, anomaly: false },
  { name: "ETH", value: 15000, anomaly: true },
  { name: "SOL", value: 8200, anomaly: false },
  { name: "ADA", value: 5400, anomaly: false },
  { name: "DOT", value: 12000, anomaly: true },
  { name: "MATIC", value: 4200, anomaly: false },
];

const metrics = [
  { label: "Market Cap", value: "$1.84T", change: "+2.4%", positive: true },
  { label: "24h Volume", value: "$89.2B", change: "+18.3%", positive: true },
  { label: "Active Traders", value: "2.4M", change: "-3.1%", positive: false },
  { label: "Network Hashrate", value: "385 EH/s", change: "+5.7%", positive: true },
];

export function MarketMetrics() {
  return (
    <div className="h-full backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
      {/* Header */}
      <div className="flex items-center gap-2 mb-6">
        <BarChart3 className="w-5 h-5 text-white" />
        <div>
          <h3 className="text-white">Market Overview</h3>
          <p className="text-white/50 text-sm">Cross-chain metrics & volume analysis</p>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        {metrics.map((metric, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.05 }}
            className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-xl p-4"
          >
            <p className="text-white/50 text-xs mb-2">{metric.label}</p>
            <div className="flex items-end justify-between">
              <p className="text-white text-xl">{metric.value}</p>
              <div className={`flex items-center gap-1 ${metric.positive ? 'text-green-400' : 'text-red-400'}`}>
                {metric.positive ? (
                  <TrendingUp className="w-3 h-3" />
                ) : (
                  <TrendingDown className="w-3 h-3" />
                )}
                <span className="text-xs">{metric.change}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Volume Chart */}
      <div className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-xl p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-white" />
            <span className="text-white text-sm">Volume Distribution</span>
          </div>
          <span className="text-white/50 text-xs">Last 24h</span>
        </div>
        
        <div className="h-[180px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={volumeData}>
              <XAxis 
                dataKey="name" 
                stroke="rgba(255,255,255,0.5)"
                style={{ fontSize: '11px' }}
              />
              <YAxis 
                stroke="rgba(255,255,255,0.5)"
                style={{ fontSize: '11px' }}
              />
              <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                {volumeData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.anomaly ? "rgba(239, 68, 68, 0.8)" : "rgba(255, 255, 255, 0.6)"} 
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
