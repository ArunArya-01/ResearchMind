import { ReactNode } from "react";

interface FloatingPanelProps {
  children: ReactNode;
  z?: number;
  className?: string;
  dark?: boolean;
  delay?: number;
}

const FloatingPanel = ({ children, z = 50, className = "", dark = false }: FloatingPanelProps) => {
  return (
    <div
      className={`${dark ? "glass-dark" : "glass-panel"} ${className}`}
      style={{
        transform: `translateZ(${z}px)`,
        transformStyle: "preserve-3d",
      }}
    >
      {children}
    </div>
  );
};

export default FloatingPanel;
