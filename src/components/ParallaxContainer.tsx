import { useState, useEffect, ReactNode } from "react";
import { motion } from "framer-motion";

interface ParallaxContainerProps {
  children: ReactNode;
  intensity?: number;
}

const ParallaxContainer = ({ children, intensity = 8 }: ParallaxContainerProps) => {
  const [rotateX, setRotateX] = useState(0);
  const [rotateY, setRotateY] = useState(0);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const centerX = window.innerWidth / 2;
      const centerY = window.innerHeight / 2;
      const x = (e.clientX - centerX) / centerX;
      const y = (e.clientY - centerY) / centerY;
      setRotateY(x * intensity);
      setRotateX(-y * intensity);
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [intensity]);

  return (
    <div style={{ perspective: "1200px" }} className="min-h-screen">
      <motion.div
        animate={{ rotateX, rotateY }}
        transition={{ type: "spring", stiffness: 100, damping: 30 }}
        style={{ transformStyle: "preserve-3d" }}
      >
        {children}
      </motion.div>
    </div>
  );
};

export default ParallaxContainer;
