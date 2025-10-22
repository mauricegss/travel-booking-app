import { LucideIcon } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface AgentCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
}

export const AgentCard = ({ icon: Icon, title, description }: AgentCardProps) => {
  return (
    <Card className="group hover:shadow-xl transition-all duration-300 border-border hover:border-primary/50 bg-card">
      <CardHeader>
        <div className="w-14 h-14 rounded-xl bg-accent flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
          <Icon className="h-7 w-7 text-accent-foreground" />
        </div>
        <CardTitle className="text-xl text-card-foreground">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <CardDescription className="text-muted-foreground leading-relaxed">
          {description}
        </CardDescription>
      </CardContent>
    </Card>
  );
};
