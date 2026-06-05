"use client";

import { SplineScene } from "@/components/ui/splite";
import { Spotlight } from "@/components/ui/spotlight";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";
 
export function SplineSceneBasic() {
  const containerRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(containerRef, { margin: "100px" });

  return (
    <div ref={containerRef} className="w-full h-full relative pointer-events-none">
      {isInView && (
        <div className="w-full h-full bg-transparent relative overflow-visible flex items-center justify-center">
          <Spotlight
            className="-top-40 left-0 md:left-60 md:-top-20"
            fill="rgba(168,85,247,0.15)"
          />
          
          <div className="flex h-full w-full relative z-10 pointer-events-none">
            <motion.div 
              className="flex-1 relative w-full h-full transform-gpu"
              animate={{ y: [0, -20, 0] }}
              transition={{
                repeat: Infinity,
                duration: 5,
                ease: "easeInOut"
              }}
            >
              <SplineScene 
                scene="https://prod.spline.design/kZDDjO5HuC9GJUM2/scene.splinecode"
                className="w-full h-full"
              />
            </motion.div>
          </div>
        </div>
      )}
    </div>
  );
}
