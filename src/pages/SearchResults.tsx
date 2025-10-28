import { useSearchParams, useNavigate, useLocation } from "react-router-dom";
import { FlightCard } from "@/components/FlightCard";
import { HotelCard } from "@/components/HotelCard";
import { ActivityCard } from "@/components/ActivityCard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { AlertCircle, ArrowLeft, Loader2, ShoppingCart } from "lucide-react";
import { useEffect, useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { TripDataResponse } from "@/services/api"; // Importa a interface
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";


const SearchResults = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const destination = searchParams.get("destination");
  const checkIn = searchParams.get("checkin");
  const checkOut = searchParams.get("checkout");

  const [apiResponse, setApiResponse] = useState<TripDataResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const [selectedFlight, setSelectedFlight] = useState<string | null>(null);
  const [selectedHotel, setSelectedHotel] = useState<string | null>(null);
  const [selectedActivities, setSelectedActivities] = useState<string[]>([]);

  useEffect(() => {
    if (location.state?.apiResponse) {
      setApiResponse(location.state.apiResponse);
    }
    setIsLoading(false); // Sempre para de carregar, mesmo se não houver apiResponse
  }, [location.state]);

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
        destination: apiResponse?.destination ?? destination, // Usa o destino da API se disponível
        checkIn: apiResponse?.start_date ?? checkIn,
        checkOut: apiResponse?.end_date ?? checkOut,
        selectedFlight,
        selectedHotel,
        selectedActivities,
        // Passa os detalhes dos itens selecionados (opcional, mas útil)
        flightDetails: apiResponse?.flights?.find(f => f.id === selectedFlight),
        hotelDetails: apiResponse?.hotels?.find(h => h.id === selectedHotel),
        activityDetails: apiResponse?.activities?.filter(a => selectedActivities.includes(a.id)),
      },
    });
  };

  // ----- Renderização -----

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-background">
        <Loader2 className="h-16 w-16 animate-spin text-primary" />
      </div>
    );
  }

  if (!apiResponse) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
         <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Erro na Busca</AlertTitle>
            <AlertDescription>
                Não foi possível carregar os resultados. Por favor, tente novamente.
            </AlertDescription>
         </Alert>
         <Button variant="outline" onClick={() => navigate("/")} className="mt-4">
              <ArrowLeft className="h-5 w-5 mr-2" />
              Voltar
         </Button>
      </div>
    );
  }

  // Se houve erro na extração, mostra o erro do itinerário e um botão de voltar
  if (apiResponse.error && (!apiResponse.flights || apiResponse.flights.length === 0)) {
     return (
       <div className="container mx-auto px-4 py-8">
            <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Erro no Planejamento</AlertTitle>
                <AlertDescription>
                    {apiResponse.itinerary || apiResponse.error}
                </AlertDescription>
            </Alert>
             <Button variant="outline" onClick={() => navigate("/")} className="mt-4">
                <ArrowLeft className="h-5 w-5 mr-2" />
                Voltar
            </Button>
       </div>
     );
  }


  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => navigate(-1)}>
              <ArrowLeft className="h-5 w-5 mr-2" />
              Voltar
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-foreground">Resultados para {apiResponse.destination ?? destination}</h1>
              <p className="text-muted-foreground">
                {apiResponse.start_date ?? checkIn} até {apiResponse.end_date ?? checkOut}
              </p>
            </div>
          </div>
          <Button
            onClick={handleProceedToBooking}
            size="lg"
            className="bg-secondary hover:bg-secondary/90 text-secondary-foreground"
            disabled={!selectedFlight || !selectedHotel}
          >
            <ShoppingCart className="h-5 w-5 mr-2" />
            Finalizar Reserva
          </Button>
        </div>

        {/* Mostra o itinerário textual gerado (opcional) */}
        {/* <Card className="mb-8">
            <CardHeader><CardTitle>Resumo do Itinerário</CardTitle></CardHeader>
            <CardContent><pre className="whitespace-pre-wrap text-left text-sm">{apiResponse.itinerary}</pre></CardContent>
        </Card> */}


        <Tabs defaultValue="flights" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-8">
            <TabsTrigger value="flights">Voos {selectedFlight && "✓"}</TabsTrigger>
            <TabsTrigger value="hotels">Hotéis {selectedHotel && "✓"}</TabsTrigger>
            <TabsTrigger value="activities">Atividades ({selectedActivities.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="flights" className="space-y-4">
            {(apiResponse.flights && apiResponse.flights.length > 0) ? (
                apiResponse.flights.map((flight) => (
                <FlightCard
                    key={flight.id}
                    {...flight}
                    onSelect={() => handleSelectFlight(flight.id)}
                    // Adiciona estilo para indicar seleção (opcional)
                    className={selectedFlight === flight.id ? "border-primary ring-2 ring-primary" : ""}
                />
                ))
            ) : (
                <p className="text-muted-foreground text-center py-4">Nenhum voo encontrado.</p>
            )}
          </TabsContent>

          <TabsContent value="hotels" className="space-y-4">
             {(apiResponse.hotels && apiResponse.hotels.length > 0) ? (
                apiResponse.hotels.map((hotel) => (
                <HotelCard
                    key={hotel.id}
                    {...hotel}
                    onSelect={() => handleSelectHotel(hotel.id)}
                    className={selectedHotel === hotel.id ? "border-primary ring-2 ring-primary" : ""}
                />
                ))
             ) : (
                <p className="text-muted-foreground text-center py-4">Nenhum hotel encontrado.</p>
             )}
          </TabsContent>

          <TabsContent value="activities" className="space-y-4">
             {(apiResponse.activities && apiResponse.activities.length > 0) ? (
                apiResponse.activities.map((activity) => (
                <ActivityCard
                    key={activity.id}
                    {...activity}
                    onSelect={() => handleSelectActivity(activity.id)}
                    className={selectedActivities.includes(activity.id) ? "border-primary ring-2 ring-primary" : ""}
                />
                ))
             ) : (
                 <p className="text-muted-foreground text-center py-4">Nenhuma atividade encontrada.</p>
             )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default SearchResults;