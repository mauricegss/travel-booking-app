import { Plane, Clock, MapPin } from "lucide-react";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface FlightCardProps {
  airline: string;
  departure: string;
  arrival: string;
  duration: string;
  price: string;
  stops: number;
  onSelect: () => void;
}

export const FlightCard = ({ airline, departure, arrival, duration, price, stops, onSelect }: FlightCardProps) => {
  return (
    <Card className="hover:shadow-lg transition-all duration-300">
      <CardContent className="pt-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Plane className="h-5 w-5 text-primary" />
            <span className="font-semibold text-foreground">{airline}</span>
          </div>
          <span className="text-2xl font-bold text-primary">{price}</span>
        </div>
        
        <div className="flex items-center justify-between mb-4">
          <div className="flex-1">
            <div className="text-sm text-muted-foreground mb-1">Saída</div>
            <div className="text-lg font-semibold text-foreground">{departure}</div>
          </div>
          
          <div className="flex-1 text-center px-4">
            <div className="text-sm text-muted-foreground mb-1">{stops === 0 ? "Direto" : `${stops} parada${stops > 1 ? 's' : ''}`}</div>
            <div className="flex items-center justify-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">{duration}</span>
            </div>
          </div>
          
          <div className="flex-1 text-right">
            <div className="text-sm text-muted-foreground mb-1">Chegada</div>
            <div className="text-lg font-semibold text-foreground">{arrival}</div>
          </div>
        </div>
      </CardContent>
      
      <CardFooter>
        <Button onClick={onSelect} className="w-full bg-primary hover:bg-primary/90 text-primary-foreground">
          Selecionar Voo
        </Button>
      </CardFooter>
    </Card>
  );
};
