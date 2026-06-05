"use client";

import { motion } from "framer-motion";
import { CheckCircle2, XCircle, AlertCircle } from "lucide-react";

export function Features() {
  return (
    <section id="evaluations" className="pb-24 bg-white scroll-mt-20">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="mb-16">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">Classifier Training & Testing Results</h3>
          
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden"
          >
            <div className="px-6 py-4 border-b border-gray-100 bg-gray-50/50 flex justify-between items-center">
              <h4 className="text-sm font-semibold text-gray-700">Model Performance Metrics</h4>
              <span className="text-xs px-2.5 py-0.5 bg-purple-100 text-purple-800 font-semibold rounded-full">
                Mistral-7B-Instruct-v0.2 AIE
              </span>
            </div>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50/85">
                  <tr>
                    <th scope="col" className="px-6 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      Threat Category
                    </th>
                    <th scope="col" className="px-6 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      Train Accuracy
                    </th>
                    <th scope="col" className="px-6 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      Test Accuracy
                    </th>
                    <th scope="col" className="px-6 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      Test ROC-AUC
                    </th>
                    <th scope="col" className="px-6 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      F1-Score
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-100">
                  {[
                    { category: "Jailbreak (AutoDAN / GCG)", trainAcc: "98.45%", testAcc: "95.80%", rocAuc: "0.9616", f1: "0.957" },
                    { category: "Bias (BBQ QA Benchmark)", trainAcc: "96.39%", testAcc: "92.40%", rocAuc: "0.9622", f1: "0.924" },
                    { category: "Lies (WikiData / SciQ)", trainAcc: "94.27%", testAcc: "96.20%", rocAuc: "0.9688", f1: "0.961" },
                    { category: "Toxic (Social Chemistry)", trainAcc: "99.75%", testAcc: "94.10%", rocAuc: "0.9886", f1: "0.941" },
                    { category: "Backdoor (BadMagic Triggers)", trainAcc: "99.93%", testAcc: "95.00%", rocAuc: "1.0000", f1: "0.942" }
                  ].map((row, idx) => (
                    <tr key={idx} className="hover:bg-purple-50/20 transition-colors">
                      <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                        {row.category}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {row.trainAcc}
                      </td>
                      <td className="px-6 py-4 text-sm font-medium text-purple-700">
                        {row.testAcc}
                      </td>
                      <td className="px-6 py-4 text-sm text-indigo-600 font-mono">
                        {row.rocAuc}
                      </td>
                      <td className="px-6 py-4 text-sm text-green-700 font-medium">
                        {row.f1}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        </div>

        {/* Dashboard Analytics Preview */}
        <div id="performance-plots" className="scroll-mt-20">
           <h3 className="text-xl font-semibold text-gray-900 mb-10 text-center">Performance & Effectiveness</h3>
           
           <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="flex flex-col gap-10 max-w-4xl mx-auto"
           >
              {/* ROC-AUC Curves */}
              <div className="bg-white border border-gray-200 shadow-xl shadow-purple-900/5 rounded-2xl overflow-hidden p-6 md:p-8 flex flex-col gap-6">
                 <div>
                    <h4 className="text-lg font-bold text-gray-900 mb-2">ROC-AUC Curves</h4>
                    <p className="text-sm text-gray-500">Displays the True Positive Rate vs False Positive Rate (ROC) for all 5 threat models.</p>
                 </div>
                 <div className="relative aspect-[5/4] w-full bg-gray-50 rounded-xl overflow-hidden border border-gray-100 flex items-center justify-center">
                    <img src="/plots/roc_curves.png" alt="ROC-AUC Curves" className="w-full h-full object-contain hover:scale-[1.01] transition-transform duration-300" />
                 </div>
              </div>

              {/* Accuracy Comparison */}
              <div className="bg-white border border-gray-200 shadow-xl shadow-purple-900/5 rounded-2xl overflow-hidden p-6 md:p-8 flex flex-col gap-6">
                 <div>
                    <h4 className="text-lg font-bold text-gray-900 mb-2">Accuracy Performance</h4>
                    <p className="text-sm text-gray-500">Compares training vs testing classification accuracy percentage across all 5 detectors.</p>
                 </div>
                 <div className="relative aspect-[4/3] w-full bg-gray-50 rounded-xl overflow-hidden border border-gray-100 flex items-center justify-center">
                    <img src="/plots/accuracy_metrics.png" alt="Accuracy Comparison" className="w-full h-full object-contain hover:scale-[1.01] transition-transform duration-300" />
                 </div>
              </div>

              {/* Loss Comparison */}
              <div className="bg-white border border-gray-200 shadow-xl shadow-purple-900/5 rounded-2xl overflow-hidden p-6 md:p-8 flex flex-col gap-6">
                 <div>
                    <h4 className="text-lg font-bold text-gray-900 mb-2">Cross-Entropy Loss</h4>
                    <p className="text-sm text-gray-500">Displays the training and testing binary cross-entropy loss values for each category.</p>
                 </div>
                 <div className="relative aspect-[4/3] w-full bg-gray-50 rounded-xl overflow-hidden border border-gray-100 flex items-center justify-center">
                    <img src="/plots/loss_metrics.png" alt="Loss Comparison" className="w-full h-full object-contain hover:scale-[1.01] transition-transform duration-300" />
                 </div>
              </div>
           </motion.div>
        </div>

      </div>
    </section>
  );
}
