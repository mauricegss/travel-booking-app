import { Plane, Hotel, MapPinned, Sparkles } from "lucide-react";
import { SearchBar } from "@/components/SearchBar";
import { AgentCard } from "@/components/AgentCard";
import heroImage from "@/assets/hero-beach.jpg";

const Index = () => {
  const agents = [
    {
      icon: Plane,
      title: "Busca de Voos",
      description: "Consulta APIs e otimiza resultados baseados nas suas preferências." 
    },
    {
      icon: Hotel,
      title: "Hospedagem",
      description: "Conecta-se a APIs de hotéis e aplica filtros considerando seu orçamento." 
    },
    {
      icon: MapPinned,
      title: "Atividades Locais",
      description: "Recomenda atrações e experiências baseadas no seu perfil e destino." 
    },
    {
      icon: Sparkles,
      title: "Integração e Reserva",
      description: "Combina informações e oferece interface simplificada para confirmação." 
    }
  ];

  return (
    <div 
      className="min-h-screen bg-cover bg-center bg-fixed flex flex-col justify-center items-center p-4 relative" 
      style={{ backgroundImage: `url(${heroImage})` }}
    >
      {/* Overlay semitransparente */}
      <div className="absolute inset-0 bg-black/50 z-0"></div>

      {/* Container principal */}
      <div className="relative z-10 container mx-auto flex flex-col items-center gap-8 md:gap-12 w-full"> 
        
        {/* Conteúdo da Hero Section */}
        <div className="text-center text-white pt-16 md:pt-24">
          <h1 className="text-4xl md:text-6xl font-bold mb-4 drop-shadow-2xl">
            Planeje sua viagem dos sonhos
          </h1>
          <p className="text-lg md:text-xl text-white/95 mb-8 max-w-3xl mx-auto drop-shadow-lg">
            Agentes de IA trabalham para encontrar as melhores opções personalizadas para você
          </p>
          <SearchBar /> 
        </div>

        {/* Agents Section */}
        <section className="w-full max-w-6xl pb-16 md:pb-24">
          <div className="text-center mb-10 text-white">
            <h2 className="text-3xl md:text-4xl font-bold mb-3 drop-shadow-lg">
              Agentes Inteligentes
            </h2>
            <p className="text-lg text-white/90 max-w-2xl mx-auto drop-shadow-lg">
              Nossa IA especializada cuida de cada detalhe da sua viagem
            </p>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"> 
            {agents.map((agent, index) => (
              // --- [INÍCIO DA MUDANÇA] ---
              // Aplicando o estilo de "vidro fosco" completo aqui
              <div 
                key={index} 
                className="bg-white/10 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20"
              > 
              {/* --- [FIM DA MUDANÇA] --- */}
                <AgentCard {...agent} />
              </div>
            ))}
          </div>
        </section>

      </div>
    </div>
  );
};

export default Index;