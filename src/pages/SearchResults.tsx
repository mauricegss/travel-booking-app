import { useSearchParams, useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  AlertCircle,
  ArrowLeft,
  Loader2,
  Download,
} from "lucide-react";
import { useEffect, useState } from "react";
import { TripDataResponse } from "@/services/api";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import ReactMarkdown from "react-markdown";
import heroImage from "@/assets/hero-beach.jpg";

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
    }
    setIsLoading(false);
  }, [location.state]);

  const handleDownloadReport = () => {
    if (!apiResponse?.itinerary) {
      alert("Não há relatório para baixar.");
      return;
    }
    const blob = new Blob([apiResponse.itinerary], { type: "text/markdown" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    const fileName = `Relatorio-Viagem-${apiResponse.destination || 'Destino'}.md`;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
  };

  // ----- Renderização -----

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-background">
        <Loader2 className="h-16 w-16 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div
      className="min-h-screen bg-cover bg-center bg-fixed flex flex-col items-center p-4 relative"
      style={{ backgroundImage: `url(${heroImage})` }}
    >
      {/* Overlay idêntico ao Index */}
      <div className="absolute inset-0 bg-black/50 z-0"></div>

      {/* Container principal */}
      <div className="relative z-10 container mx-auto flex flex-col items-center gap-8 w-full max-w-6xl py-8 md:py-16">
        
        {(!apiResponse ||
          (apiResponse.error && (!apiResponse.flights || apiResponse.flights.length === 0))
        ) ? (
          <Card className="w-full max-w-2xl bg-white/10 backdrop-blur-sm rounded-2xl shadow-xl border-destructive">
            <CardHeader>
              <AlertTitle className="text-destructive-foreground text-lg font-bold flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-destructive" />
                Erro no Planejamento
              </AlertTitle>
            </CardHeader>
            <CardContent>
              <AlertDescription className="text-white/90">
                {apiResponse?.itinerary ||
                  apiResponse?.error ||
                  "Não foi possível carregar os resultados. Por favor, tente novamente."}
              </AlertDescription>
              {/* --- [INÍCIO DA MUDANÇA] --- */}
              {/* Botão "Voltar" (erro) com estilo "vidro fosco" */}
              <Button
                onClick={() => navigate("/")} 
                className="mt-6 bg-white/20 backdrop-blur-sm text-white border border-white/30 hover:bg-white/30 transition-colors"
              >
              {/* --- [FIM DA MUDANÇA] --- */}
                <ArrowLeft className="h-5 w-5 mr-2" />
                Voltar para a Busca
              </Button>
            </CardContent>
          </Card>
        ) : (
          
          <>
            <div className="w-full flex flex-col sm:flex-row items-center justify-between gap-4 mb-4">
              <div className="flex items-center gap-4">
                {/* --- [INÍCIO DA MUDANÇA] --- */}
                {/* Botão "Voltar" (ícone) com estilo "vidro fosco" */}
                <Button
                  variant="outline"
                  size="icon"
                  className="hidden sm:inline-flex bg-white/20 backdrop-blur-sm text-white border border-white/30 hover:bg-white/30 transition-colors"
                  onClick={() => navigate(-1)}
                >
                {/* --- [FIM DA MUDANÇA] --- */}
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
              
              <Button
                onClick={handleDownloadReport}
                size="lg"
                className="w-full sm:w-auto bg-white/20 backdrop-blur-sm text-white border border-white/30 hover:bg-white/30 transition-colors"
              >
                <Download className="h-5 w-5 mr-2" />
                Salvar Relatório
              </Button>
            </div>

            <Card className="w-full bg-white/10 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20">
              <CardHeader>
                <CardTitle className="text-white text-2xl">
                  Resumo do seu Agente de IA
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm prose-invert max-w-none text-left">
                  <ReactMarkdown>{apiResponse.itinerary}</ReactMarkdown>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
};

export default SearchResults;