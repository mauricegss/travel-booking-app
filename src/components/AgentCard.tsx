import { LucideIcon } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface AgentCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
}

export const AgentCard = ({ icon: Icon, title, description }: AgentCardProps) => {
  return (
    // Removido bg-card, border-border, hover:border-primary/50. Adicionado text-white. Removido shadow padrão.
    <Card className="group hover:shadow-xl transition-all duration-300 text-white bg-transparent border-none shadow-none"> 
      <CardHeader>
        {/* Fundo do ícone ajustado para melhor contraste */}
        <div className="w-14 h-14 rounded-xl bg-white/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
          {/* Cor do ícone ajustada */}
          <Icon className="h-7 w-7 text-white" /> 
        </div>
        {/* Cor do título ajustada */}
        <CardTitle className="text-xl text-white">{title}</CardTitle> 
      </CardHeader>
      <CardContent>
        {/* Cor da descrição ajustada */}
        <CardDescription className="text-white/80 leading-relaxed"> 
          {description}
        </CardDescription>
      </CardContent>
    </Card>
  );
};