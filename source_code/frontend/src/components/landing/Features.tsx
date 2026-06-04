"use client";

import { motion } from "framer-motion";
import { CheckCircle2, XCircle, AlertCircle } from "lucide-react";

export function Features() {
  return (
    <section className="pb-24 bg-white">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="mb-16">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">2. Detect Misbehaviors</h3>
          
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden"
          >
            <div className="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
              <h4 className="text-sm font-semibold text-gray-700">Supported Misbehavior Detections</h4>
            </div>
            
            <div className="divide-y divide-gray-100">
              {[
                { name: "Lie Detection (Truthful vs Untruthful)", status: "Supported", runOn: "Scanner", extra: "Average AUC > 0.98" },
                { name: "Jailbreak Detection (Adversarial Prompts)", status: "Supported", runOn: "Scanner", extra: "AutoDAN, GCG, PAP" },
                { name: "Toxicity Detection (SocialChem)", status: "Supported", runOn: "Scanner", extra: "Accurate context analysis" },
                { name: "Backdoor Detection (Trigger Attacks)", status: "Supported", runOn: "Scanner", extra: "Badnet, CTBA, MTBA, Sleeper" },
              ].map((test, i) => (
                <div key={i} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 hover:bg-gray-50 transition-colors gap-4">
                  <div className="flex items-center gap-3">
                    <div className="w-4 h-4 rounded bg-purple-100 flex items-center justify-center">
                      <div className="w-1.5 h-1.5 bg-purple-600 rounded-sm"></div>
                    </div>
                    <span className="text-sm text-gray-700 font-medium">{test.name}</span>
                  </div>
                  
                  <div className="flex items-center gap-6">
                    <div className="flex items-center gap-1.5 w-24">
                      {test.status === "Supported" ? (
                         <CheckCircle2 className="w-4 h-4 text-green-500" />
                      ) : (
                         <XCircle className="w-4 h-4 text-red-500" />
                      )}
                      <span className={`text-xs font-medium ${test.status === "Supported" ? "text-green-700" : "text-red-700"}`}>
                        {test.status}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-2 text-xs text-gray-500 w-24">
                       <AlertCircle className="w-3.5 h-3.5" />
                       {test.runOn}
                    </div>
                    
                    {test.extra && (
                      <div className="hidden md:flex items-center gap-2 text-xs text-gray-400 max-w-[200px] truncate">
                        <span className="px-2 py-0.5 bg-gray-100 rounded text-gray-600">{test.extra}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Dashboard Analytics Preview */}
        <div>
           <h3 className="text-xl font-semibold text-gray-900 mb-6 text-center">Performance & Effectiveness</h3>
           <p className="text-center text-gray-500 mb-10 text-sm max-w-lg mx-auto">Evaluated on state-of-the-art LLMs (Llama-3.1, Mistral, Llama-2). LLMSCAN achieves an average AUC of over 0.98 across 13 diverse datasets while remaining lightweight.</p>
           
           <motion.div 
            initial={{ opacity: 0, scale: 0.98 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="w-full h-auto bg-white border border-gray-200 shadow-xl shadow-purple-900/5 rounded-2xl overflow-hidden p-6"
           >
              {/* Fake Dashboard Header */}
              <div className="flex justify-between items-center mb-6">
                 <div className="flex gap-4">
                    <div className="h-2 w-24 bg-gray-200 rounded"></div>
                    <div className="h-2 w-16 bg-gray-200 rounded"></div>
                    <div className="h-2 w-32 bg-gray-200 rounded"></div>
                 </div>
                 <div className="h-6 w-20 bg-purple-100 rounded-md"></div>
              </div>

              {/* Fake Charts Grid */}
              <div className="grid md:grid-cols-3 gap-6">
                 {[...Array(6)].map((_, i) => {
                    const v1 = (i * 13 % 10) / 10;
                    const v2 = (i * 17 % 10) / 10;
                    const v3 = (i * 23 % 10) / 10;
                    const v4 = (i * 29 % 10) / 10;
                    
                    const startY = 50 + v1 * 30;
                    const qX = 25;
                    const qY = 20 + v2 * 40;
                    const qEndX = 50;
                    const qEndY = 40 + v3 * 20;
                    const tEndX = 100;
                    const tEndY = 30 + v4 * 40;
                    
                    const pathCurve = `M0,${startY} Q${qX},${qY} ${qEndX},${qEndY} T${tEndX},${tEndY}`;
                    const pathFill = `M0,100 L0,${startY} Q${qX},${qY} ${qEndX},${qEndY} T${tEndX},${tEndY} L100,100 Z`;

                    return (
                    <div key={i} className="border border-gray-100 rounded-xl p-4">
                       <div className="flex justify-between items-center mb-4">
                          <div className="h-3 w-32 bg-gray-200 rounded"></div>
                          <div className={`h-2 w-2 rounded-full ${i % 2 === 0 ? 'bg-red-400' : 'bg-green-400'}`}></div>
                       </div>
                       <div className="h-24 w-full bg-gradient-to-t from-purple-50 to-transparent flex items-end">
                          <svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 100">
                             <path d={pathFill} fill="rgba(168, 85, 247, 0.2)" />
                             <path d={pathCurve} fill="none" stroke="rgba(147, 51, 234, 0.8)" strokeWidth="2" />
                          </svg>
                       </div>
                    </div>
                 )})}
              </div>
           </motion.div>
        </div>

      </div>
    </section>
  );
}
