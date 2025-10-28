import { LucideIcon } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils"; // Importa cn
import * as React from "react"; // Importa React

// Adiciona className? e key/índice (opcional) à interface
interface AgentCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  className?: string; // Adiciona className opcional
}

// Adiciona className e ref
export const AgentCard = React.forwardRef<HTMLDivElement, AgentCardProps>(
  ({ icon: Icon, title, description, className, ...props }, ref) => {
  return (
    // Aplica className ao Card e passa ref e props
    <Card ref={ref} className={cn("group hover:shadow-xl transition-all duration-300 text-white bg-transparent border-none shadow-none", className)} {...props}>
      <CardHeader>
        <div className="w-14 h-14 rounded-xl bg-white/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
          <Icon className="h-7 w-7 text-white" />
        </div>
        <CardTitle className="text-xl text-white">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <CardDescription className="text-white/80 leading-relaxed">
          {description}
        </CardDescription>
      </CardContent>
    </Card>
  );
});
AgentCard.displayName = "AgentCard"; // Adiciona displayName