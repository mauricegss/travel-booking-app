import { useSearchParams, useNavigate, useLocation } from "react-router-dom";
import { FlightCard } from "@/components/FlightCard";
import { HotelCard } from "@/components/HotelCard";
import { ActivityCard } from "@/components/ActivityCard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import {
  AlertCircle,
  ArrowLeft,
  Loader2,
  Bookmark, // <-- MUDANÇA: Ícone
} from "lucide-react";
import { useEffect, useState } from "react";
import { useToast } from "@/hooks/use-toast";
import {
  TripDataResponse,
  ApiFlight,
  ApiHotel,
  ApiActivity,
} from "@/services/api";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import ReactMarkdown from "react-markdown"; // <-- MUDANÇA: Importa Markdown

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

  // MUDANÇA: Os tipos agora vêm da API, não apenas strings
  const [selectedFlight, setSelectedFlight] = useState<ApiFlight | null>(null);
  const [selectedHotel, setSelectedHotel] = useState<ApiHotel | null>(null);
  const [selectedActivities, setSelectedActivities] = useState<ApiActivity[]>(
    [],
  );

  useEffect(() => {
    if (location.state?.apiResponse) {
      setApiResponse(location.state.apiResponse);
    }
    setIsLoading(false);
  }, [location.state]);

  // MUDANÇA: As funções de seleção agora salvam o objeto inteiro
  const handleSelectFlight = (flight: ApiFlight) => {
    if (selectedFlight?.id === flight.id) {
      setSelectedFlight(null); // Permite desmarcar
      toast({
        title: "Voo removido",
      });
    } else {
      setSelectedFlight(flight);
      toast({
        title: "Voo selecionado",
        description: "Voo adicionado ao seu resumo.",
      });
    }
  };

  const handleSelectHotel = (hotel: ApiHotel) => {
    if (selectedHotel?.id === hotel.id) {
      setSelectedHotel(null); // Permite desmarcar
      toast({
        title: "Hotel removido",
      });
    } else {
      setSelectedHotel(hotel);
      toast({
        title: "Hotel selecionado",
        description: "Hotel adicionado ao seu resumo.",
      });
    }
  };

  const handleSelectActivity = (activity: ApiActivity) => {
    if (selectedActivities.find((a) => a.id === activity.id)) {
      setSelectedActivities(
        selectedActivities.filter((a) => a.id !== activity.id),
      );
      toast({
        title: "Atividade removida",
      });
    } else {
      setSelectedActivities([...selectedActivities, activity]);
      toast({
        title: "Atividade adicionada",
      });
    }
  };

  // MUDANÇA: Renomeada e lógica atualizada
  const handleGoToSummary = () => {
    if (
      !selectedFlight &&
      !selectedHotel &&
      selectedActivities.length === 0
    ) {
      toast({
        title: "Nenhum item selecionado",
        description: "Selecione ao menos um item para salvar no resumo.",
        variant: "destructive",
      });
      return;
    }

    navigate("/summary", { // <-- MUDANÇA: Rota
      state: {
        destination: apiResponse?.destination ?? destination,
        checkIn: apiResponse?.start_date ?? checkIn,
        checkOut: apiResponse?.end_date ?? checkOut,
        // MUDANÇA: Passa os objetos completos
        flightDetails: selectedFlight,
        hotelDetails: selectedHotel,
        activityDetails: selectedActivities,
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

  if (
    !apiResponse ||
    (apiResponse.error && (!apiResponse.flights || apiResponse.flights.length === 0))
  ) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Erro no Planejamento</AlertTitle>
          <AlertDescription>
            {apiResponse?.itinerary ||
              apiResponse?.error ||
              "Não foi possível carregar os resultados. Por favor, tente novamente."}
          </AlertDescription>
        </Alert>
        <Button variant="outline" onClick={() => navigate("/")} className="mt-4">
          <ArrowLeft className="h-5 w-5 mr-2" />
          Voltar
        </Button>
      </div>
    );
  }

  // Estilo de fundo similar ao Index
  return (
    <div
      className="min-h-screen bg-cover bg-center bg-fixed"
      style={{
        backgroundImage:
          "linear-gradient(to bottom, hsl(var(--background) / 0.9), hsl(var(--background) / 1)), url(/src/assets/hero-beach.jpg)",
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mb-8">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="icon"
              className="hidden sm:inline-flex"
              onClick={() => navigate(-1)}
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-foreground">
                Recomendações para {apiResponse.destination ?? destination}
              </h1>
              <p className="text-muted-foreground">
                {apiResponse.start_date ?? checkIn} até{" "}
                {apiResponse.end_date ?? checkOut}
              </p>
            </div>
          </div>
          <Button
            onClick={handleGoToSummary} // <-- MUDANÇA
            size="lg"
            className="bg-secondary hover:bg-secondary/90 text-secondary-foreground w-full sm:w-auto"
            // MUDANÇA: Lógica do disabled
            disabled={
              !selectedFlight &&
              !selectedHotel &&
              selectedActivities.length === 0
            }
          >
            <Bookmark className="h-5 w-5 mr-2" /> 
            Salvar Itens Selecionados 
          </Button>
        </div>

        {/* MUDANÇA: Relatório da IA agora é o destaque! */}
        <Card className="mb-8 bg-card/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle>Resumo do seu Agente de IA</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm dark:prose-invert max-w-none text-left text-card-foreground">
              <ReactMarkdown>{apiResponse.itinerary}</ReactMarkdown>
            </div>
          </CardContent>
        </Card>

        {/* Abas com os links detalhados */}
        <h2 className="text-2xl font-bold text-foreground mb-4">
          Links e Opções Detalhadas
        </h2>
        <Tabs defaultValue="flights" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-8">
            <TabsTrigger value="flights">
              Voos {selectedFlight && "✓"}
            </TabsTrigger>
            <TabsTrigger value="hotels">
              Hotéis {selectedHotel && "✓"}
            </TabsTrigger>
            <TabsTrigger value="activities">
              Atividades ({selectedActivities.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="flights" className="space-y-4">
            {apiResponse.flights && apiResponse.flights.length > 0 ? (
              apiResponse.flights.map((flight) => (
                <FlightCard
                  key={flight.id}
                  {...flight}
                  onSelect={() => handleSelectFlight(flight)}
                  className={
                    selectedFlight?.id === flight.id
                      ? "border-primary ring-2 ring-primary"
                      : "bg-card/80 backdrop-blur-sm"
                  }
                />
              ))
            ) : (
              <p className="text-muted-foreground text-center py-4">
                Nenhum voo encontrado.
              </p>
            )}
          </TabsContent>

          <TabsContent value="hotels" className="space-y-4">
            {apiResponse.hotels && apiResponse.hotels.length > 0 ? (
              apiResponse.hotels.map((hotel) => (
                <HotelCard
                  key={hotel.id}
                  {...hotel}
                  onSelect={() => handleSelectHotel(hotel)}
                  className={
                    selectedHotel?.id === hotel.id
                      ? "border-primary ring-2 ring-primary"
                      : "bg-card/80 backdrop-blur-sm"
                  }
                />
              ))
            ) : (
              <p className="text-muted-foreground text-center py-4">
                Nenhum hotel encontrado.
              </p>
            )}
          </TabsContent>

          <TabsContent value="activities" className="space-y-4">
            {apiResponse.activities && apiResponse.activities.length > 0 ? (
              apiResponse.activities.map((activity) => (
                <ActivityCard
                  key={activity.id}
                  {...activity}
                  onSelect={() => handleSelectActivity(activity)}
                  className={
                    selectedActivities.find((a) => a.id === activity.id)
                      ? "border-primary ring-2 ring-primary"
                      : "bg-card/80 backdrop-blur-sm"
                  }
                />
              ))
            ) : (
              <p className="text-muted-foreground text-center py-4">
                Nenhuma atividade encontrada.
              </p>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default SearchResults;