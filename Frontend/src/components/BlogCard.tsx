import React from "react";
import { ChevronRight, Calendar, User, Tag } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

interface BlogCardProps {
  title: string;
  excerpt: string;
  date: string;
  author: string;
  category: string;
  readTime: string;
  onClick?: () => void;
}

const BlogCard = ({ title, excerpt, date, author, category, readTime, onClick }: BlogCardProps) => {
  return (
    <div 
      className="group bg-[#111116] border border-white/5 rounded-2xl p-6 transition-all duration-300 hover:border-green-500/30 hover:shadow-[0_0_30px_rgba(34,197,94,0.1)] cursor-pointer"
      onClick={onClick}
    >
      <div className="flex justify-between items-start mb-4">
        <Badge variant="secondary" className="bg-green-500/10 text-green-500 border-green-500/20 px-2 py-0.5 text-[10px] uppercase tracking-wider font-bold">
          {category}
        </Badge>
        <div className="flex items-center gap-2 text-[10px] text-gray-500 font-medium">
          <Calendar size={12} />
          {date}
        </div>
      </div>
      
      <h3 className="text-xl font-bold text-white mb-3 group-hover:text-green-400 transition-colors">
        {title}
      </h3>
      
      <p className="text-sm text-gray-400 leading-relaxed mb-6 line-clamp-2">
        {excerpt}
      </p>
      
      <div className="flex items-center justify-between pt-4 border-t border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center text-[10px] font-bold text-white border border-white/10">
            {author.charAt(0)}
          </div>
          <div>
            <p className="text-[11px] font-bold text-gray-300">{author}</p>
            <p className="text-[9px] text-gray-500 uppercase tracking-tighter">{readTime} Read</p>
          </div>
        </div>
        
        <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="sm" className="text-gray-400 group-hover:text-green-500 p-0 h-auto hover:bg-transparent">
                <span className="text-[11px] font-bold mr-1">READ MORE</span>
                <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="top">Open full article</TooltipContent>
          </Tooltip>
      </div>
    </div>
  );
};

export default BlogCard;
