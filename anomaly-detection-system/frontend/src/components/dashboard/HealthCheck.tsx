import { motion } from "framer-motion";
import { Activity, RefreshCw } from "lucide-react";
import { useState } from "react";

interface HealthCheckProps {
  status: string;
  onCheckHealth: () => void;
}

export function HealthCheck({ status, onCheckHealth }: HealthCheckProps) {
  const [isChecking, setIsChecking] = useState(false);

  const handleCheck = async () => {
    setIsChecking(true);
    await onCheckHealth();
    setTimeout(() => setIsChecking(false), 500);
  };

  return (
    <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-white" />
          <h3 className="text-white">System Health</h3>
        </div>
        
        <motion.button
          onClick={handleCheck}
          disabled={isChecking}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="px-4 py-2 rounded-lg backdrop-blur-sm bg-white/10 border border-white/20 text-white text-sm flex items-center gap-2 transition-all hover:bg-white/15"
        >
          <motion.div
            animate={isChecking ? { rotate: 360 } : {}}
            transition={{ duration: 0.5, ease: "linear" }}
          >
            <RefreshCw className="w-4 h-4" />
          </motion.div>
          Check Health
        </motion.button>
      </div>

      {/* Status Display */}
      <motion.div
        key={status}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-xl p-4"
      >
        <div className="flex items-start gap-3">
          <motion.div
            animate={{ 
              scale: [1, 1.2, 1],
              opacity: [0.6, 1, 0.6]
            }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-3 h-3 rounded-full bg-green-400 mt-1 flex-shrink-0"
          />
          <div className="flex-1">
            <p className="text-white/90 leading-relaxed">{status}</p>
          </div>
        </div>
      </motion.div>

      {/* Additional Info */}
      <div className="mt-4 grid grid-cols-2 gap-3">
        <div className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-lg p-3">
          <p className="text-white/50 text-xs mb-1">Uptime</p>
          <p className="text-white text-sm">99.8%</p>
        </div>
        <div className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-lg p-3">
          <p className="text-white/50 text-xs mb-1">Response Time</p>
          <p className="text-white text-sm">24ms</p>
        </div>
      </div>
    </div>
  );
}
