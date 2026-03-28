import React, { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { 
  LayoutDashboard, Activity, Database, BookOpen, Search, 
  ChevronRight, ArrowLeft, LogOut, Github, Cpu, ShieldCheck, 
  Zap, HelpCircle, Code2, Globe, SlidersHorizontal
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";
import BlogCard from "@/components/BlogCard";

const BLOG_POSTS = [
  {
    id: 1,
    title: "Sub-millisecond Arbitrage: GRU vs. Transformer-XL",
    excerpt: "In 2026, latency is the only moat. We compare the new Gated Recurrent Unit (GRU) cores against the Transformer-XL for predictive price discovery.",
    date: "March 28, 2026",
    author: "Ziad Ahmed",
    category: "Strategy",
    readTime: "9 min",
    icon: <Zap size={18} className="text-yellow-400" />,
    content: "The arbitrage landscape of 2026 is defined by micro-spreads and mega-liquidity. Our testing shows that while Transformer-XL models provide 14% higher directional accuracy over standard LSTMs, the inference latency of specialized GRU-v2 units (running locally on NVIDIA H200s) is significantly lower, allowing for execution within a 200-microsecond window. For most users, the GRU core remains the optimal balance of speed and precision in high-frequency cross-exchange pivots."
  },
  {
    id: 2,
    title: "Zero-Knowledge Vaults: The Future of API Security",
    excerpt: "Protecting your exchange credentials with ZK-proofs and multi-party computation. How the AI Arbitrage Bot secures your assets in a multi-tenant environment.",
    date: "March 24, 2026",
    author: "Sara Malik",
    category: "Developers",
    readTime: "12 min",
    icon: <ShieldCheck size={18} className="text-green-400" />,
    content: "Security in 2026 requires more than just encryption. Our 'Operator Vault' system utilizes a simplified Multi-Party Computation (MPC) protocol where API keys are never stored in their entirety on a single server. By fragmenting the secrets across three independent shards, we ensure that an attacker would need to compromise multiple environments simultaneously to reconstruct a single key. Furthermore, we've integrated ZK-proofs to verify exchange permissions without exposing the raw secret to the trading engine's logging layer."
  },
  {
    id: 3,
    title: "Navigating L3 Liquidity Mesh",
    excerpt: "As liquidity fragments across Layer 3 application chains, the bot now supports atomic route discovery across 14 independent sequencers.",
    date: "March 20, 2026",
    author: "Alex Chen",
    category: "Guides",
    readTime: "7 min",
    icon: <Globe size={18} className="text-blue-400" />,
    content: "The 'Liquidity Mesh' is the new reality. With the proliferation of L3s like Arbitrum Centauri and Optimism Hyperlane, traditional bridge arbitrage is dead. Instead, the focus has shifted to 'Sequencer Arbitrage'—capturing the delta between sequencer batches. Our bot's 'Hyper-Router' now monitors these L3 sequencers directly, bypassing standard RPC latency to execute trades before they are even visible on block explorers."
  },
  {
    id: 4,
    title: "MEV-Shield: Frontrunning Protection for Retail",
    excerpt: "Stop being the 'exit liquidity' for toxic MEV bots. Learn how our back-running protection and private RPC routing preserve your alpha.",
    date: "March 15, 2026",
    author: "Ziad Ahmed",
    category: "Strategy",
    readTime: "6 min",
    icon: <ShieldCheck size={18} className="text-purple-400" />,
    content: "Toxic MEV (Maximal Extractable Value) continues to be the primary drain on arbitrage returns. To combat this, the 2026 version of our bot routes all on-chain legs through private mempools (like Flashbots-V3 and Eden-X). This ensures your trade is bundled directly with a block builder, neutralizing the threat of sandwich attacks and frontrunning. We've also implemented 'Back-run Alpha' logic that specifically looks for heavy DEX swaps to immediately arbitrage the resulting slippage."
  },
  {
    id: 5,
    title: "Optimizing Bot Parameters: Threshold vs. Slippage",
    excerpt: "A practical guide to setting your profit thresholds, managing gas spikes, and tuning the AI confidence filters for maximum ROI.",
    date: "March 10, 2026",
    author: "Sara Malik",
    category: "Guides",
    readTime: "10 min",
    icon: <SlidersHorizontal size={18} className="text-orange-400" />,
    content: "Tuning your bot is an art. While a 0.05% threshold might seem low, with our new 'Dynamic Gas' module, it can be highly profitable during low-congestion periods. We recommend using a 'Confidence Filter' of 0.85 for the GRU model—this ensures the AI is 85% certain of a spread's persistence before initiating the execution sequence. For developers, the `params.json` file now allows for per-exchange latency padding to account for ISP-level variance."
  }
];

const FAQS = [
  {
    id: "fq-1",
    q: "Why does the bot show a spread but not execute?",
    a: "This is usually due to the 'AI Confidence Filter'. If the predicted persistence of the spread is shorter than the average execution latency (currently ~340ms), the bot will skip the trade to avoid 'chasing' ghost liquidity."
  },
  {
    id: "fq-2",
    q: "How are the exchange API keys actually stored?",
    a: "Keys are fragmented into three shards using an MPC approach. One shard is stored in the local encrypted database, one is in the 'Operator Vault', and the third is generated via a user-derived salt. No single location contains the full key."
  },
  {
    id: "fq-3",
    q: "Can this bot handle CEX to DEX arbitrage?",
    a: "Yes. Integration for major DEXs (Uniswap V4, PancakeL3) is included. However, on-chain execution requires a bonded ETH/Solana balance for gas and MEV-protection bundling."
  },
  {
    id: "fq-4",
    q: "What is the 'MEV-Shield' and can it be disabled?",
    a: "MEV-Shield routes transactions through private RPCs to prevent frontrunning. It can be disabled in Settings for faster (but riskier) public mempool execution, though we advise against it."
  }
];

const Blog = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [readingPost, setReadingPost] = useState<any>(null);

  const filteredPosts = useMemo(() => {
    const search = searchQuery.toLowerCase().trim();
    return BLOG_POSTS.filter(post => {
      const matchesSearch = !search || 
                            post.title.toLowerCase().includes(search) || 
                            post.excerpt.toLowerCase().includes(search) ||
                            post.content.toLowerCase().includes(search) ||
                            post.author.toLowerCase().includes(search);
      const matchesCategory = selectedCategory === "all" || post.category.toLowerCase() === selectedCategory.toLowerCase();
      return matchesSearch && matchesCategory;
    });
  }, [searchQuery, selectedCategory]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login', { replace: true });
  };

  return (
    <div className="flex h-screen w-full bg-[#050505] text-gray-200 overflow-hidden font-sans selection:bg-green-500/30">
      
      {/* SIDEBAR */}
      <aside className="w-20 border-r border-white/5 bg-[#0a0a0c] flex flex-col items-center py-6 gap-8 z-10 transition-all">
          <div 
            onClick={() => navigate("/")}
            className="w-10 h-10 bg-gradient-to-br from-green-400 to-green-600 rounded-xl flex items-center justify-center font-black text-xl text-black shadow-[0_0_20px_rgba(34,197,94,0.3)] hover:scale-105 transition-transform cursor-pointer"
          >
            A
          </div>
          <nav className="flex flex-col gap-6 text-gray-600">
            <Tooltip>
              <TooltipTrigger asChild>
                <button onClick={() => navigate("/")} className="p-3 hover:text-gray-300 transition-colors"><LayoutDashboard size={20} /></button>
              </TooltipTrigger>
              <TooltipContent side="right">Back to Dashboard</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <button className="p-3 hover:text-gray-300 transition-colors"><Activity size={20} /></button>
              </TooltipTrigger>
              <TooltipContent side="right">System Activity</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <button className="p-3 hover:text-gray-300 transition-colors"><Database size={20} /></button>
              </TooltipTrigger>
              <TooltipContent side="right">Exchange Vaults</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <button className="p-3 text-green-500 bg-green-500/10 rounded-xl"><BookOpen size={20} /></button>
              </TooltipTrigger>
              <TooltipContent side="right">Knowledge Base (Current)</TooltipContent>
            </Tooltip>
          </nav>
        </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 overflow-hidden flex flex-col relative">
        <div className="absolute top-0 left-0 bg-red-500 text-white z-[100] p-2 text-xs">BLOG RENDERED</div>
        
        {/* TOP BAR / NAVIGATION */}
        <header className="px-8 py-5 border-b border-white/5 bg-[#0a0a0c]/80 backdrop-blur-md flex justify-between items-center z-20">
          <div className="flex items-center gap-4">
            {readingPost ? (
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setReadingPost(null)}
                className="text-gray-400 hover:text-white flex items-center gap-2"
              >
                <ArrowLeft size={16} /> Back to Hub
              </Button>
            ) : (
              <h1 className="text-xl font-black text-white flex items-center gap-2">
                <BookOpen size={22} className="text-green-500" />
                Knowledge Base
              </h1>
            )}
          </div>
          
          <div className="flex items-center gap-4">
            <div className="relative group hidden md:block">
              <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="relative">
                      <Search size={16} className={`absolute left-3 top-1/2 -translate-y-1/2 transition-colors ${searchQuery ? 'text-green-500' : 'text-gray-500'}`} />
                      <Input 
                        placeholder="Search topics (e.g. MEV, AI, ZK)..." 
                        className="w-72 h-10 bg-white/5 border-white/10 rounded-xl pl-10 text-sm focus-visible:ring-green-500/30"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                      />
                    </div>
                  </TooltipTrigger>
                  <TooltipContent side="bottom">Filter insights by keyword or author</TooltipContent>
                </Tooltip>
                
                {searchQuery && (
                  <button 
                    onClick={() => setSearchQuery("")}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
                  >
                    <ArrowLeft size={14} className="rotate-45" />
                  </button>
                )}
              </div>

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button onClick={handleLogout} variant="destructive" size="sm" className="bg-red-500/10 text-red-500 hover:bg-red-500/20 border-red-500/20 transition-all">
                    <LogOut size={16} className="mr-2" /> Logout
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="bottom">Exit session</TooltipContent>
              </Tooltip>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto">
          <div className="p-8 max-w-6xl mx-auto space-y-12 pb-20">
            
            {readingPost ? (
              /* SINGLE POST VIEW */
              <article className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-8">
                <header className="space-y-6">
                  <div className="flex items-center gap-4">
                    <Badge className="bg-green-500/10 text-green-500 border-green-500/20">
                      {readingPost.category}
                    </Badge>
                    <span className="text-xs text-gray-500 font-mono">{readingPost.date}</span>
                  </div>
                  <h2 className="text-4xl md:text-5xl font-black text-white leading-tight">
                    {readingPost.title}
                  </h2>
                  <div className="flex items-center gap-4 py-2">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-green-500 to-green-700 flex items-center justify-center font-bold text-black border-2 border-white/10">
                      {readingPost.author.charAt(0)}
                    </div>
                    <div>
                      <p className="text-sm font-bold text-white">{readingPost.author}</p>
                      <p className="text-xs text-gray-500">System Architect & Strategy Lead</p>
                    </div>
                  </div>
                </header>
                
                <div className="aspect-video w-full bg-[#111116] rounded-3xl border border-white/5 flex items-center justify-center relative overflow-hidden group">
                   <div className="absolute inset-0 bg-gradient-to-t from-[#050505] to-transparent opacity-60"></div>
                   <div className="relative z-10 flex flex-col items-center gap-4">
                      {readingPost.icon}
                      <p className="text-[10px] uppercase tracking-[0.4em] text-gray-500 font-black">Analytical Visual Intelligence Layer</p>
                   </div>
                   <div className="absolute -bottom-10 -right-10 w-64 h-64 bg-green-500/5 blur-[80px] group-hover:bg-green-500/10 transition-all duration-700"></div>
                </div>

                <div className="prose prose-invert max-w-none">
                  <p className="text-lg text-gray-300 leading-relaxed font-light first-letter:text-5xl first-letter:font-black first-letter:mr-3 first-letter:float-left first-letter:text-green-500">
                    {readingPost.content}
                  </p>
                  <p className="text-lg text-gray-300 leading-relaxed font-light mt-6">
                    As we look toward the next iteration of the Arbitrage Bot, our commitment to sub-millisecond precision remains unwavering. The integration of zero-knowledge proofs and Layer 3 liquidity meshes is just the beginning. By prioritizing user security and execution alpha, we are building a tool that doesn't just play the market but anticipates it.
                  </p>
                </div>

                <div className="p-8 bg-[#111116] rounded-3xl border border-white/5 space-y-4">
                  <h4 className="flex items-center gap-2 text-sm font-bold text-white uppercase tracking-widest">
                    <Cpu size={16} className="text-green-500" /> Strategy Insight Core
                  </h4>
                  <p className="text-xs text-gray-400 font-mono leading-relaxed bg-[#050505] p-4 rounded-xl border border-white/5">
                    // Real-world Arbitrage Optimization <br/>
                    const executionMetric = Math.abs(spread_discovery - execution_timestamp); <br/>
                    const alphaDecay = (1 - (executionMetric / maxLatencyAllowed)); <br/>
                    return tradeOpportunity * alphaDecay;
                  </p>
                </div>
              </article>
            ) : (
              /* BLOG LISTING VIEW */
              <>
                <section className="space-y-6">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div>
                      <h2 className="text-3xl font-black text-white mb-2 tracking-tight">System Insights</h2>
                      <p className="text-sm text-gray-500">Real-world guides and technical directives for 2026 operations.</p>
                    </div>
                    
                    <Tabs defaultValue="all" value={selectedCategory} onValueChange={setSelectedCategory} className="w-full md:w-auto">
                      <TabsList className="bg-white/5 border border-white/10 p-1 rounded-xl">
                        <TabsTrigger value="all" className="rounded-lg px-4 py-2 text-xs font-bold data-[state=active]:bg-green-500 data-[state=active]:text-black transition-all">All Resources</TabsTrigger>
                        <TabsTrigger value="guides" className="rounded-lg px-4 py-2 text-xs font-bold data-[state=active]:bg-green-500 data-[state=active]:text-black transition-all">User Guides</TabsTrigger>
                        <TabsTrigger value="developers" className="rounded-lg px-4 py-2 text-xs font-bold data-[state=active]:bg-green-500 data-[state=active]:text-black transition-all">Dev Stack</TabsTrigger>
                        <TabsTrigger value="strategy" className="rounded-lg px-4 py-2 text-xs font-bold data-[state=active]:bg-green-500 data-[state=active]:text-black transition-all">AI Strategy</TabsTrigger>
                      </TabsList>
                    </Tabs>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in duration-700">
                    {filteredPosts.length > 0 ? (
                      filteredPosts.map(post => (
                        <BlogCard 
                          key={post.id}
                          {...post}
                          onClick={() => setReadingPost(post)}
                        />
                      ))
                    ) : (
                      <div className="col-span-full py-24 text-center border-2 border-dashed border-white/5 rounded-[2rem] bg-white/[0.02]">
                        <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-6 text-gray-600">
                           <Search size={32} />
                        </div>
                        <h3 className="text-xl font-bold text-white mb-2">Alpha Not Found</h3>
                        <p className="text-gray-500 text-sm max-w-sm mx-auto">
                          We couldn't find any resources for "<span className="text-green-500 font-mono">{searchQuery}</span>". Try searching for 'MEV', 'GRU', or 'Vault'.
                        </p>
                        <Button 
                          variant="ghost" 
                          onClick={() => setSearchQuery("")}
                          className="mt-6 text-green-500 hover:text-green-400"
                        >
                          Clear Search
                        </Button>
                      </div>
                    )}
                  </div>
                </section>

                <section className="pt-12 space-y-8">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-purple-500/10 rounded-xl text-purple-500"><HelpCircle size={24} /></div>
                    <div>
                      <h2 className="text-2xl font-black text-white tracking-tight">Executive Queries & FAQs</h2>
                      <p className="text-sm text-gray-500">Operational intelligence for high-frequency environments.</p>
                    </div>
                  </div>

                  <Accordion type="single" collapsible className="w-full space-y-4">
                    {FAQS.map(faq => (
                      <AccordionItem key={faq.id} value={faq.id} className="border border-white/5 bg-[#111116] rounded-2xl overflow-hidden px-6 transition-all hover:border-purple-500/20">
                        <AccordionTrigger className="hover:no-underline text-sm font-bold text-gray-200 py-5 text-left">
                          {faq.q}
                        </AccordionTrigger>
                        <AccordionContent className="text-sm text-gray-400 leading-relaxed pb-5 pt-0">
                          {faq.a}
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                </section>

                {/* DEVELOPER ECOSYSTEM CTA */}
                <section className="bg-gradient-to-br from-[#111116] to-[#050505] border border-green-500/10 rounded-[2.5rem] p-10 flex flex-col md:flex-row items-center justify-between gap-10 relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-64 h-64 bg-green-500/5 blur-[100px]"></div>
                  <div className="space-y-4 relative z-10 max-w-xl">
                    <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-500/10 text-green-500 text-[10px] font-black uppercase tracking-widest rounded-full border border-green-500/20">
                      Open Source Core
                    </div>
                    <h2 className="text-4xl font-black text-white leading-tight">Contribution & Extension</h2>
                    <p className="text-gray-400 text-sm leading-relaxed">
                      Wany to extend the bot logic or build your own strategy module? Our ecosystem supports third-party integrations via the standardized Execution Interface.
                    </p>
                    <div className="flex gap-4 pt-2">
                       <Button className="bg-green-500 hover:bg-green-400 text-black font-black px-6 h-12 rounded-xl flex items-center gap-2">
                         <Github size={18} /> GITHUB REPO
                       </Button>
                       <Button variant="ghost" className="text-gray-400 hover:text-white font-bold px-6 h-12 rounded-xl border border-white/10">
                         VIEW SPEC
                       </Button>
                    </div>
                  </div>
                  <div className="relative z-10 hidden lg:block">
                     <div className="w-64 h-64 bg-green-500/10 rounded-full flex items-center justify-center border border-white/5 animate-pulse">
                        <Code2 size={80} className="text-green-500/40" />
                     </div>
                  </div>
                </section>
              </>
            )}

          </div>
        </div>
      </main>
    </div>
  );
};

export default Blog;
