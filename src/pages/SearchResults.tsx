import { useSearchParams, useNavigate } from "react-router-dom";
import { FlightCard } from "@/components/FlightCard";
import { HotelCard } from "@/components/HotelCard";
import { ActivityCard } from "@/components/ActivityCard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { ArrowLeft, ShoppingCart } from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

const SearchResults = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const destination = searchParams.get("destination");
  const checkIn = searchParams.get("checkin");
  const checkOut = searchParams.get("checkout");

  const [selectedFlight, setSelectedFlight] = useState<string | null>(null);
  const [selectedHotel, setSelectedHotel] = useState<string | null>(null);
  const [selectedActivities, setSelectedActivities] = useState<string[]>([]);

  // Mock data - em produção viria da API
  const flights = [
    { id: "1", airline: "LATAM", departure: "08:00", arrival: "14:30", duration: "11h 30m", price: "R$ 2.450", stops: 0 },
    { id: "2", airline: "Azul", departure: "10:45", arrival: "18:15", duration: "12h 30m", price: "R$ 2.180", stops: 1 },
    { id: "3", airline: "Gol", departure: "15:20", arrival: "22:45", duration: "12h 25m", price: "R$ 2.320", stops: 1 },
  ];

  const hotels = [
    { id: "1", name: "Hotel Le Marais", location: "Centro de Paris", rating: 5, price: "R$ 680", amenities: ["wifi", "breakfast"] },
    { id: "2", name: "Ibis Paris Opera", location: "Próximo à Ópera", rating: 4, price: "R$ 420", amenities: ["wifi"] },
    { id: "3", name: "Novotel Tour Eiffel", location: "Vista Torre Eiffel", rating: 4, price: "R$ 850", amenities: ["wifi", "breakfast"] },
  ];

  const activities = [
    { id: "1", title: "Tour pela Torre Eiffel", description: "Visita guiada com acesso prioritário", duration: "3h", price: "R$ 280", capacity: "Até 15 pessoas" },
    { id: "2", title: "Museu do Louvre", description: "Entrada e guia especializado", duration: "4h", price: "R$ 320", capacity: "Até 20 pessoas" },
    { id: "3", title: "Cruzeiro no Sena", description: "Passeio noturno com jantar", duration: "2h 30m", price: "R$ 450", capacity: "Até 50 pessoas" },
  ];

  const handleSelectFlight = (id: string) => {
    setSelectedFlight(id);
    toast({
      title: "Voo selecionado",
      description: "Voo adicionado à sua reserva",
    });
  };

  const handleSelectHotel = (id: string) => {
    setSelectedHotel(id);
    toast({
      title: "Hotel selecionado",
      description: "Hotel adicionado à sua reserva",
    });
  };

  const handleSelectActivity = (id: string) => {
    if (selectedActivities.includes(id)) {
      setSelectedActivities(selectedActivities.filter(a => a !== id));
      toast({
        title: "Atividade removida",
        description: "Atividade removida da sua reserva",
      });
    } else {
      setSelectedActivities([...selectedActivities, id]);
      toast({
        title: "Atividade adicionada",
        description: "Atividade adicionada à sua reserva",
      });
    }
  };

  const handleProceedToBooking = () => {
    if (!selectedFlight || !selectedHotel) {
      toast({
        title: "Seleção incompleta",
        description: "Por favor, selecione um voo e um hotel antes de continuar",
        variant: "destructive",
      });
      return;
    }
    navigate("/booking", {
      state: {
        destination,
        checkIn,
        checkOut,
        selectedFlight,
        selectedHotel,
        selectedActivities,
      },
    });
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => navigate("/")}>
              <ArrowLeft className="h-5 w-5 mr-2" />
              Voltar
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-foreground">Resultados para {destination}</h1>
              <p className="text-muted-foreground">
                {checkIn} até {checkOut}
              </p>
            </div>
          </div>
          <Button 
            onClick={handleProceedToBooking}
            size="lg"
            className="bg-secondary hover:bg-secondary/90 text-secondary-foreground"
          >
            <ShoppingCart className="h-5 w-5 mr-2" />
            Finalizar Reserva
          </Button>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="flights" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-8">
            <TabsTrigger value="flights">Voos {selectedFlight && "✓"}</TabsTrigger>
            <TabsTrigger value="hotels">Hotéis {selectedHotel && "✓"}</TabsTrigger>
            <TabsTrigger value="activities">Atividades ({selectedActivities.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="flights" className="space-y-4">
            {flights.map((flight) => (
              <FlightCard
                key={flight.id}
                {...flight}
                onSelect={() => handleSelectFlight(flight.id)}
              />
            ))}
          </TabsContent>

          <TabsContent value="hotels" className="space-y-4">
            {hotels.map((hotel) => (
              <HotelCard
                key={hotel.id}
                {...hotel}
                onSelect={() => handleSelectHotel(hotel.id)}
              />
            ))}
          </TabsContent>

          <TabsContent value="activities" className="space-y-4">
            {activities.map((activity) => (
              <ActivityCard
                key={activity.id}
                {...activity}
                onSelect={() => handleSelectActivity(activity.id)}
              />
            ))}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default SearchResults;
