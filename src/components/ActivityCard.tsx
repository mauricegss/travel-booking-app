import { MapPinned, Users, Link } from "lucide-react"; // Trocamos Clock por Link
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils"; 
import * as React from "react"; 

export interface ActivityCardProps {
  id: string; // url
  title: string;
  description: string;
  duration: string; // "N/A"
  price: string; // "Verificar no site"
  capacity: string; // source
  onSelect: () => void;
  className?: string; 
}

export const ActivityCard = React.forwardRef<HTMLDivElement, ActivityCardProps>(
  ({ id, title, description, price, capacity, onSelect, className, ...props }, ref) => {
  
  // Função para abrir o link em nova aba
  const handleViewOffer = (e: React.MouseEvent) => {
    e.stopPropagation(); 
    window.open(id, "_blank", "noopener,noreferrer");
  };

  return (
    <Card 
      ref={ref} 
      className={cn("hover:shadow-lg transition-all duration-300 cursor-pointer", className)} 
      onClick={onSelect}
      {...props}
    >
      <CardContent className="pt-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <MapPinned className="h-5 w-5 text-primary" />
              <h3 className="font-semibold text-lg text-foreground">{title}</h3>
            </div>
            <p className="text-sm text-muted-foreground mb-4 line-clamp-3">{description}</p>

            <div className="flex gap-4 text-sm">
              <div className="flex items-center gap-1 text-muted-foreground">
                <Users className="h-4 w-4" />
                <span>Fonte: {capacity}</span>
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
        <Button 
          onClick={handleViewOffer} 
          className="w-full bg-primary hover:bg-primary/90 text-primary-foreground"
        >
          <Link className="h-4 w-4 mr-2" />
          Ver Oferta no Site
        </Button>
      </CardFooter>
    </Card>
  );
});
ActivityCard.displayName = "ActivityCard";