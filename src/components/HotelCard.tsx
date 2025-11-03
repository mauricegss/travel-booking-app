import { Hotel, MapPin, Wifi, FileText, Link } from "lucide-react"; // Trocamos ícones
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils"; 
import * as React from "react"; 

export interface HotelCardProps {
  id: string; // url
  name: string; // title
  location: string; // source
  rating: number; // 0
  price: string; // "Verificar no site"
  amenities: string[]; // [description]
  onSelect: () => void;
  className?: string; 
}

export const HotelCard = React.forwardRef<HTMLDivElement, HotelCardProps>(
  ({ id, name, location, price, amenities, onSelect, className, ...props }, ref) => {
  
  // Função para abrir o link em nova aba
  const handleViewOffer = (e: React.MouseEvent) => {
    e.stopPropagation(); 
    window.open(id, "_blank", "noopener,noreferrer");
  };

  const description = amenities && amenities.length > 0 ? amenities[0] : "Sem descrição.";

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
              <Hotel className="h-5 w-5 text-primary" />
              <h3 className="font-semibold text-lg text-foreground">{name}</h3>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
              <MapPin className="h-4 w-4" />
              <span>{location}</span>
            </div>
            {/* Removemos as estrelas (rating) pois não temos esse dado */}
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-primary">{price}</div>
            <div className="text-sm text-muted-foreground">por noite</div>
          </div>
        </div>

        {/* Usamos o campo de amenities para mostrar o snippet da busca */}
        <div className="flex gap-3 mt-4">
          <div className="flex items-start gap-2 text-sm text-muted-foreground">
            <FileText className="h-4 w-4 mt-1 shrink-0" />
            <span className="line-clamp-3">{description}</span>
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
HotelCard.displayName = "HotelCard";