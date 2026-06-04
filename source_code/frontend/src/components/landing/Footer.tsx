import Link from "next/link";
import { ShieldCheck } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-white border-t border-gray-100 pt-16 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
          
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <ShieldCheck className="w-6 h-6 text-purple-600" />
              <span className="font-bold text-lg text-gray-900">LLMSCAN</span>
            </Link>
            <p className="text-sm text-gray-500 mb-6 max-w-xs">
              A novel method for "brain-scanning" LLMs using causality analysis to proactively detect misbehavior.
            </p>
          </div>

          <div>
            <h4 className="font-semibold text-gray-900 mb-4">Research</h4>
            <ul className="space-y-3">
              <li><Link href="#" className="text-sm text-gray-500 hover:text-purple-600 transition-colors">ArXiv Paper</Link></li>
              <li><Link href="#" className="text-sm text-gray-500 hover:text-purple-600 transition-colors">Causality Maps</Link></li>
              <li><Link href="#" className="text-sm text-gray-500 hover:text-purple-600 transition-colors">Ablation Studies</Link></li>
              <li><Link href="#" className="text-sm text-gray-500 hover:text-purple-600 transition-colors">Datasets</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-gray-900 mb-4">Misbehaviors</h4>
            <ul className="space-y-3">
              <li><Link href="#" className="text-sm text-gray-500 hover:text-purple-600 transition-colors">Lie Detection</Link></li>
              <li><Link href="#" className="text-sm text-gray-500 hover:text-purple-600 transition-colors">Jailbreak Detection</Link></li>
              <li><Link href="#" className="text-sm text-gray-500 hover:text-purple-600 transition-colors">Toxicity Detection</Link></li>
              <li><Link href="#" className="text-sm text-gray-500 hover:text-purple-600 transition-colors">Backdoor Detection</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-gray-900 mb-4">Code</h4>
            <ul className="space-y-3">
              <li><a href="https://github.com/zhangmengling/LLMScan" target="_blank" rel="noopener noreferrer" className="text-sm text-gray-500 hover:text-purple-600 transition-colors">GitHub Repository</a></li>
              <li><Link href="#" className="text-sm text-gray-500 hover:text-purple-600 transition-colors">PyPI Package</Link></li>
              <li><Link href="#" className="text-sm text-gray-500 hover:text-purple-600 transition-colors">Installation</Link></li>
              <li><Link href="#" className="text-sm text-gray-500 hover:text-purple-600 transition-colors">Documentation</Link></li>
            </ul>
          </div>

        </div>
        
        <div className="pt-8 border-t border-gray-100 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-gray-500">© {new Date().getFullYear()} LLM Scan. All rights reserved.</p>
          <div className="flex gap-4">
            <Link href="#" className="text-gray-400 hover:text-gray-600 transition-colors">Twitter</Link>
            <Link href="#" className="text-gray-400 hover:text-gray-600 transition-colors">GitHub</Link>
            <Link href="#" className="text-gray-400 hover:text-gray-600 transition-colors">Discord</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
