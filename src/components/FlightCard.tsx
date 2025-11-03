import { Plane, Link } from "lucide-react"; // Trocamos Clock por Link
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import * as React from "react"; 

export interface FlightCardProps {
  id: string; // url
  airline: string; // source
  departure: string; // "N/A"
  arrival: string; // "N/A"
  duration: string; // title
  price: string; // "Verificar no site"
  stops: number; // 0
  onSelect: () => void;
  className?: string; 
}

export const FlightCard = React.forwardRef<HTMLDivElement, FlightCardProps>(
  ({ id, airline, duration, price, onSelect, className, ...props }, ref) => {
  
  // Função para abrir o link em nova aba
  const handleViewOffer = (e: React.MouseEvent) => {
    e.stopPropagation(); // Impede que o onSelect seja disparado
    window.open(id, "_blank", "noopener,noreferrer");
  };

  return (
    <Card 
      ref={ref} 
      className={cn("hover:shadow-lg transition-all duration-300 cursor-pointer", className)} 
      onClick={onSelect} // Permite selecionar o card clicando nele
      {...props}
    >
      <CardContent className="pt-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Plane className="h-5 w-5 text-primary" />
            <span className="font-semibold text-foreground">{airline}</span>
          </div>
          <span className="text-lg font-bold text-primary">{price}</span>
        </div>

        <div className="flex items-center justify-center text-center mb-4">
          <p className="text-sm text-muted-foreground">{duration}</p>
        </div>
      </CardContent>

      <CardFooter>
        <Button 
          onClick={handleViewOffer} // Botão agora abre o link
          className="w-full bg-primary hover:bg-primary/90 text-primary-foreground"
        >
          <Link className="h-4 w-4 mr-2" />
          Ver Oferta no Site
        </Button>
      </CardFooter>
    </Card>
  );
});
FlightCard.displayName = "FlightCard";