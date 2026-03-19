import { useEffect, useState } from "react";
import { getReports, deleteReport, TripDataResponse } from "@/services/api";
import { Card, CardHeader, CardTitle, CardContent, CardFooter, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { Trash2, Eye, CalendarDays, MapPin, FileText, ArrowLeft, Frown } from "lucide-react";
import heroImage from "@/assets/hero-beach.jpg";
import { useToast } from "@/hooks/use-toast";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
  } from "@/components/ui/alert-dialog";

const MyReports = () => {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { toast } = useToast();

  const fetchReports = async () => {
    try {
        setLoading(true);
        const data = await getReports();
        // Ordena por ID decrescente (mais recentes primeiro)
        setReports(data.sort((a: any, b: any) => b.id - a.id));
    } catch (e) {
        console.error(e);
        toast({ title: "Erro", description: "Não foi possível carregar seus relatórios.", variant: "destructive" });
    } finally {
        setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleDelete = async (id: number) => {
    try {
        await deleteReport(id);
        toast({ title: "Sucesso", description: "Relatório excluído." });
        fetchReports(); 
    } catch (error) {
        toast({ title: "Erro", description: "Falha ao excluir.", variant: "destructive" });
    }
  };

  const handleView = (report: any) => {
    const apiResponse: TripDataResponse = {
        final_report: report.content,
        destination: report.destination,
        start_date: report.start_date,
        end_date: report.end_date,
        error: null
    };
    navigate("/home", { state: { apiResponse } });
  };

  return (
    <div 
      className="min-h-screen bg-cover bg-center bg-fixed flex flex-col p-4 relative overflow-y-auto" 
      style={{ backgroundImage: `url(${heroImage})` }}
    >
      {/* Overlay Escuro para legibilidade */}
      <div className="absolute inset-0 bg-black/50 z-0 fixed"></div>

      <div className="relative z-10 w-full max-w-7xl mx-auto py-10">
        
        {/* Cabeçalho */}
        <div className="flex flex-col md:flex-row justify-between items-center mb-10 gap-4">
            <div className="flex items-center gap-4">
                <Button 
                    variant="outline" 
                    size="icon"
                    className="bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30"
                    onClick={() => navigate("/home")}
                >
                    <ArrowLeft className="h-6 w-6" />
                </Button>
                <div>
                    <h1 className="text-3xl md:text-4xl font-bold text-white drop-shadow-lg flex items-center gap-3">
                        <FileText className="h-8 w-8 md:h-10 md:w-10" /> Meus Relatórios
                    </h1>
                    <p className="text-white/80 mt-1">Histórico das suas viagens planejadas</p>
                </div>
            </div>
        </div>

        {/* Estado de Carregamento ou Vazio */}
        {!loading && reports.length === 0 && (
            <div className="flex flex-col items-center justify-center h-[50vh] text-white/70">
                <Frown className="h-20 w-20 mb-4 opacity-50" />
                <h2 className="text-2xl font-semibold">Nenhum relatório encontrado</h2>
                <p className="mt-2">Que tal planejar sua primeira viagem agora?</p>
                <Button onClick={() => navigate("/home")} className="mt-6 bg-white text-primary hover:bg-white/90">
                    Planejar Viagem
                </Button>
            </div>
        )}

        {/* Grid de Relatórios */}
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {reports.map((report) => (
            <Card 
                key={report.id} 
                className="group relative bg-white/5 hover:bg-white/10 backdrop-blur-xl border-white/10 text-white overflow-hidden transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_20px_50px_rgba(0,0,0,0.5)] flex flex-col justify-between"
            >
                {/* Glow de fundo */}
                <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/20 rounded-full blur-3xl -mr-10 -mt-10 pointer-events-none transition-opacity opacity-40 group-hover:opacity-100"></div>

                <CardHeader className="pb-4 relative z-10">
                    <div className="flex justify-between items-start mb-4">
                        <div className="bg-gradient-to-br from-white/10 to-white/5 p-3 rounded-xl border border-white/10 shadow-inner group-hover:ring-2 ring-blue-400/30 transition-all">
                             <MapPin className="h-6 w-6 text-blue-300 drop-shadow-sm" />
                        </div>
                        {/* Botão de Deletar com Confirmação */}
                        <AlertDialog>
                            <AlertDialogTrigger asChild>
                                <Button variant="ghost" size="icon" className="text-white/40 hover:text-red-400 hover:bg-red-500/20 -mr-2 -mt-2 transition-colors">
                                    <Trash2 className="h-5 w-5" />
                                </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent className="bg-slate-900 border-slate-700 text-white rounded-2xl">
                                <AlertDialogHeader>
                                    <AlertDialogTitle className="text-xl">Excluir Relatório?</AlertDialogTitle>
                                    <AlertDialogDescription className="text-slate-400">
                                        Esta ação não pode ser desfeita.
                                    </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter className="mt-4">
                                    <AlertDialogCancel className="bg-transparent border-slate-600 text-white hover:bg-slate-800 rounded-lg">Cancelar</AlertDialogCancel>
                                    <AlertDialogAction onClick={() => handleDelete(report.id)} className="bg-red-600 hover:bg-red-700 border-none rounded-lg font-bold">
                                        Excluir
                                    </AlertDialogAction>
                                </AlertDialogFooter>
                            </AlertDialogContent>
                        </AlertDialog>
                    </div>
                    <CardTitle className="text-2xl font-bold truncate tracking-tight" title={report.destination}>
                        {report.destination}
                    </CardTitle>
                </CardHeader>
                
                <CardContent className="relative z-10 flex-grow">
                    <div className="flex flex-col gap-3 bg-black/20 p-4 rounded-xl border border-white/5">
                        <div className="flex items-center gap-3 text-white/90">
                            <CalendarDays className="h-4 w-4 text-white/50" />
                            <div className="flex flex-col">
                                <span className="text-[10px] uppercase tracking-wider text-white/50 font-semibold mb-[2px]">Ida</span>
                                <span className="font-medium text-sm">{report.start_date}</span>
                            </div>
                        </div>
                        <div className="h-[1px] w-full bg-white/10"></div>
                        <div className="flex items-center gap-3 text-white/90">
                            <CalendarDays className="h-4 w-4 text-white/50" />
                            <div className="flex flex-col">
                                <span className="text-[10px] uppercase tracking-wider text-white/50 font-semibold mb-[2px]">Volta</span>
                                <span className="font-medium text-sm">{report.end_date}</span>
                            </div>
                        </div>
                    </div>
                </CardContent>

                <CardFooter className="pt-2 pb-6 px-6 relative z-10">
                    <Button 
                        className="w-full bg-white text-black hover:bg-blue-50 font-bold transition-all shadow-lg hover:shadow-xl group-hover:scale-[1.03]"
                        onClick={() => handleView(report)}
                    >
                        <Eye className="w-4 h-4 mr-2" /> Reviver Viagem
                    </Button>
                </CardFooter>
            </Card>
            ))}
        </div>
      </div>
    </div>
  );
};

export default MyReports;