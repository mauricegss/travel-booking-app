import { useSearchParams, useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  AlertCircle,
  ArrowLeft,
  Loader2,
  ImageOff,
  Plane,
  Hotel,
  MapPin,
  Star,
  Luggage,
} from "lucide-react";
import { useEffect, useState } from "react";
import {
  TripDataResponse,
  ApiFlight,
  ApiHotel,
  ApiActivity,
  CuratedRecommendation,
} from "@/services/api";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel"; // <-- Importar Carousel
import { Badge } from "@/components/ui/badge"; // <-- Importar Badge
import heroImage from "@/assets/hero-beach.jpg";

// Componente de fallback para imagem
const ImageFallback = () => (
  <div className="flex aspect-[16/10] w-full items-center justify-center rounded-t-lg bg-muted">
    <ImageOff className="h-12 w-12 text-muted-foreground" />
  </div>
);

// Componente para o Card de Voo
const CuratedFlightCard = ({
  item,
}: {
  item: CuratedRecommendation<ApiFlight>;
}) => (
  <Card className="w-full bg-white/10 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 text-white overflow-hidden">
    <div className="flex flex-col md:flex-row">
      {/* Imagem */}
      <div className="md:w-1/3">
        {item.data.image_url ? (
          <img
            src={item.data.image_url}
            alt={item.data.airline}
            className="h-full w-full object-contain p-4 aspect-[16/10] md:aspect-auto"
          />
        ) : (
          <div className="flex h-full items-center justify-center p-4 bg-white/10">
            <Plane className="h-12 w-12 text-white/70" />
          </div>
        )}
      </div>
      {/* Conteúdo */}
      <div className="md:w-2/3">
        <CardHeader>
          <CardTitle className="text-xl text-white">
            {item.data.airline}
          </CardTitle>
          <CardDescription className="text-white/80 !mt-0">
            {item.data.duration} ({item.data.stops} parada(s))
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex justify-between items-center mb-4">
            <div>
              <p className="text-sm text-white/70">Partida</p>
              <p className="text-lg font-semibold">{item.data.departure}</p>
            </div>
            <div>
              <p className="text-sm text-white/70">Chegada</p>
              <p className="text-lg font-semibold">{item.data.arrival}</p>
            </div>
            <div>
              <p className="text-sm text-white/70">Preço</p>
              <p className="text-lg font-semibold text-secondary-foreground">
                {item.data.price}
              </p>
            </div>
          </div>
          <p className="text-sm text-white/90 italic">
            "{item.justification}"
          </p>
        </CardContent>
        <CardFooter>
          <Button
            asChild
            className="bg-white/20 backdrop-blur-sm text-white border border-white/30 hover:bg-white/30 transition-colors w-full"
          >
            <a href={item.data.id} target="_blank" rel="noopener noreferrer">
              Ver Voo
            </a>
          </Button>
        </CardFooter>
      </div>
    </div>
  </Card>
);

// Componente para o Card de Hotel (usado no Carousel)
const CuratedHotelCard = ({
  item,
}: {
  item: CuratedRecommendation<ApiHotel>;
}) => (
  <Card className="h-full bg-white/10 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 text-white overflow-hidden flex flex-col">
    {item.data.image_url ? (
      <img
        src={item.data.image_url}
        alt={item.data.name}
        className="w-full h-48 object-cover"
      />
    ) : (
      <div className="h-48 w-full flex items-center justify-center bg-white/5">
        <Hotel className="h-12 w-12 text-white/70" />
      </div>
    )}
    <CardHeader>
      <CardTitle className="text-xl text-white">{item.data.name}</CardTitle>
      <CardDescription className="text-white/80 !mt-0 flex items-center gap-2">
        <MapPin className="h-4 w-4" /> {item.data.location}
      </CardDescription>
    </CardHeader>
    <CardContent className="flex-grow">
      <div className="flex justify-between items-center mb-2">
        <Badge variant="secondary" className="bg-secondary/80">
          {item.data.price}
        </Badge>
        {item.data.rating > 0 && (
          <div className="flex items-center gap-1">
            <span className="font-bold">{item.data.rating}</span>
            <Star className="h-4 w-4 text-yellow-400" fill="currentColor" />
          </div>
        )}
      </div>
      <p className="text-sm text-white/90 italic mt-4">
        "{item.justification}"
      </p>
    </CardContent>
    <CardFooter>
      <Button
        asChild
        className="bg-white/20 backdrop-blur-sm text-white border border-white/30 hover:bg-white/30 transition-colors w-full"
      >
        <a href={item.data.id} target="_blank" rel="noopener noreferrer">
          Ver Hotel
        </a>
      </Button>
    </CardFooter>
  </Card>
);

// Componente para o Card de Atividade (usado no Carousel)
const CuratedActivityCard = ({
  item,
}: {
  item: CuratedRecommendation<ApiActivity>;
}) => (
  <Card className="h-full bg-white/10 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 text-white overflow-hidden flex flex-col">
    {item.data.image_url ? (
      <img
        src={item.data.image_url}
        alt={item.data.title}
        className="w-full h-48 object-cover"
      />
    ) : (
      <div className="h-48 w-full flex items-center justify-center bg-white/5">
        <Luggage className="h-12 w-12 text-white/70" />
      </div>
    )}
    <CardHeader>
      <CardTitle className="text-xl text-white">{item.data.title}</CardTitle>
      <CardDescription className="text-white/80 !mt-0">
        {item.data.description}
      </CardDescription>
    </CardHeader>
    <CardContent className="flex-grow">
      <Badge variant="secondary" className="bg-secondary/80">
        {item.data.price}
      </Badge>
      <p className="text-sm text-white/90 italic mt-4">
        "{item.justification}"
      </p>
    </CardContent>
    <CardFooter>
      <Button
        asChild
        className="bg-white/20 backdrop-blur-sm text-white border border-white/30 hover:bg-white/30 transition-colors w-full"
      >
        <a href={item.data.id} target="_blank" rel="noopener noreferrer">
          Ver Atividade
        </a>
      </Button>
    </CardFooter>
  </Card>
);

// --- COMPONENTE PRINCIPAL DA PÁGINA ---

const SearchResults = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();
  const destination = searchParams.get("destination");
  const checkIn = searchParams.get("checkin");
  const checkOut = searchParams.get("checkout");

  const [apiResponse, setApiResponse] = useState<TripDataResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (location.state?.apiResponse) {
      setApiResponse(location.state.apiResponse);
      console.log("API Response recebida:", location.state.apiResponse);
    }
    setIsLoading(false);
  }, [location.state]);

  // Removemos o handleDownloadReport
  
  // ----- Renderização -----

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-background">
        <Loader2 className="h-16 w-16 animate-spin text-primary" />
      </div>
    );
  }

  // Define o conteúdo a ser renderizado
  const renderContent = () => {
    if (
      !apiResponse ||
      (!apiResponse.final_report && apiResponse.error)
    ) {
      return (
        <Card className="w-full max-w-2xl bg-white/10 backdrop-blur-sm rounded-2xl shadow-xl border-destructive text-white">
          <CardHeader>
            <AlertTitle className="text-destructive-foreground text-lg font-bold flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-destructive" />
              Erro no Planejamento
            </AlertTitle>
          </CardHeader>
          <CardContent>
            <AlertDescription className="text-white/90">
              {apiResponse?.error ||
                "Não foi possível carregar os resultados. Por favor, tente novamente."}
            </AlertDescription>
            <Button
              onClick={() => navigate("/")}
              className="mt-6 bg-white/20 backdrop-blur-sm text-white border border-white/30 hover:bg-white/30 transition-colors"
            >
              <ArrowLeft className="h-5 w-5 mr-2" />
              Voltar para a Busca
            </Button>
          </CardContent>
        </Card>
      );
    }
    
    // Se temos um relatório (mesmo que parcial)
    if (apiResponse.final_report) {
      const { 
        summary_text, 
        curated_flights, 
        curated_hotels, 
        curated_activities, 
        closing_text 
      } = apiResponse.final_report;

      return (
        <>
          {/* Cabeçalho */}
          <div className="w-full flex flex-col sm:flex-row items-center justify-between gap-4 mb-4">
            <div className="flex items-center gap-4">
              <Button
                variant="outline"
                size="icon"
                className="hidden sm:inline-flex bg-white/20 backdrop-blur-sm text-white border border-white/30 hover:bg-white/30 transition-colors"
                onClick={() => navigate(-1)}
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-3xl font-bold text-white drop-shadow-lg">
                  Recomendações para {apiResponse.destination ?? destination}
                </h1>
                <p className="text-white/90 drop-shadow-md">
                  {apiResponse.start_date ?? checkIn} até{" "}
                  {apiResponse.end_date ?? checkOut}
                </p>
              </div>
            </div>
            {/* Botão de Download removido */}
          </div>

          {/* Sumário */}
          <Card className="w-full bg-white/10 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 text-white">
            <CardHeader>
              <CardTitle className="text-white text-2xl">
                Resumo do seu Agente de IA
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-lg text-white/90">{summary_text}</p>
            </CardContent>
          </Card>

          {/* Voos */}
          {curated_flights.length > 0 && (
            <div className="w-full">
              <h2 className="text-2xl font-bold text-white mb-4 drop-shadow-lg">✈️ Voos Recomendados</h2>
              <div className="grid grid-cols-1 gap-6">
                {curated_flights.map((item) => (
                  <CuratedFlightCard key={item.data.id} item={item} />
                ))}
              </div>
            </div>
          )}

          {/* Hotéis */}
          {curated_hotels.length > 0 && (
            <div className="w-full">
              <h2 className="text-2xl font-bold text-white mb-4 drop-shadow-lg">🏨 Hotéis Recomendados</h2>
              <Carousel
                opts={{
                  align: "start",
                  loop: false,
                }}
                className="w-full"
              >
                <CarouselContent className="-ml-4">
                  {curated_hotels.map((item) => (
                    <CarouselItem key={item.data.id} className="pl-4 md:basis-1/2 lg:basis-1/3">
                      <div className="p-1 h-full">
                        <CuratedHotelCard item={item} />
                      </div>
                    </CarouselItem>
                  ))}
                </CarouselContent>
                <CarouselPrevious className="ml-14 bg-white/30 border-white/30 text-white hover:bg-white/50" />
                <CarouselNext className="mr-14 bg-white/30 border-white/30 text-white hover:bg-white/50" />
              </Carousel>
            </div>
          )}

          {/* Atividades */}
          {curated_activities.length > 0 && (
            <div className="w-full">
              <h2 className="text-2xl font-bold text-white mb-4 drop-shadow-lg">🗺️ Atividades Sugeridas</h2>
              <Carousel
                opts={{
                  align: "start",
                  loop: false,
                }}
                className="w-full"
              >
                <CarouselContent className="-ml-4">
                  {curated_activities.map((item) => (
                    <CarouselItem key={item.data.id} className="pl-4 md:basis-1/2 lg:basis-1/3">
                       <div className="p-1 h-full">
                         <CuratedActivityCard item={item} />
                       </div>
                    </CarouselItem>
                  ))}
                </CarouselContent>
                <CarouselPrevious className="ml-14 bg-white/30 border-white/30 text-white hover:bg-white/50" />
                <CarouselNext className="mr-14 bg-white/30 border-white/30 text-white hover:bg-white/50" />
              </Carousel>
            </div>
          )}
          
          {/* Encerramento */}
           <p className="text-center text-lg text-white/90 drop-shadow-lg">{closing_text}</p>
        </>
      );
    }
    
    // Fallback final se algo muito estranho acontecer
    return <p className="text-white">Carregando...</p>;
  };

  return (
    <div
      className="min-h-screen bg-cover bg-center bg-fixed flex flex-col items-center p-4 relative"
      style={{ backgroundImage: `url(${heroImage})` }}
    >
      <div className="absolute inset-0 bg-black/50 z-0"></div>
      <div className="relative z-10 container mx-auto flex flex-col items-center gap-8 w-full max-w-6xl py-8 md:py-16">
        {renderContent()}
      </div>
    </div>
  );
};

export default SearchResults;