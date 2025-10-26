import { Search, Calendar, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

export const SearchBar = () => {
  const navigate = useNavigate();
  const [destination, setDestination] = useState("");
  const [checkIn, setCheckIn] = useState("");
  const [checkOut, setCheckOut] = useState("");

  const handleSearch = () => {
    if (destination && checkIn && checkOut) {
      navigate(`/search-results?destination=${encodeURIComponent(destination)}&checkin=${checkIn}&checkout=${checkOut}`);
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto bg-white/10 backdrop-blur-sm rounded-2xl shadow-2xl p-6"> 
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="relative">
          <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input 
            placeholder="Destino" 
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            className="pl-10 h-12 bg-background border-border text-foreground placeholder:text-muted-foreground" 
          />
        </div>
        
        <div className="relative">
          <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input 
            type="date" 
            value={checkIn}
            onChange={(e) => setCheckIn(e.target.value)}
            placeholder="Check-in" 
            className="pl-10 h-12 bg-background border-border text-foreground placeholder:text-muted-foreground" 
            style={{ colorScheme: 'light' }}
          />
        </div>
        
        <div className="relative">
          <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input 
            type="date"
            value={checkOut}
            onChange={(e) => setCheckOut(e.target.value)}
            placeholder="Check-out" 
            className="pl-10 h-12 bg-background border-border text-foreground placeholder:text-muted-foreground"
            style={{ colorScheme: 'light' }}
          />
        </div>
        
        <Button 
          onClick={handleSearch}
          className="h-12 bg-primary hover:bg-primary/90 text-primary-foreground font-medium"
        >
          <Search className="mr-2 h-5 w-5" />
          Buscar
        </Button>
      </div>
    </div>
  );
};