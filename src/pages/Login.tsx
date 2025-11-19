import { useState, useEffect } from "react";
import { loginUser, registerUser } from "@/services/api";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Plane, Hotel, MapPinned, Sparkles, LogIn, UserPlus } from "lucide-react";
import { AgentCard } from "@/components/AgentCard";
import heroImage from "@/assets/hero-beach.jpg";

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const { toast } = useToast();

  // Otimização: Se já tiver token, pula para a home
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      navigate("/home");
    }
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isLogin) {
        const data = await loginUser(email, password);
        localStorage.setItem("token", data.access_token);
        // toast({ title: "Bem-vindo de volta!", description: "Login realizado com sucesso." });
        navigate("/home");
      } else {
        await registerUser(email, password);
        toast({ title: "Conta criada!", description: "Faça login para continuar." });
        setIsLogin(true);
      }
    } catch (error) {
      toast({ title: "Erro", description: "Falha na autenticação. Verifique seus dados.", variant: "destructive" });
    }
  };

  const agents = [
    {
      icon: Plane,
      title: "Busca de Voos",
      description: "Consulta APIs e otimiza resultados baseados nas suas preferências." 
    },
    {
      icon: Hotel,
      title: "Hospedagem",
      description: "Conecta-se a APIs de hotéis e aplica filtros de busca inteligentes." 
    },
    {
      icon: MapPinned,
      title: "Atividades Locais",
      description: "Recomenda atrações e experiências baseadas no seu perfil." 
    },
    {
      icon: Sparkles,
      title: "Roteiro Completo",
      description: "A IA combina tudo em um relatório de viagem perfeito." 
    }
  ];

  return (
    <div 
      className="min-h-screen bg-cover bg-center bg-fixed flex flex-col items-center p-4 relative overflow-hidden" 
      style={{ backgroundImage: `url(${heroImage})` }}
    >
      <div className="absolute inset-0 bg-black/60 z-0"></div>

      <div className="relative z-10 container mx-auto flex flex-col lg:flex-row items-center justify-center gap-12 w-full min-h-screen py-10"> 
        
        {/* Lado Esquerdo: Boas Vindas e Cards */}
        <div className="flex-1 flex flex-col gap-8 text-white max-w-2xl">
          <div className="text-center lg:text-left">
            <h1 className="text-4xl md:text-6xl font-bold mb-4 drop-shadow-2xl">
              Travel Booking App
            </h1>
            <p className="text-lg md:text-xl text-white/90 mb-8 drop-shadow-lg">
              Sua próxima aventura começa aqui. Deixe nossa IA planejar cada detalhe da sua viagem dos sonhos.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4"> 
            {agents.map((agent, index) => (
              <div 
                key={index} 
                className="bg-white/10 backdrop-blur-sm rounded-xl shadow-lg border border-white/10 p-2 hover:bg-white/15 transition-colors"
              > 
                <AgentCard {...agent} />
              </div>
            ))}
          </div>
        </div>

        {/* Lado Direito: Card de Login */}
        <div className="w-full max-w-md">
          <Card className="bg-white/95 backdrop-blur-md border-none shadow-2xl">
            <CardHeader>
              <CardTitle className="text-2xl text-center text-primary">
                {isLogin ? "Acesse sua conta" : "Crie sua conta"}
              </CardTitle>
              <CardDescription className="text-center">
                {isLogin ? "Entre para planejar suas viagens" : "Junte-se a nós e explore o mundo"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Input 
                    placeholder="Seu melhor email" 
                    type="email"
                    value={email} 
                    onChange={(e) => setEmail(e.target.value)} 
                    className="bg-white"
                  />
                </div>
                <div className="space-y-2">
                  <Input 
                    type="password" 
                    placeholder="Sua senha segura" 
                    value={password} 
                    onChange={(e) => setPassword(e.target.value)} 
                    className="bg-white"
                  />
                </div>
                <Button type="submit" className="w-full text-lg h-12 font-semibold shadow-md">
                  {isLogin ? (
                    <><LogIn className="mr-2 h-5 w-5" /> Entrar</>
                  ) : (
                    <><UserPlus className="mr-2 h-5 w-5" /> Cadastrar</>
                  )}
                </Button>
              </form>
              <div className="mt-6 text-center">
                <Button 
                  variant="link" 
                  onClick={() => setIsLogin(!isLogin)} 
                  className="text-muted-foreground hover:text-primary transition-colors"
                >
                  {isLogin ? "Não tem conta? Cadastre-se gratuitamente" : "Já tem uma conta? Faça login"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

      </div>
    </div>
  );
};

export default Login;