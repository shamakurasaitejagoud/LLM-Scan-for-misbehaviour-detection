"use client";

import { SplineScene } from "@/components/ui/splite";
import { Card } from "@/components/ui/card"
import { Spotlight } from "@/components/ui/spotlight"
import { motion } from "framer-motion"
 
export function SplineSceneBasic() {
  return (
    <Card className="w-full h-full bg-transparent relative overflow-visible rounded-2xl border-none flex items-center justify-center">
      <Spotlight
        className="-top-40 left-0 md:left-60 md:-top-20"
        fill="rgba(168,85,247,0.15)"
      />
      
      <div className="flex h-full w-full relative z-10 pointer-events-auto">
        <motion.div 
          className="flex-1 relative w-full h-full drop-shadow-[0_20px_30px_rgba(168,85,247,0.4)]"
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
    </Card>
  )
}
