import { motion } from "framer-motion";
import { Zap, Layers, Sparkles, Circle } from "lucide-react";

const cards = [
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Experience blazing fast performance with optimized animations and smooth transitions.",
  },
  {
    icon: Layers,
    title: "Layered Design",
    description: "Multi-dimensional interfaces that create depth and visual hierarchy through glass effects.",
  },
  {
    icon: Sparkles,
    title: "Pure Elegance",
    description: "Minimalist aesthetics combined with sophisticated glassmorphism for a premium feel.",
  },
];

export function GlassCards() {
  return (
    <section className="relative px-4 py-20">
      <div className="max-w-7xl mx-auto">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full backdrop-blur-sm bg-white/5 border border-white/10 mb-6">
            <Circle className="w-3 h-3 text-white fill-white" />
            <span className="text-white/80 text-sm">Features</span>
          </div>
          <h2 className="text-white mb-4">
            Designed for Excellence
          </h2>
          <p className="text-white/60 max-w-2xl mx-auto">
            Every element crafted with precision and attention to detail
          </p>
        </motion.div>

        {/* Cards grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {cards.map((card, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{ y: -10, scale: 1.02 }}
              className="group relative"
            >
              {/* Card */}
              <div className="relative h-full backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 overflow-hidden">
                {/* Hover effect */}
                <motion.div
                  className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                />

                <div className="relative z-10">
                  {/* Icon container */}
                  <motion.div
                    animate={{
                      rotate: [0, 5, 0, -5, 0],
                    }}
                    transition={{
                      duration: 5,
                      repeat: Infinity,
                      ease: "easeInOut",
                    }}
                    className="inline-flex items-center justify-center w-14 h-14 rounded-2xl backdrop-blur-sm bg-white/10 border border-white/20 mb-6"
                  >
                    <card.icon className="w-7 h-7 text-white" />
                  </motion.div>

                  {/* Content */}
                  <h3 className="text-white mb-3">
                    {card.title}
                  </h3>
                  <p className="text-white/60">
                    {card.description}
                  </p>
                </div>

                {/* Animated corner accent */}
                <motion.div
                  animate={{
                    scale: [1, 1.2, 1],
                    opacity: [0.3, 0.6, 0.3],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                  className="absolute -bottom-8 -right-8 w-32 h-32 rounded-full bg-white/5 blur-2xl"
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
