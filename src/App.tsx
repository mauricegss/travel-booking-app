import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Index from "./pages/Index";
import SearchResults from "./pages/SearchResults";
import NotFound from "./pages/NotFound";
import Login from "./pages/Login";
import MyReports from "./pages/MyReports";

const queryClient = new QueryClient();

// Componente simples para proteger rotas privadas
const PrivateRoute = ({ children }: { children: JSX.Element }) => {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/" replace />;
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          {/* A rota raiz agora é o Login */}
          <Route path="/" element={<Login />} />
          
          {/* Rotas Protegidas (Home e Relatórios) */}
          <Route 
            path="/home" 
            element={
              <PrivateRoute>
                <Index />
              </PrivateRoute>
            } 
          />
          <Route 
            path="/search-results" 
            element={
              <PrivateRoute>
                <SearchResults />
              </PrivateRoute>
            } 
          />
          <Route 
            path="/my-reports" 
            element={
              <PrivateRoute>
                <MyReports />
              </PrivateRoute>
            } 
          />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;