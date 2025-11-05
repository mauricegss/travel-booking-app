import { useSearchParams, useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  AlertCircle,
  ArrowLeft,
  Loader2,
  Download, // <-- MUDANÇA: Ícone de Download
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

const SearchResults = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();
  const destination = searchParams.get("destination");
  const checkIn = searchParams.get("checkin");
  const checkOut = searchParams.get("checkout");

  const [apiResponse, setApiResponse] = useState<TripDataResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // REMOVEMOS os estados de seleção (selectedFlight, selectedHotel, etc.)

  useEffect(() => {
    if (location.state?.apiResponse) {
      setApiResponse(location.state.apiResponse);
    }
    setIsLoading(false);
  }, [location.state]);

  // REMOVEMOS as funções handleSelect (handleSelectFlight, etc.)

  // MUDANÇA: Esta função agora baixa o relatório
  const handleDownloadReport = () => {
    if (!apiResponse?.itinerary) {
      alert("Não há relatório para baixar.");
      return;
    }

    // Cria um "Blob" (Binary Large Object) com o texto do relatório
    const blob = new Blob([apiResponse.itinerary], { type: "text/markdown" });

    // Cria um link <a> em memória
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    
    // Define o nome do arquivo que será baixado
    const fileName = `Relatorio-Viagem-${apiResponse.destination || 'Destino'}.md`;
    link.download = fileName;

    // Simula o clique no link para iniciar o download
    document.body.appendChild(link);
    link.click();

    // Remove o link da memória
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

  // Se houver erro ou resposta vazia, mostra o erro
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
            onClick={handleDownloadReport} // <-- MUDANÇA
            size="lg"
            className="bg-secondary hover:bg-secondary/90 text-secondary-foreground w-full sm:w-auto"
            // O botão está sempre ativo se o relatório existe
          >
            <Download className="h-5 w-5 mr-2" />
            Salvar Relatório (.md)
          </Button>
        </div>

        {/* Relatório da IA é a única coisa na página */}
        <Card className="bg-card/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle>Resumo do seu Agente de IA</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm dark:prose-invert max-w-none text-left text-card-foreground">
              <ReactMarkdown>{apiResponse.itinerary}</ReactMarkdown>
            </div>
          </CardContent>
        </Card>

        {/* REMOVEMOS toda a seção de <Tabs> e Cards */}
      </div>
    </div>
  );
};

export default SearchResults;