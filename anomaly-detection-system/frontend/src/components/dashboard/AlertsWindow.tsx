import { motion } from "framer-motion";
import { AlertTriangle, AlertCircle, Info, CheckCircle } from "lucide-react";

const alerts = [
  {
    type: "critical",
    icon: AlertTriangle,
    title: "Price Spike Detected",
    message: "BTC experienced 8.2% increase in 15 minutes. Pattern analysis suggests whale activity.",
    time: "2 min ago",
  },
  {
    type: "warning",
    icon: AlertCircle,
    title: "Volume Anomaly",
    message: "Trading volume 340% above average. Multiple models flagged irregular behavior.",
    time: "8 min ago",
  },
  {
    type: "info",
    icon: Info,
    title: "Sentiment Shift",
    message: "Social sentiment changed from neutral to highly bullish. Correlation detected with price movement.",
    time: "15 min ago",
  },
  {
    type: "success",
    icon: CheckCircle,
    title: "Pattern Recognized",
    message: "Neural network identified similar pre-rally conditions from historical data.",
    time: "23 min ago",
  },
  {
    type: "warning",
    icon: AlertCircle,
    title: "Network Congestion",
    message: "On-chain metrics show increased transaction activity. Possible market event incoming.",
    time: "31 min ago",
  },
];

const alertColors = {
  critical: "rgba(239, 68, 68, 0.8)",
  warning: "rgba(251, 191, 36, 0.8)",
  info: "rgba(59, 130, 246, 0.8)",
  success: "rgba(34, 197, 94, 0.8)",
};

export function AlertsWindow() {
  return (
    <div className="h-full backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6 flex flex-col">
      {/* Header */}
      <div className="mb-4">
        <h3 className="text-white mb-1">Anomaly Alerts</h3>
        <p className="text-white/50 text-sm">Real-time detection feed</p>
      </div>

      {/* Alerts List */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
        {alerts.map((alert, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.02, x: 5 }}
            className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-xl p-4"
          >
            <div className="flex gap-3">
              <motion.div
                animate={{ 
                  scale: alert.type === "critical" ? [1, 1.2, 1] : 1,
                }}
                transition={{ duration: 2, repeat: Infinity }}
                className="flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: alertColors[alert.type as keyof typeof alertColors] }}
              >
                <alert.icon className="w-5 h-5 text-white" />
              </motion.div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2 mb-1">
                  <h4 className="text-white text-sm">{alert.title}</h4>
                  <span className="text-white/40 text-xs flex-shrink-0">{alert.time}</span>
                </div>
                <p className="text-white/60 text-sm leading-relaxed">{alert.message}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.2);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.3);
        }
      `}</style>
    </div>
  );
}
