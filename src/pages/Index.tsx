import { Plane, Hotel, MapPinned, Sparkles } from "lucide-react";
import { SearchBar } from "@/components/SearchBar";
import { AgentCard } from "@/components/AgentCard";
import { DestinationCard } from "@/components/DestinationCard";
import heroImage from "@/assets/hero-beach.jpg";
import parisImage from "@/assets/paris.jpg";
import tokyoImage from "@/assets/tokyo.jpg";
import maldivesImage from "@/assets/maldives.jpg";
import newyorkImage from "@/assets/newyork.jpg";

const Index = () => {
  const agents = [
    {
      icon: Plane,
      title: "Busca de Voos",
      description: "Consulta APIs de companhias aéreas e otimiza resultados baseados nas suas preferências de horário, preço e conforto."
    },
    {
      icon: Hotel,
      title: "Hospedagem",
      description: "Conecta-se a APIs de hotéis e aplica filtros personalizados considerando seu orçamento, localização desejada e serviços."
    },
    {
      icon: MapPinned,
      title: "Atividades Locais",
      description: "Recomenda atrações, eventos e experiências únicas baseadas no seu perfil e destino escolhido."
    },
    {
      icon: Sparkles,
      title: "Integração e Reserva",
      description: "Combina todas as informações e oferece uma interface simplificada para confirmação e pagamento seguro."
    }
  ];

  const destinations = [
    {
      image: parisImage,
      title: "Paris",
      description: "Cidade Luz e capital do romance",
      price: "R$ 3.200"
    },
    {
      image: tokyoImage,
      title: "Tóquio",
      description: "Modernidade e tradição japonesa",
      price: "R$ 4.800"
    },
    {
      image: maldivesImage,
      title: "Maldivas",
      description: "Paraíso tropical no Oceano Índico",
      price: "R$ 5.500"
    },
    {
      image: newyorkImage,
      title: "Nova York",
      description: "A cidade que nunca dorme",
      price: "R$ 3.800"
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative h-[90vh] flex items-center justify-center overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${heroImage})` }}
        >
          <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-black/30 to-background" />
        </div>
        
        <div className="relative z-10 container mx-auto px-4 text-center">
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 drop-shadow-2xl">
            Planeje sua viagem dos sonhos
          </h1>
          <p className="text-xl md:text-2xl text-white/95 mb-12 max-w-2xl mx-auto drop-shadow-lg">
            Agentes de IA trabalham para encontrar as melhores opções personalizadas para você
          </p>
          <SearchBar />
        </div>
      </section>

      {/* Agents Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Agentes Inteligentes
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Nossa equipe de IA especializada cuida de cada detalhe da sua viagem
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {agents.map((agent, index) => (
              <AgentCard key={index} {...agent} />
            ))}
          </div>
        </div>
      </section>

      {/* Destinations Section */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Destinos Populares
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Descubra os lugares mais incríveis do mundo
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {destinations.map((destination, index) => (
              <DestinationCard key={index} {...destination} />
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-card border-t border-border py-12 px-4">
        <div className="container mx-auto max-w-6xl text-center">
          <p className="text-muted-foreground">
            © 2025 Travel Booking App. Reservas inteligentes com tecnologia de IA.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
