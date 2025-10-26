import { useLocation, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { ArrowLeft, CreditCard, Check } from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

const Booking = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { destination, checkIn, checkOut, selectedFlight, selectedHotel, selectedActivities } = location.state || {};

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [cardNumber, setCardNumber] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  if (!destination) {
    navigate("/");
    return null;
  }

  const handleConfirmBooking = () => {
    if (!name || !email || !cardNumber) {
      toast({
        title: "Campos obrigatórios",
        description: "Por favor, preencha todos os campos",
        variant: "destructive",
      });
      return;
    }

    setIsProcessing(true);
    // Simula processamento
    setTimeout(() => {
      toast({
        title: "Reserva confirmada!",
        description: "Você receberá um email com os detalhes da sua viagem",
      });
      setIsProcessing(false);
      navigate("/");
    }, 2000);
  };

  const flightPrice = 2450;
  const hotelPrice = 680;
  const activityPrice = selectedActivities?.length * 280 || 0;
  const totalPrice = flightPrice + hotelPrice + activityPrice;

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Button variant="ghost" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-5 w-5 mr-2" />
            Voltar
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-foreground">Confirmação de Reserva</h1>
            <p className="text-muted-foreground">Finalize sua viagem para {destination}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Resumo da Reserva */}
          <div className="lg:col-span-2 space-y-6">
            {/* Dados do Passageiro */}
            <Card>
              <CardHeader>
                <CardTitle className="text-foreground">Dados do Passageiro</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
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

            {/* Pagamento */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-foreground">
                  <CreditCard className="h-5 w-5" />
                  Informações de Pagamento
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="card">Número do Cartão</Label>
                  <Input
                    id="card"
                    value={cardNumber}
                    onChange={(e) => setCardNumber(e.target.value)}
                    placeholder="0000 0000 0000 0000"
                    maxLength={19}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="expiry">Validade</Label>
                    <Input id="expiry" placeholder="MM/AA" />
                  </div>
                  <div>
                    <Label htmlFor="cvv">CVV</Label>
                    <Input id="cvv" placeholder="123" maxLength={3} />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Resumo do Pedido */}
          <div className="lg:col-span-1">
            <Card className="sticky top-8">
              <CardHeader>
                <CardTitle className="text-foreground">Resumo do Pedido</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm font-semibold text-foreground mb-2">Destino</p>
                  <p className="text-muted-foreground">{destination}</p>
                  <p className="text-sm text-muted-foreground">{checkIn} - {checkOut}</p>
                </div>

                <Separator />

                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Voo</span>
                    <span className="font-medium text-foreground">R$ {flightPrice.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Hotel</span>
                    <span className="font-medium text-foreground">R$ {hotelPrice.toFixed(2)}</span>
                  </div>
                  {selectedActivities?.length > 0 && (
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">
                        Atividades ({selectedActivities.length})
                      </span>
                      <span className="font-medium text-foreground">R$ {activityPrice.toFixed(2)}</span>
                    </div>
                  )}
                </div>

                <Separator />

                <div className="flex justify-between items-center">
                  <span className="text-lg font-bold text-foreground">Total</span>
                  <span className="text-2xl font-bold text-primary">R$ {totalPrice.toFixed(2)}</span>
                </div>

                <Button 
                  onClick={handleConfirmBooking}
                  disabled={isProcessing}
                  className="w-full bg-secondary hover:bg-secondary/90 text-secondary-foreground"
                  size="lg"
                >
                  {isProcessing ? (
                    "Processando..."
                  ) : (
                    <>
                      <Check className="h-5 w-5 mr-2" />
                      Confirmar Reserva
                    </>
                  )}
                </Button>

                <p className="text-xs text-center text-muted-foreground">
                  Ao confirmar, você concorda com nossos termos e condições
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Booking;
