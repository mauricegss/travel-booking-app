import { MapPinned, Clock, Users } from "lucide-react";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils"; // Importa cn
import * as React from "react"; // Importa React

// Adiciona className? à interface
export interface ActivityCardProps {
  id: string; // Adiciona id para key
  title: string;
  description: string;
  duration: string;
  price: string;
  capacity: string;
  onSelect: () => void;
  className?: string; // Adiciona className opcional
}

// Adiciona className e ref
export const ActivityCard = React.forwardRef<HTMLDivElement, ActivityCardProps>(
  ({ title, description, duration, price, capacity, onSelect, className, ...props }, ref) => {
  return (
    // Aplica className ao Card e passa ref e props
    <Card ref={ref} className={cn("hover:shadow-lg transition-all duration-300", className)} {...props}>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <MapPinned className="h-5 w-5 text-primary" />
              <h3 className="font-semibold text-lg text-foreground">{title}</h3>
            </div>
            <p className="text-sm text-muted-foreground mb-4">{description}</p>

            <div className="flex gap-4 text-sm">
              <div className="flex items-center gap-1 text-muted-foreground">
                <Clock className="h-4 w-4" />
                <span>{duration}</span>
              </div>
              <div className="flex items-center gap-1 text-muted-foreground">
                <Users className="h-4 w-4" />
                <span>{capacity}</span>
              </div>
            </div>
          </div>
          <div className="text-right ml-4">
            <div className="text-2xl font-bold text-primary">{price}</div>
            <div className="text-sm text-muted-foreground">por pessoa</div>
          </div>
        </div>
      </CardContent>

      <CardFooter>
        <Button onClick={onSelect} className="w-full bg-primary hover:bg-primary/90 text-primary-foreground">
          Adicionar Atividade
        </Button>
      </CardFooter>
    </Card>
  );
});
ActivityCard.displayName = "ActivityCard"; // Adiciona displayName