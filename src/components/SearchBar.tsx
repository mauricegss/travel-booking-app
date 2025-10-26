import { Search, Calendar, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export const SearchBar = () => {
  return (
    <div className="w-full max-w-5xl mx-auto bg-white/10 backdrop-blur-sm rounded-2xl shadow-2xl p-6 b"> 
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="relative">
          <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input 
            placeholder="Destino" 
            className="pl-10 h-12 bg-background border-border text-foreground placeholder:text-muted-foreground" 
          />
        </div>
        
        <div className="relative">
          <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input 
            type="date" 
            placeholder="Check-in" 
            className="pl-10 h-12 bg-background border-border text-foreground placeholder:text-muted-foreground" 
            style={{ colorScheme: 'light' }}
          />
        </div>
        
        <div className="relative">
          <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input 
            type="date" 
            placeholder="Check-out" 
            className="pl-10 h-12 bg-background border-border text-foreground placeholder:text-muted-foreground"
            style={{ colorScheme: 'light' }}
          />
        </div>
        
        <Button className="h-12 bg-primary hover:bg-primary/90 text-primary-foreground font-medium">
          <Search className="mr-2 h-5 w-5" />
          Buscar
        </Button>
      </div>
    </div>
  );
};