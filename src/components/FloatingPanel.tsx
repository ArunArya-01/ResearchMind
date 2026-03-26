import { motion } from "framer-motion";
import { ReactNode } from "react";

interface FloatingPanelProps {
  children: ReactNode;
  z?: number;
  className?: string;
  dark?: boolean;
  delay?: number;
}

const FloatingPanel = ({ children, z = 50, className = "", dark = false, delay = 0 }: FloatingPanelProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{
        y: -6,
        scale: 1.005,
        boxShadow: "0 50px 120px -20px hsl(0 0% 0% / 0.9)",
        transition: { duration: 0.3 },
      }}
      className={`${dark ? "glass-dark" : "glass-panel"} ${className}`}
      style={{
        transform: `translateZ(${z}px)`,
        transformStyle: "preserve-3d",
      }}
    >
      {children}
    </motion.div>
  );
};

export default FloatingPanel;
