import { motion } from "framer-motion";
import { FileText, Sparkles } from "lucide-react";
import { useState } from "react";

interface AnalysisPanelProps {
  analysisText: string;
  onFetchAnalysis: () => void;
}

export function AnalysisPanel({ analysisText, onFetchAnalysis }: AnalysisPanelProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleFetch = async () => {
    setIsLoading(true);
    await onFetchAnalysis();
    setTimeout(() => setIsLoading(false), 800);
  };

  return (
    <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-white" />
          <div>
            <h3 className="text-white">Latest Analysis</h3>
            <p className="text-white/50 text-xs">AI-Generated Market Intelligence</p>
          </div>
        </div>
        
        <motion.button
          onClick={handleFetch}
          disabled={isLoading}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="px-5 py-2.5 rounded-lg backdrop-blur-sm bg-white/10 border border-white/20 text-white text-sm flex items-center gap-2 transition-all hover:bg-white/15"
        >
          {isLoading ? (
            <>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              >
                <Sparkles className="w-4 h-4" />
              </motion.div>
              Processing...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Get Latest Analysis
            </>
          )}
        </motion.button>
      </div>

      {/* Analysis Text Display */}
      <motion.div
        key={analysisText}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="relative"
      >
        {isLoading && (
          <div className="absolute inset-0 backdrop-blur-sm bg-white/5 rounded-xl flex items-center justify-center z-10">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            >
              <Sparkles className="w-8 h-8 text-white" />
            </motion.div>
          </div>
        )}
        
        <div className="backdrop-blur-sm bg-black/20 border border-white/10 rounded-xl p-5 min-h-[400px] max-h-[500px] overflow-y-auto custom-scrollbar">
          {analysisText ? (
            <pre className="text-white/80 text-sm leading-relaxed whitespace-pre-wrap font-mono">
              {analysisText}
            </pre>
          ) : (
            <div className="flex flex-col items-center justify-center h-[400px] text-white/40">
              <FileText className="w-12 h-12 mb-3 opacity-50" />
              <p>No analysis data available</p>
              <p className="text-xs mt-2">Click "Get Latest Analysis" to fetch data</p>
            </div>
          )}
        </div>
      </motion.div>

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
