import { motion } from "framer-motion";

export function FloatingShapes() {
  const shapes = [
    { size: 400, x: "10%", y: "20%", duration: 20 },
    { size: 300, x: "80%", y: "60%", duration: 25 },
    { size: 250, x: "60%", y: "10%", duration: 22 },
    { size: 350, x: "20%", y: "70%", duration: 18 },
    { size: 200, x: "90%", y: "30%", duration: 24 },
    { size: 280, x: "40%", y: "80%", duration: 21 },
  ];

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {shapes.map((shape, index) => (
        <motion.div
          key={index}
          className="absolute rounded-full"
          style={{
            width: shape.size,
            height: shape.size,
            left: shape.x,
            top: shape.y,
            background: "radial-gradient(circle, rgba(255,255,255,0.03) 0%, transparent 70%)",
            border: "1px solid rgba(255,255,255,0.05)",
          }}
          animate={{
            y: [0, -50, 0],
            x: [0, 30, 0],
            scale: [1, 1.1, 1],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: shape.duration,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}

      {/* Animated grid lines */}
      {[...Array(5)].map((_, i) => (
        <motion.div
          key={`h-line-${i}`}
          className="absolute left-0 right-0 h-px"
          style={{
            top: `${20 + i * 20}%`,
            background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent)",
          }}
          animate={{
            opacity: [0.2, 0.5, 0.2],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            delay: i * 0.2,
          }}
        />
      ))}

      {[...Array(5)].map((_, i) => (
        <motion.div
          key={`v-line-${i}`}
          className="absolute top-0 bottom-0 w-px"
          style={{
            left: `${20 + i * 20}%`,
            background: "linear-gradient(180deg, transparent, rgba(255,255,255,0.05), transparent)",
          }}
          animate={{
            opacity: [0.2, 0.5, 0.2],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            delay: i * 0.2,
          }}
        />
      ))}
    </div>
  );
}
