import { motion } from "framer-motion";
import { ArrowRight, Brain, Network, AlertTriangle, TrendingUp, Shield } from "lucide-react";

interface LandingPageProps {
  onExplore: () => void;
}

export function LandingPage({ onExplore }: LandingPageProps) {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-20">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="relative max-w-5xl w-full"
      >
        {/* Main glass card */}
        <div className="relative backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-12 md:p-16 shadow-2xl">
          {/* Animated border glow */}
          <motion.div
            className="absolute inset-0 rounded-3xl"
            animate={{
              boxShadow: [
                "0 0 20px rgba(255,255,255,0.1)",
                "0 0 60px rgba(255,255,255,0.2)",
                "0 0 20px rgba(255,255,255,0.1)",
              ],
            }}
            transition={{ duration: 4, repeat: Infinity }}
          />
          
          <div className="relative z-10">
            {/* Logo/Brand */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="flex items-center gap-3 mb-8"
            >
              <motion.div
                animate={{ 
                  rotate: [0, 360],
                }}
                transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                className="relative w-14 h-14 backdrop-blur-sm bg-white/10 border border-white/20 rounded-2xl flex items-center justify-center"
              >
                <Network className="w-7 h-7 text-white" />
                <motion.div
                  animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="absolute inset-0 rounded-2xl border-2 border-white/40"
                />
              </motion.div>
              <div>
                <h2 className="text-white">HIVEMIND</h2>
                <p className="text-white/50 text-sm">Neural Crypto Intelligence</p>
              </div>
            </motion.div>

            {/* Main Headline */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-white mb-6"
            >
              AI-Powered Anomaly Detection
              <br />
              <span className="text-white/60">for Cryptocurrency Markets</span>
            </motion.h1>

            {/* Description */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-white/70 mb-12 max-w-3xl text-lg"
            >
              Hivemind leverages advanced neural networks and machine learning algorithms 
              to identify market anomalies in real-time. Our multi-method approach analyzes 
              patterns, sentiment, and on-chain data to detect irregular behavior before it 
              impacts your portfolio.
            </motion.p>

            {/* Features Grid */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12"
            >
              {[
                { icon: Brain, label: "Neural Networks" },
                { icon: AlertTriangle, label: "Anomaly Detection" },
                { icon: TrendingUp, label: "Real-time Analysis" },
                { icon: Shield, label: "Risk Assessment" },
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.6 + index * 0.1 }}
                  whileHover={{ scale: 1.05, y: -5 }}
                  className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-xl p-4 text-center"
                >
                  <feature.icon className="w-6 h-6 text-white mx-auto mb-2" />
                  <p className="text-white/80 text-sm">{feature.label}</p>
                </motion.div>
              ))}
            </motion.div>

            {/* CTA Button */}
            <motion.button
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              onClick={onExplore}
              whileHover={{ scale: 1.05, backgroundColor: "rgba(255,255,255,0.15)" }}
              whileTap={{ scale: 0.95 }}
              className="group inline-flex items-center gap-3 px-10 py-5 rounded-full backdrop-blur-sm bg-white/10 border border-white/20 text-white transition-all"
            >
              <span className="text-lg">Explore Dashboard</span>
              <motion.div
                animate={{ x: [0, 5, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                <ArrowRight className="w-6 h-6" />
              </motion.div>
            </motion.button>
          </div>
        </div>

        {/* Floating accent elements */}
        <motion.div
          animate={{ 
            y: [0, -25, 0],
            rotate: [0, 10, 0]
          }}
          transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -top-10 -right-10 w-40 h-40 backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl"
        />
        <motion.div
          animate={{ 
            y: [0, 25, 0],
            rotate: [0, -10, 0]
          }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -bottom-8 -left-8 w-32 h-32 backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl"
        />
        
        {/* Neural network visualization */}
        <motion.div
          animate={{ 
            scale: [1, 1.1, 1],
            opacity: [0.3, 0.6, 0.3]
          }}
          transition={{ duration: 3, repeat: Infinity }}
          className="absolute top-1/2 right-0 w-64 h-64 -translate-y-1/2 translate-x-1/2"
        >
          {[...Array(3)].map((_, i) => (
            <motion.div
              key={i}
              animate={{ rotate: 360 }}
              transition={{ duration: 10 + i * 5, repeat: Infinity, ease: "linear" }}
              className="absolute inset-0 border border-white/10 rounded-full"
              style={{ transform: `scale(${1 - i * 0.3})` }}
            />
          ))}
        </motion.div>
      </motion.div>
    </div>
  );
}
