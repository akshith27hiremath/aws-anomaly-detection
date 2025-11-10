import { motion } from "framer-motion";
import { BarChart3, RefreshCw, TrendingUp, Activity, PieChart } from "lucide-react";
import { useState } from "react";
import { 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  PieChart as RechartsPie, 
  Pie, 
  Cell,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend 
} from "recharts";

interface StatisticsData {
  volumeData: Array<{ time: string; volume: number }>;
  sentimentData: Array<{ category: string; value: number }>;
  anomalyTypes: Array<{ type: string; count: number }>;
}

interface StatisticsPanelProps {
  data: StatisticsData | null;
  onRefresh: () => void;
}

const COLORS = [
  "rgba(255, 255, 255, 0.9)",
  "rgba(200, 200, 200, 0.8)",
  "rgba(160, 160, 160, 0.8)",
  "rgba(120, 120, 120, 0.8)",
];

export function StatisticsPanel({ data, onRefresh }: StatisticsPanelProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await onRefresh();
    setTimeout(() => setIsRefreshing(false), 500);
  };

  return (
    <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-white" />
          <div>
            <h3 className="text-white">Statistics Dashboard</h3>
            <p className="text-white/50 text-xs">Real-time analytics & metrics</p>
          </div>
        </div>
        
        <motion.button
          onClick={handleRefresh}
          disabled={isRefreshing}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="px-4 py-2 rounded-lg backdrop-blur-sm bg-white/10 border border-white/20 text-white text-sm flex items-center gap-2 transition-all hover:bg-white/15"
        >
          <motion.div
            animate={isRefreshing ? { rotate: 360 } : {}}
            transition={{ duration: 0.5, ease: "linear" }}
          >
            <RefreshCw className="w-4 h-4" />
          </motion.div>
          Refresh
        </motion.button>
      </div>

      {data ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Volume Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="backdrop-blur-sm bg-black/20 border border-white/10 rounded-xl p-4"
          >
            <div className="flex items-center gap-2 mb-4">
              <Activity className="w-4 h-4 text-white" />
              <h4 className="text-white text-sm">Trading Volume</h4>
            </div>
            <div className="h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.volumeData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis 
                    dataKey="time" 
                    stroke="rgba(255,255,255,0.5)"
                    style={{ fontSize: '11px' }}
                  />
                  <YAxis 
                    stroke="rgba(255,255,255,0.5)"
                    style={{ fontSize: '11px' }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(0,0,0,0.9)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '8px',
                    }}
                    labelStyle={{ color: 'rgba(255,255,255,0.8)' }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="volume" 
                    stroke="rgba(255, 255, 255, 0.9)" 
                    strokeWidth={2}
                    dot={{ fill: 'rgba(255, 255, 255, 0.9)', r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Sentiment Pie Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="backdrop-blur-sm bg-black/20 border border-white/10 rounded-xl p-4"
          >
            <div className="flex items-center gap-2 mb-4">
              <PieChart className="w-4 h-4 text-white" />
              <h4 className="text-white text-sm">Sentiment Distribution</h4>
            </div>
            <div className="h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPie>
                  <Pie
                    data={data.sentimentData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.category}: ${entry.value}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {data.sentimentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(0,0,0,0.9)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '8px',
                    }}
                  />
                </RechartsPie>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Anomaly Types Bar Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="backdrop-blur-sm bg-black/20 border border-white/10 rounded-xl p-4 lg:col-span-2"
          >
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-4 h-4 text-white" />
              <h4 className="text-white text-sm">Anomaly Detection by Type</h4>
            </div>
            <div className="h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.anomalyTypes}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis 
                    dataKey="type" 
                    stroke="rgba(255,255,255,0.5)"
                    style={{ fontSize: '12px' }}
                  />
                  <YAxis 
                    stroke="rgba(255,255,255,0.5)"
                    style={{ fontSize: '12px' }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(0,0,0,0.9)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '8px',
                    }}
                    labelStyle={{ color: 'rgba(255,255,255,0.8)' }}
                  />
                  <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                    {data.anomalyTypes.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center h-[400px] text-white/40">
          <BarChart3 className="w-12 h-12 mb-3 opacity-50" />
          <p>No statistics data available</p>
          <p className="text-xs mt-2">Click "Refresh" to load analytics</p>
        </div>
      )}
    </div>
  );
}
