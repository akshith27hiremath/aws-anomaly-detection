import { motion } from "framer-motion";
import { TrendingUp, AlertCircle } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart, ReferenceDot } from "recharts";

// Mock data with anomalies
const data = [
  { time: "00:00", price: 42000, anomaly: false },
  { time: "02:00", price: 42150, anomaly: false },
  { time: "04:00", price: 41900, anomaly: false },
  { time: "06:00", price: 42300, anomaly: false },
  { time: "08:00", price: 43200, anomaly: true },
  { time: "10:00", price: 42800, anomaly: false },
  { time: "12:00", price: 42950, anomaly: false },
  { time: "14:00", price: 41500, anomaly: true },
  { time: "16:00", price: 42100, anomaly: false },
  { time: "18:00", price: 42600, anomaly: false },
  { time: "20:00", price: 43100, anomaly: false },
  { time: "22:00", price: 43400, anomaly: false },
];

export function AnomalyChart() {
  return (
    <div className="h-full backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="w-5 h-5 text-white" />
            <h3 className="text-white">Market Analysis</h3>
          </div>
          <p className="text-white/50 text-sm">BTC/USD - 24h Anomaly Detection</p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-white" />
            <span className="text-white/60 text-sm">Price</span>
          </div>
          <div className="flex items-center gap-2">
            <motion.div 
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-3 h-3 rounded-full bg-red-400"
            />
            <span className="text-white/60 text-sm">Anomaly</span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-[400px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="rgba(255,255,255,0.3)" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="rgba(255,255,255,0.1)" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis 
              dataKey="time" 
              stroke="rgba(255,255,255,0.5)"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="rgba(255,255,255,0.5)"
              style={{ fontSize: '12px' }}
              domain={['dataMin - 500', 'dataMax + 500']}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'rgba(0,0,0,0.9)',
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: '8px',
                backdropFilter: 'blur(10px)'
              }}
              labelStyle={{ color: 'rgba(255,255,255,0.8)' }}
            />
            <Area 
              type="monotone" 
              dataKey="price" 
              stroke="rgba(255,255,255,0.8)" 
              strokeWidth={2}
              fill="url(#priceGradient)" 
            />
            {data.map((entry, index) => 
              entry.anomaly ? (
                <ReferenceDot
                  key={index}
                  x={entry.time}
                  y={entry.price}
                  r={8}
                  fill="rgba(239, 68, 68, 0.8)"
                  stroke="rgba(255,255,255,0.5)"
                  strokeWidth={2}
                />
              ) : null
            )}
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Bottom Stats */}
      <div className="grid grid-cols-4 gap-4 mt-6 pt-4 border-t border-white/10">
        {[
          { label: "Current Price", value: "$43,400" },
          { label: "24h Change", value: "+3.4%" },
          { label: "Anomalies Detected", value: "2" },
          { label: "Confidence", value: "94.2%" },
        ].map((stat, index) => (
          <div key={index} className="text-center">
            <p className="text-white/50 text-xs mb-1">{stat.label}</p>
            <p className="text-white">{stat.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
