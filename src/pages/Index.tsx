import { SearchBar } from "@/components/SearchBar";
import heroImage from "@/assets/hero-beach.jpg";
import { Button } from "@/components/ui/button";
import { LogOut, FileText } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Index = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  return (
    <div 
      className="min-h-screen bg-cover bg-center bg-fixed flex flex-col p-4 relative" 
      style={{ backgroundImage: `url(${heroImage})` }}
    >
      {/* Overlay */}
      <div className="absolute inset-0 bg-black/50 z-0"></div>

      {/* Navbar Simplificada */}
      <div className="relative z-20 w-full max-w-6xl mx-auto flex justify-end items-center py-6 gap-4">
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

      {/* Conteúdo Central */}
      <div className="relative z-10 flex-1 flex flex-col justify-center items-center w-full max-w-4xl mx-auto -mt-20"> 
        
        <div className="text-center text-white mb-12">
          <h1 className="text-4xl md:text-6xl font-bold mb-4 drop-shadow-2xl">
            Para onde vamos?
          </h1>
          <p className="text-xl text-white/90 drop-shadow-lg max-w-2xl mx-auto">
            Diga-nos o destino e as datas, e nós cuidaremos do resto.
          </p>
        </div>

        <div className="w-full">
          <SearchBar />
        </div>

      </div>
    </div>
  );
};

export default Index;