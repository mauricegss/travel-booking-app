import { Hotel, Star, MapPin, Wifi, Coffee } from "lucide-react";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface HotelCardProps {
  name: string;
  location: string;
  rating: number;
  price: string;
  amenities: string[];
  onSelect: () => void;
}

export const HotelCard = ({ name, location, rating, price, amenities, onSelect }: HotelCardProps) => {
  const amenityIcons: { [key: string]: any } = {
    wifi: Wifi,
    breakfast: Coffee,
  };

  return (
    <Card className="hover:shadow-lg transition-all duration-300">
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
            <div className="flex items-center gap-1">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`h-4 w-4 ${i < rating ? "fill-secondary text-secondary" : "text-muted"}`}
                />
              ))}
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-primary">{price}</div>
            <div className="text-sm text-muted-foreground">por noite</div>
          </div>
        </div>
        
        <div className="flex gap-3 mt-4">
          {amenities.map((amenity, index) => {
            const Icon = amenityIcons[amenity] || Wifi;
            return (
              <div key={index} className="flex items-center gap-1 text-sm text-muted-foreground">
                <Icon className="h-4 w-4" />
                <span className="capitalize">{amenity}</span>
              </div>
            );
          })}
        </div>
      </CardContent>
      
      <CardFooter>
        <Button onClick={onSelect} className="w-full bg-primary hover:bg-primary/90 text-primary-foreground">
          Selecionar Hotel
        </Button>
      </CardFooter>
    </Card>
  );
};
