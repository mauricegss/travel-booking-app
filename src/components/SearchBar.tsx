import { Search, Calendar, MapPin, Loader2, PlaneTakeoff } from "lucide-react"; // Adiciona PlaneTakeoff
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { planTrip } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

export const SearchBar = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [origin, setOrigin] = useState("Rio de Janeiro"); // Define um valor para testes
  const [destination, setDestination] = useState("Curitiba"); // Define um valor para testes
  const [checkIn, setCheckIn] = useState("");
  const [checkOut, setCheckOut] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async () => {
    // Validação
    if (!origin || !destination || !checkIn || !checkOut) {
      toast({
        title: "Campos incompletos",
        description: "Por favor, preencha origem, destino, check-in e check-out.",
        variant: "destructive",
      });
      return;
    }
     // Validação simples de datas
    if (new Date(checkOut) <= new Date(checkIn)) {
        toast({
            title: "Datas inválidas",
            description: "A data de check-out deve ser posterior à data de check-in.",
            variant: "destructive",
        });
        return;
    }


    setIsLoading(true);
    // Cria a string de requisição para o backend
    const userRequest = `Planeje uma viagem saindo de ${origin} para ${destination} de ${checkIn} até ${checkOut}.`;

    try {
      // Chama a API
      const apiResponse = await planTrip(userRequest);
      // Navega para a página de resultados passando os dados via state
      navigate(
        // Passa os parâmetros originais na URL para exibição
        `/search-results?origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destination)}&checkin=${checkIn}&checkout=${checkOut}`,
        { state: { apiResponse } } // Passa a resposta completa da API
      );
    } catch (error) {
      console.error("Erro ao buscar planejamento:", error);
      toast({
        title: "Erro na busca",
        description: error instanceof Error ? error.message : "Não foi possível conectar ao planejador. Tente novamente.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    // Estilos do container principal
    <div className="w-full max-w-5xl mx-auto bg-white/10 backdrop-blur-sm rounded-2xl shadow-2xl p-6">
      {/* Grid para os inputs e botão */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4"> {/* Ajustado para 5 colunas */}

        {/* Input Origem */}
        <div className="relative md:col-span-1"> {/* Define a coluna */}
          <PlaneTakeoff className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input
            placeholder="Origem"
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
            className="pl-10 h-12 bg-background border-border text-foreground placeholder:text-muted-foreground"
            disabled={isLoading}
          />
        </div>

        {/* Input Destino */}
        <div className="relative md:col-span-1"> {/* Define a coluna */}
          <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input
            placeholder="Destino"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            className="pl-10 h-12 bg-background border-border text-foreground placeholder:text-muted-foreground"
            disabled={isLoading}
          />
        </div>

        {/* Input Check-in */}
        <div className="relative md:col-span-1"> {/* Define a coluna */}
          <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input
            type="date"
            value={checkIn}
            onChange={(e) => setCheckIn(e.target.value)}
            placeholder="Check-in" // Placeholder pode não aparecer em inputs date
            className="pl-10 h-12 bg-background border-border text-foreground placeholder:text-muted-foreground"
            style={{ colorScheme: "light" }} // Força o date picker claro
            disabled={isLoading}
          />
        </div>

        {/* Input Check-out */}
        <div className="relative md:col-span-1"> {/* Define a coluna */}
          <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input
            type="date"
            value={checkOut}
            onChange={(e) => setCheckOut(e.target.value)}
            placeholder="Check-out" // Placeholder pode não aparecer em inputs date
            className="pl-10 h-12 bg-background border-border text-foreground placeholder:text-muted-foreground"
            style={{ colorScheme: "light" }} // Força o date picker claro
            disabled={isLoading}
          />
        </div>

        {/* Botão Buscar */}
        <Button
          onClick={handleSearch}
          className="h-12 bg-primary hover:bg-primary/90 text-primary-foreground font-medium md:col-span-1" // Define a coluna
          disabled={isLoading}
        >
          {/* Ícone condicional de carregamento ou busca */}
          {isLoading ? (
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
          ) : (
            <Search className="mr-2 h-5 w-5" />
          )}
          {/* Texto condicional do botão */}
          {isLoading ? "Buscando..." : "Buscar"}
        </Button>
      </div>
    </div>
  );
};