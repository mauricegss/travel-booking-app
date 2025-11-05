import { useLocation, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  ArrowLeft,
  Check,
  Link as LinkIcon,
  Plane,
  Hotel,
  MapPinned,
} from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { ApiActivity, ApiFlight, ApiHotel } from "@/services/api";

// Componente helper para criar um item da lista
const SummaryItem = ({
  icon: Icon,
  title,
  url,
}: {
  icon: React.ElementType;
  title: string;
  url: string;
}) => (
  <div className="flex items-center justify-between">
    <div className="flex items-center gap-3">
      <Icon className="h-5 w-5 text-primary" />
      <span className="text-sm font-medium text-foreground">{title}</span>
    </div>
    <Button variant="ghost" size="sm" asChild>
      <a href={url} target="_blank" rel="noopener noreferrer">
        <LinkIcon className="h-4 w-4 mr-2" />
        Ver link
      </a>
    </Button>
  </div>
);

// MUDANÇA: Componente renomeado para Summary
const Summary = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { toast } = useToast();

  const {
    destination,
    checkIn,
    checkOut,
    flightDetails,
    hotelDetails,
    activityDetails,
  } = (location.state || {}) as {
    destination: string;
    checkIn: string;
    checkOut: string;
    flightDetails: ApiFlight; // Agora espera o objeto completo
    hotelDetails: ApiHotel; // Agora espera o objeto completo
    activityDetails: ApiActivity[]; // Agora espera os objetos completos
  };

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  // MUDANÇA: Melhor verificação. Se não houver *nada* para salvar, volta.
  if (!destination && !flightDetails && !hotelDetails && !activityDetails) {
    navigate("/");
    return null;
  }

  const handleConfirmSummary = () => {
    if (!name || !email) {
      toast({
        title: "Campos obrigatórios",
        description: "Por favor, preencha seu nome e email para salvar.",
        variant: "destructive",
      });
      return;
    }

    setIsProcessing(true);
    // Simula o envio do resumo da pesquisa
    setTimeout(() => {
      toast({
        title: "Pesquisa Salva!",
        description: `Um resumo dos links para sua viagem para ${destination} foi salvo.`,
      });
      setIsProcessing(false);
      navigate("/");
    }, 1500);
  };

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
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Button variant="outline" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-5 w-5 mr-2" />
            Voltar
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              Resumo da Pesquisa
            </h1>
            <p className="text-muted-foreground">
              Salve os links de interesse para sua viagem
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Informações do Usuário (Para salvar a pesquisa) */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-foreground">
                  Salvar suas Recomendações
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  Preencha seus dados para salvar este resumo. (Isso é uma
                  simulação)
                </p>
                <div>
                  <Label htmlFor="name">Nome Completo</Label>
                  <Input
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Digite seu nome completo"
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="seu@email.com"
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Resumo dos Itens Selecionados */}
          <div className="lg:col-span-1">
            <Card className="sticky top-8">
              <CardHeader>
                <CardTitle className="text-foreground">Itens Salvos</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm font-semibold text-foreground mb-2">
                    Destino
                  </p>
                  <p className="text-muted-foreground">{destination}</p>
                  <p className="text-sm text-muted-foreground">
                    {checkIn} - {checkOut}
                  </p>
                </div>

                <Separator />

                <div className="space-y-3">
                  {/* Item de Voo */}
                  {flightDetails && (
                    <SummaryItem
                      icon={Plane}
                      title={flightDetails.airline}
                      url={flightDetails.id}
                    />
                  )}

                  {/* Item de Hotel */}
                  {hotelDetails && (
                    <SummaryItem
                      icon={Hotel}
                      title={hotelDetails.name}
                      url={hotelDetails.id}
                    />
                  )}

                  {/* Itens de Atividade */}
                  {activityDetails?.length > 0 &&
                    activityDetails.map((activity) => (
                      <SummaryItem
                        key={activity.id}
                        icon={MapPinned}
                        title={activity.title}
                        url={activity.id}
                      />
                    ))}
                </div>

                <Separator />

                <Button
                  onClick={handleConfirmSummary}
                  disabled={isProcessing}
                  className="w-full bg-secondary hover:bg-secondary/90 text-secondary-foreground"
                  size="lg"
                >
                  {isProcessing ? (
                    "Salvando..."
                  ) : (
                    <>
                      <Check className="h-5 w-5 mr-2" />
                      Salvar Resumo
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Summary;