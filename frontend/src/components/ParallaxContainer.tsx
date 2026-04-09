import { ReactNode } from "react";

interface ParallaxContainerProps {
  children: ReactNode;
  intensity?: number;
}

const ParallaxContainer = ({ children }: ParallaxContainerProps) => {
  return (
    <div className="min-h-screen">
      {children}
    </div>
  );
};

export default ParallaxContainer;
