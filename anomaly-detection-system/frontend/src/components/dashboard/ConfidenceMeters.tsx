import { motion } from "framer-motion";
import { Brain, Target, Zap } from "lucide-react";

const models = [
  { name: "LSTM Network", confidence: 94.2, icon: Brain, color: "rgba(59, 130, 246, 0.8)" },
  { name: "Pattern Recognition", confidence: 87.5, icon: Target, color: "rgba(168, 85, 247, 0.8)" },
  { name: "Sentiment Analysis", confidence: 91.8, icon: Zap, color: "rgba(34, 197, 94, 0.8)" },
];

export function ConfidenceMeters() {
  return (
    <div className="h-full backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-white mb-1">Model Confidence</h3>
        <p className="text-white/50 text-sm">Neural network accuracy scores</p>
      </div>

      {/* Confidence Meters */}
      <div className="space-y-6">
        {models.map((model, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-xl p-4"
          >
            <div className="flex items-center gap-3 mb-3">
              <motion.div
                animate={{ rotate: [0, 360] }}
                transition={{ duration: 8 + index * 2, repeat: Infinity, ease: "linear" }}
                className="w-10 h-10 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: model.color }}
              >
                <model.icon className="w-5 h-5 text-white" />
              </motion.div>
              <div className="flex-1">
                <p className="text-white text-sm">{model.name}</p>
                <p className="text-white/50 text-xs">Active</p>
              </div>
              <div className="text-right">
                <p className="text-white">{model.confidence}%</p>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="relative h-2 bg-white/10 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${model.confidence}%` }}
                transition={{ duration: 1.5, delay: index * 0.2, ease: "easeOut" }}
                className="absolute inset-y-0 left-0 rounded-full"
                style={{ backgroundColor: model.color }}
              >
                <motion.div
                  animate={{ 
                    opacity: [0.5, 1, 0.5],
                    x: ['-100%', '200%']
                  }}
                  transition={{ 
                    opacity: { duration: 2, repeat: Infinity },
                    x: { duration: 1.5, repeat: Infinity, ease: "linear" }
                  }}
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                />
              </motion.div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Overall Status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="mt-6 backdrop-blur-sm bg-white/5 border border-white/10 rounded-xl p-4"
      >
        <div className="flex items-center justify-between mb-2">
          <span className="text-white/70 text-sm">Overall System Confidence</span>
          <motion.div
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-2 h-2 rounded-full bg-green-400"
          />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-white text-3xl">91.2%</span>
          <span className="text-green-400 text-sm">+2.3%</span>
        </div>
        <p className="text-white/50 text-xs mt-2">All models operating optimally</p>
      </motion.div>
    </div>
  );
}
