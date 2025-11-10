import { motion } from "framer-motion";
import { Database, RefreshCw, CheckCircle, AlertCircle, Clock } from "lucide-react";
import { useState } from "react";

interface DataSource {
  name: string;
  status: string;
  lastUpdate: string;
  reliability: number;
}

interface DataSourcesProps {
  sources: DataSource[];
  onUpdate: () => void;
}

export function DataSources({ sources, onUpdate }: DataSourcesProps) {
  const [isUpdating, setIsUpdating] = useState(false);

  const handleUpdate = async () => {
    setIsUpdating(true);
    await onUpdate();
    setTimeout(() => setIsUpdating(false), 500);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active":
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case "delayed":
        return <Clock className="w-4 h-4 text-yellow-400" />;
      case "error":
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      default:
        return <CheckCircle className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "rgba(34, 197, 94, 0.3)";
      case "delayed":
        return "rgba(251, 191, 36, 0.3)";
      case "error":
        return "rgba(239, 68, 68, 0.3)";
      default:
        return "rgba(156, 163, 175, 0.3)";
    }
  };

  return (
    <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Database className="w-5 h-5 text-white" />
          <div>
            <h3 className="text-white">Data Sources</h3>
            <p className="text-white/50 text-xs">Active feed monitors</p>
          </div>
        </div>
        
        <motion.button
          onClick={handleUpdate}
          disabled={isUpdating}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="px-4 py-2 rounded-lg backdrop-blur-sm bg-white/10 border border-white/20 text-white text-sm flex items-center gap-2 transition-all hover:bg-white/15"
        >
          <motion.div
            animate={isUpdating ? { rotate: 360 } : {}}
            transition={{ duration: 0.5, ease: "linear" }}
          >
            <RefreshCw className="w-4 h-4" />
          </motion.div>
          Update
        </motion.button>
      </div>

      {/* Sources List */}
      <div className="space-y-2 max-h-[600px] overflow-y-auto custom-scrollbar pr-2">
        {sources.length > 0 ? (
          sources.map((source, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              whileHover={{ scale: 1.02, x: 5 }}
              className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-xl p-4"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getStatusIcon(source.status)}
                  <span className="text-white text-sm">{source.name}</span>
                </div>
                <span className="text-white/50 text-xs">{source.lastUpdate}</span>
              </div>

              {/* Reliability Bar */}
              <div className="flex items-center gap-2">
                <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${source.reliability}%` }}
                    transition={{ duration: 1, delay: index * 0.05 }}
                    className="h-full rounded-full"
                    style={{ backgroundColor: getStatusColor(source.status) }}
                  />
                </div>
                <span className="text-white/60 text-xs w-12 text-right">
                  {source.reliability}%
                </span>
              </div>
            </motion.div>
          ))
        ) : (
          <div className="flex flex-col items-center justify-center py-12 text-white/40">
            <Database className="w-10 h-10 mb-2 opacity-50" />
            <p className="text-sm">No data sources available</p>
            <p className="text-xs mt-1">Click "Update" to load sources</p>
          </div>
        )}
      </div>

      {/* Summary */}
      {sources.length > 0 && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <div className="grid grid-cols-3 gap-2">
            <div className="text-center backdrop-blur-sm bg-white/5 border border-white/10 rounded-lg p-2">
              <p className="text-white text-lg">{sources.filter(s => s.status === "active").length}</p>
              <p className="text-white/50 text-xs">Active</p>
            </div>
            <div className="text-center backdrop-blur-sm bg-white/5 border border-white/10 rounded-lg p-2">
              <p className="text-white text-lg">{sources.length}</p>
              <p className="text-white/50 text-xs">Total</p>
            </div>
            <div className="text-center backdrop-blur-sm bg-white/5 border border-white/10 rounded-lg p-2">
              <p className="text-white text-lg">
                {sources.length > 0 ? Math.round(sources.reduce((acc, s) => acc + s.reliability, 0) / sources.length) : 0}%
              </p>
              <p className="text-white/50 text-xs">Avg</p>
            </div>
          </div>
        </div>
      )}

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
