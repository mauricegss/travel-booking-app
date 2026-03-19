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
  Save // <-- Ícone de Salvar
} from "lucide-react";
import { useEffect, useState } from "react";
import {
  TripDataResponse,
  ApiFlight,
  ApiHotel,
  ApiActivity,
  CuratedRecommendation,
  saveReport // <-- Função de salvar
} from "@/services/api";
import { useToast } from "@/hooks/use-toast"; // <-- Toast
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";
import { Badge } from "@/components/ui/badge";
import heroImage from "@/assets/hero-beach.jpg";
import { SearchBar } from "@/components/SearchBar"; 
import { LogOut, FileText, Info, Clock } from "lucide-react"; 

// --- Componentes Auxiliares (Cards) Compactos ---
const CuratedFlightCard = ({ item }: { item: CuratedRecommendation<ApiFlight> }) => (
  <Card className="w-full h-full bg-black/40 backdrop-blur-md rounded-2xl shadow-xl border border-white/10 text-white overflow-hidden hover:bg-black/50 transition-colors flex flex-col">
    <div className="flex flex-col sm:flex-row h-full">
      {/* Coluna da Logo */}
      <div className="sm:w-1/3 bg-white/5 flex flex-col items-center justify-center p-4 sm:border-r border-white/10">
        <div className="bg-white rounded-xl p-2 mb-3 shadow-md flex items-center justify-center w-16 h-16">
          {item.data.image_url ? (
            <img src={item.data.image_url} alt={item.data.airline} className="max-w-full max-h-full object-contain" />
          ) : (
            <Plane className="h-8 w-8 text-blue-900" />
          )}
        </div>
        <span className="text-[11px] font-bold text-white/90 text-center tracking-wider uppercase">{item.data.airline}</span>
      </div>
      
      {/* Detalhes do Voo */}
      <div className="sm:w-2/3 flex flex-col justify-between p-5 relative">
        <div className="absolute top-4 right-4">
           <Badge className="bg-blue-600/30 text-blue-100 border-blue-500/30 font-bold px-3 py-1 text-sm shadow-sm">{item.data.price}</Badge>
        </div>

        <div className="w-full pr-24 mb-6">
          <div className="flex items-center gap-2 mb-1">
             <Clock className="w-4 h-4 text-white/50" />
             <span className="text-sm font-medium text-white/90">{item.data.duration}</span>
             <span className="text-[10px] uppercase tracking-wider font-bold text-white/50 bg-white/10 px-2 py-0.5 rounded-full">{item.data.stops} parada(s)</span>
          </div>
        </div>
        
        <div className="flex justify-between items-center mb-6 w-full bg-black/30 rounded-xl p-4 border border-white/5 shadow-inner">
          <div className="flex flex-col col-span-1 text-left">
             <span className="text-[9px] uppercase tracking-widest text-white/50 mb-1 font-bold">Saída</span>
             <span className="text-[15px] font-bold text-white leading-tight">{item.data.departure}</span>
          </div>
          
          <div className="flex flex-col flex-grow mx-4 items-center justify-center">
             <div className="w-full h-[1px] bg-gradient-to-r from-transparent via-blue-400/50 to-transparent relative flex items-center justify-center">
                <Plane className="w-4 h-4 text-blue-300 absolute bg-transparent p-0" />
             </div>
          </div>

          <div className="flex flex-col text-right col-span-1">
             <span className="text-[9px] uppercase tracking-widest text-white/50 mb-1 font-bold">Chegada</span>
             <span className="text-[15px] font-bold text-white leading-tight">{item.data.arrival}</span>
          </div>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-3 items-center mt-auto">
          <div className="bg-white/5 p-2 rounded-lg flex-grow border border-white/5 w-full">
            <p className="text-[11px] text-white/70 italic leading-relaxed line-clamp-2">"{item.justification}"</p>
          </div>
          <Button size="sm" asChild className="bg-white text-blue-900 border-none hover:bg-blue-50 font-bold transition-all whitespace-nowrap px-6 h-9 shadow-md hover:shadow-lg">
            <a href={item.data.id} target="_blank" rel="noopener noreferrer">Ver Voo</a>
          </Button>
        </div>
      </div>
    </div>
  </Card>
);

const CuratedHotelCard = ({ item }: { item: CuratedRecommendation<ApiHotel> }) => (
  <Card className="h-full bg-white/10 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 text-white overflow-hidden flex flex-col">
    {item.data.image_url ? (
      <img src={item.data.image_url} alt={item.data.name} className="w-full h-32 object-cover" />
    ) : (
      <div className="h-32 w-full flex items-center justify-center bg-white/5"><Hotel className="h-10 w-10 text-white/70" /></div>
    )}
    <CardHeader className="p-4 pb-2">
      <CardTitle className="text-lg text-white leading-tight">{item.data.name}</CardTitle>
      <CardDescription className="text-white/80 !mt-1 text-xs flex items-center gap-1"><MapPin className="h-3 w-3" /> <span className="truncate">{item.data.location}</span></CardDescription>
    </CardHeader>
    <CardContent className="flex-grow p-4 pt-0">
      <div className="flex justify-between items-center mb-2">
        <Badge variant="secondary" className="bg-secondary/80 text-xs">{item.data.price}</Badge>
        {item.data.rating > 0 && (<div className="flex items-center gap-1"><span className="font-bold text-sm">{item.data.rating}</span><Star className="h-3 w-3 text-yellow-400" fill="currentColor" /></div>)}
      </div>
      <p className="text-xs text-white/90 italic mt-2 line-clamp-3">"{item.justification}"</p>
    </CardContent>
    <CardFooter className="p-4 pt-0 mt-auto">
      <Button size="sm" asChild className="bg-white/20 backdrop-blur-sm text-white border border-white/30 hover:bg-white/30 transition-colors w-full h-8 text-xs">
        <a href={item.data.id} target="_blank" rel="noopener noreferrer">Ver Hotel</a>
      </Button>
    </CardFooter>
  </Card>
);

const CuratedActivityCard = ({ item }: { item: CuratedRecommendation<ApiActivity> }) => (
  <Card className="h-full bg-white/10 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 text-white overflow-hidden flex flex-col">
    {item.data.image_url ? (
      <img src={item.data.image_url} alt={item.data.title} className="w-full h-32 object-cover" />
    ) : (
      <div className="h-32 w-full flex items-center justify-center bg-white/5"><Luggage className="h-10 w-10 text-white/70" /></div>
    )}
    <CardHeader className="p-4 pb-2">
      <CardTitle className="text-lg text-white leading-tight">{item.data.title}</CardTitle>
      <CardDescription className="text-white/80 !mt-1 text-xs line-clamp-2">{item.data.description}</CardDescription>
    </CardHeader>
    <CardContent className="flex-grow p-4 pt-0">
      <Badge variant="secondary" className="bg-secondary/80 text-xs mb-2">{item.data.price}</Badge>
      <p className="text-xs text-white/90 italic mt-2 line-clamp-4">"{item.justification}"</p>
    </CardContent>
    <CardFooter className="p-4 pt-0 mt-auto">
      <Button size="sm" asChild className="bg-white/20 backdrop-blur-sm text-white border border-white/30 hover:bg-white/30 transition-colors w-full h-8 text-xs">
        <a href={item.data.id} target="_blank" rel="noopener noreferrer">Ver Atividade</a>
      </Button>
    </CardFooter>
  </Card>
);

// --- COMPONENTE PRINCIPAL ---

const SearchResults = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast(); // Hook para notificações

  const destination = searchParams.get("destination");
  const checkIn = searchParams.get("checkin");
  const checkOut = searchParams.get("checkout");

  const [apiResponse, setApiResponse] = useState<TripDataResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (location.state?.apiResponse) {
      setApiResponse(location.state.apiResponse);
    }
    // Se não tiver state, apenas exibe a barra de busca limpa (não fica em loading)
    setIsLoading(false);
  }, [location.state]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  // --- Lógica para Salvar Viagem ---
  const handleSaveTrip = async () => {
    if (!apiResponse || !apiResponse.final_report) return;
    
    const token = localStorage.getItem("token");
    if (!token) {
        toast({ title: "Login necessário", description: "Faça login para salvar sua viagem.", variant: "destructive" });
        navigate("/login"); // Redireciona para login
        return;
    }

    try {
        await saveReport({
            destination: apiResponse.destination || destination || "Destino Desconhecido",
            start_date: apiResponse.start_date || checkIn || "",
            end_date: apiResponse.end_date || checkOut || "",
            content: apiResponse.final_report
        });
        toast({ title: "Sucesso!", description: "Viagem salva nos seus relatórios." });
    } catch (error) {
        toast({ title: "Erro", description: "Não foi possível salvar a viagem.", variant: "destructive" });
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-background">
        <Loader2 className="h-16 w-16 animate-spin text-primary" />
      </div>
    );
  }

  const renderContent = () => {
    if (!apiResponse || (!apiResponse.final_report && apiResponse.error)) {
      return (
        <Card className="w-full max-w-2xl bg-white/10 backdrop-blur-sm rounded-2xl shadow-xl border-destructive text-white">
          <CardHeader>
            <AlertTitle className="text-destructive-foreground text-lg font-bold flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-destructive" /> Erro no Planejamento
            </AlertTitle>
          </CardHeader>
          <CardContent>
            <AlertDescription className="text-white/90">
              {apiResponse?.error || "Não foi possível carregar os resultados. Por favor, tente novamente."}
            </AlertDescription>
            <Button onClick={() => navigate("/")} className="mt-6 bg-white/20 backdrop-blur-sm text-white border border-white/30 hover:bg-white/30 transition-colors">
              <ArrowLeft className="h-5 w-5 mr-2" /> Voltar para a Busca
            </Button>
          </CardContent>
        </Card>
      );
    }
    
    if (apiResponse.final_report) {
      const { summary_text, curated_flights, curated_hotels, curated_activities, closing_text } = apiResponse.final_report;

      return (
        <>
          {/* Cabeçalho com Botões */}
          <div className="w-full flex flex-col sm:flex-row items-center justify-between gap-4 mb-4">
            <div className="flex items-center gap-4">
              <Button variant="outline" size="icon" className="hidden sm:inline-flex bg-white/20 backdrop-blur-sm text-white border border-white/30 hover:bg-white/30 transition-colors" onClick={() => navigate(-1)}>
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-3xl font-bold text-white drop-shadow-lg">Recomendações para {apiResponse.destination ?? destination}</h1>
                <p className="text-white/90 drop-shadow-md">{apiResponse.start_date ?? checkIn} até {apiResponse.end_date ?? checkOut}</p>
              </div>
            </div>
            {/* Botão de Salvar */}
            <Button onClick={handleSaveTrip} className="bg-green-500/80 hover:bg-green-600/80 text-white backdrop-blur-sm border border-white/20">
                <Save className="mr-2 h-4 w-4" /> Salvar Viagem
            </Button>
          </div>

          {/* Sumário */}
          <Card className="w-full bg-white/10 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 text-white">
            <CardHeader><CardTitle className="text-white text-2xl">Resumo do seu Agente de IA</CardTitle></CardHeader>
            <CardContent><p className="text-lg text-white/90">{summary_text}</p></CardContent>
          </Card>

          {/* Seções de Cards (Voos, Hotéis, Atividades) */}
          {curated_flights.length > 0 && (
            <div className="w-full">
              <h2 className="text-2xl font-bold text-white mb-4 drop-shadow-lg">✈️ Voos Recomendados</h2>
              {(() => {
                 const fallbackNotes = curated_flights.map(f => f.data.fallback_note).filter(Boolean);
                 if (fallbackNotes.length > 0) {
                   return (
                     <div className="mb-6 bg-gradient-to-r from-blue-600/20 to-indigo-600/20 backdrop-blur-xl border border-blue-500/30 rounded-2xl p-4 shadow-lg flex items-start gap-4">
                        <div className="bg-blue-500/30 p-2 rounded-full mt-1"><Info className="h-5 w-5 text-blue-300" /></div>
                        <div>
                           <h3 className="text-base font-bold text-blue-200 mb-1">Rotas Otimizadas</h3>
                           <p className="text-sm text-blue-100/90 leading-relaxed">
                              {fallbackNotes[0]} Nós ajustamos os aeroportos para garantir as melhores opções disponíveis para você.
                           </p>
                        </div>
                     </div>
                   )
                 }
                 return null;
              })()}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">{curated_flights.map((item) => (<CuratedFlightCard key={item.data.id} item={item} />))}</div>
            </div>
          )}

          {curated_hotels.length > 0 && (
            <div className="w-full">
              <h2 className="text-2xl font-bold text-white mb-4 drop-shadow-lg">🏨 Hotéis Recomendados</h2>
              <Carousel opts={{ align: "start", loop: false }} className="w-full">
                <CarouselContent className="-ml-4">
                  {curated_hotels.map((item) => (
                    <CarouselItem key={item.data.id} className="pl-4 md:basis-1/2 lg:basis-1/3">
                      <div className="p-1 h-full"><CuratedHotelCard item={item} /></div>
                    </CarouselItem>
                  ))}
                </CarouselContent>
                <CarouselPrevious className="ml-14 bg-white/30 border-white/30 text-white hover:bg-white/50" />
                <CarouselNext className="mr-14 bg-white/30 border-white/30 text-white hover:bg-white/50" />
              </Carousel>
            </div>
          )}

          {curated_activities.length > 0 && (
            <div className="w-full">
              <h2 className="text-2xl font-bold text-white mb-4 drop-shadow-lg">🗺️ Atividades Sugeridas</h2>
              <Carousel opts={{ align: "start", loop: false }} className="w-full">
                <CarouselContent className="-ml-4">
                  {curated_activities.map((item) => (
                    <CarouselItem key={item.data.id} className="pl-4 md:basis-1/2 lg:basis-1/3">
                       <div className="p-1 h-full"><CuratedActivityCard item={item} /></div>
                    </CarouselItem>
                  ))}
                </CarouselContent>
                <CarouselPrevious className="ml-14 bg-white/30 border-white/30 text-white hover:bg-white/50" />
                <CarouselNext className="mr-14 bg-white/30 border-white/30 text-white hover:bg-white/50" />
              </Carousel>
            </div>
          )}
          
           <p className="text-center text-lg text-white/90 drop-shadow-lg">{closing_text}</p>
        </>
      );
    }
    return <p className="text-white">Carregando...</p>;
  };

  return (
    <div className="min-h-screen bg-cover bg-center bg-fixed flex flex-col items-center p-4 relative" style={{ backgroundImage: `url(${heroImage})` }}>
      <div className="absolute inset-0 bg-black/50 z-0"></div>
      
      {/* Navbar Simplificada no topo */}
      <div className="relative z-20 w-full max-w-6xl mx-auto flex justify-end items-center py-4 gap-4 mt-2">
        <Button 
          onClick={() => navigate("/my-reports")}
          variant="secondary"
          className="bg-white/20 backdrop-blur-sm text-white border border-white/30 hover:bg-white/30"
        >
          <FileText className="mr-2 h-4 w-4" /> Meus Relatórios
        </Button>
        <Button 
          onClick={handleLogout}
          variant="destructive"
          className="backdrop-blur-sm shadow-lg"
        >
          <LogOut className="mr-2 h-4 w-4" /> Sair
        </Button>
      </div>

      <div className="relative z-10 container mx-auto flex flex-col items-center gap-8 w-full max-w-6xl pt-6 md:pt-10 pb-16">
        
        {/* TEXTO HERO */}
        <div className="text-center text-white mb-2">
          <h1 className="text-4xl md:text-6xl font-bold mb-4 drop-shadow-2xl">
            Para onde vamos?
          </h1>
          <p className="text-xl text-white/90 drop-shadow-lg max-w-2xl mx-auto">
            Diga-nos o destino e as datas, e nós cuidaremos do resto.
          </p>
        </div>

        {/* BARRA DE PESQUISA */}
        <div className="w-full mb-4">
           <SearchBar />
        </div>

        {/* EXIBE OS RESULTADOS SOMENTE SE HOUVER APIRESPONSE */}
        {apiResponse && renderContent()}
        
      </div>
    </div>
  );
};

export default SearchResults;