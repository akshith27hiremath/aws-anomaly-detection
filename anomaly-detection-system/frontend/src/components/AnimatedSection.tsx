import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import { ArrowUpRight, Box, Hexagon, Triangle } from "lucide-react";

export function AnimatedSection() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"],
  });

  const y = useTransform(scrollYProgress, [0, 1], [100, -100]);
  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.5, 1], [0.8, 1, 0.8]);

  return (
    <section ref={containerRef} className="relative px-4 py-32">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left side - Content */}
          <motion.div
            style={{ opacity }}
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-10">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2 }}
              >
                <h2 className="text-white mb-6">
                  Fluid Interactions
                  <br />
                  <span className="text-white/50">in Motion</span>
                </h2>
                <p className="text-white/70 mb-8">
                  Every interaction is carefully choreographed to create a seamless 
                  and delightful user experience. From subtle micro-interactions to 
                  grand animations, we've perfected the art of motion design.
                </p>

                <div className="space-y-4">
                  {[
                    "Scroll-based animations",
                    "Gesture-driven interactions",
                    "Smooth state transitions",
                  ].map((item, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: 0.3 + index * 0.1 }}
                      className="flex items-center gap-3"
                    >
                      <div className="w-1.5 h-1.5 rounded-full bg-white" />
                      <span className="text-white/80">{item}</span>
                    </motion.div>
                  ))}
                </div>

                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="mt-8 inline-flex items-center gap-2 px-6 py-3 rounded-full backdrop-blur-sm bg-white/10 border border-white/20 text-white"
                >
                  <span>Learn More</span>
                  <ArrowUpRight className="w-4 h-4" />
                </motion.button>
              </motion.div>
            </div>
          </motion.div>

          {/* Right side - Animated shapes */}
          <motion.div
            style={{ y, scale }}
            className="relative h-[500px]"
          >
            {/* Center glass panel */}
            <motion.div
              animate={{
                rotateY: [0, 10, 0, -10, 0],
              }}
              transition={{
                duration: 8,
                repeat: Infinity,
                ease: "easeInOut",
              }}
              className="absolute inset-0 backdrop-blur-2xl bg-white/5 border border-white/10 rounded-3xl"
              style={{ transformStyle: "preserve-3d" }}
            />

            {/* Floating geometric shapes */}
            <motion.div
              animate={{
                y: [0, -30, 0],
                rotate: [0, 360],
              }}
              transition={{
                duration: 6,
                repeat: Infinity,
                ease: "easeInOut",
              }}
              className="absolute top-10 left-10 w-20 h-20 backdrop-blur-sm bg-white/10 border border-white/20 rounded-2xl flex items-center justify-center"
            >
              <Box className="w-10 h-10 text-white" />
            </motion.div>

            <motion.div
              animate={{
                y: [0, 40, 0],
                rotate: [0, -180],
              }}
              transition={{
                duration: 7,
                repeat: Infinity,
                ease: "easeInOut",
              }}
              className="absolute top-32 right-16 w-24 h-24 backdrop-blur-sm bg-white/10 border border-white/20 rounded-3xl flex items-center justify-center"
            >
              <Hexagon className="w-12 h-12 text-white" />
            </motion.div>

            <motion.div
              animate={{
                y: [0, -25, 0],
                rotate: [0, 360],
              }}
              transition={{
                duration: 5,
                repeat: Infinity,
                ease: "easeInOut",
              }}
              className="absolute bottom-20 left-1/4 w-16 h-16 backdrop-blur-sm bg-white/10 border border-white/20 rounded-xl flex items-center justify-center"
            >
              <Triangle className="w-8 h-8 text-white" />
            </motion.div>

            <motion.div
              animate={{
                y: [0, 35, 0],
                x: [0, -20, 0],
                scale: [1, 1.1, 1],
              }}
              transition={{
                duration: 6.5,
                repeat: Infinity,
                ease: "easeInOut",
              }}
              className="absolute bottom-32 right-8 w-28 h-28 backdrop-blur-sm bg-white/10 border border-white/20 rounded-full"
            />

            {/* Orbiting elements */}
            <motion.div
              animate={{
                rotate: 360,
              }}
              transition={{
                duration: 15,
                repeat: Infinity,
                ease: "linear",
              }}
              className="absolute inset-0 flex items-center justify-center"
            >
              <div className="w-64 h-64 relative">
                <motion.div className="absolute top-0 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-white/80" />
                <motion.div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-white/60" />
                <motion.div className="absolute left-0 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-white/70" />
                <motion.div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-white/50" />
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
