// --- DEFINIÇÕES DOS DADOS BRUTOS ---

export interface ApiFlight {
  id: string;       
  airline: string;  
  departure: string;
  arrival: string;  
  duration: string; 
  price: string;    
  stops: number;    
  image_url: string | null;
}

export interface ApiHotel {
  id: string;       
  name: string;     
  location: string; 
  rating: number;   
  price: string;    
  amenities: string[];
  image_url: string | null;
}

export interface ApiActivity {
  id: string;         
  title: string;      
  description: string;
  duration: string;   
  price: string;      
  capacity: string;   
  image_url: string | null;
}

// --- DEFINIÇÕES DO RELATÓRIO CURADO ---

export interface CuratedRecommendation<T> {
  data: T; 
  justification: string;
}

export interface FinalReport {
  summary_text: string;
  curated_flights: CuratedRecommendation<ApiFlight>[];
  curated_hotels: CuratedRecommendation<ApiHotel>[];
  curated_activities: CuratedRecommendation<ApiActivity>[];
  closing_text: string;
}

export interface TripDataResponse {
  final_report: FinalReport | null;
  destination: string | null;
  start_date: string | null;
  end_date: string | null;
  error: string | null;
}

// --- HELPER DE AUTH ---
const getAuthHeader = () => {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// --- FUNÇÕES DA API ---

// 1. Planejamento de Viagem (Público)
export const planTrip = async (user_request: string): Promise<TripDataResponse> => {
  const response = await fetch("http://127.0.0.1:8000/plan-trip", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_request }),
  });

  if (!response.ok) {
     const errorData = await response.json().catch(() => ({ detail: "Erro desconhecido na API" }));
     console.error("Erro da API:", errorData);
     throw new Error(errorData.detail || "Falha ao planejar a viagem");
  }

  return response.json();
};

// 2. Login
export const loginUser = async (email: string, password: string) => {
  const formData = new FormData();
  formData.append("username", email); // OAuth2 espera 'username'
  formData.append("password", password);

  const response = await fetch("http://127.0.0.1:8000/token", {
    method: "POST",
    body: formData,
  });
  if (!response.ok) throw new Error("Login falhou");
  return response.json();
};

// 3. Cadastro
export const registerUser = async (email: string, password: string) => {
  const response = await fetch("http://127.0.0.1:8000/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) throw new Error("Cadastro falhou");
  return response.json();
};

// 4. Salvar Relatório
export const saveReport = async (data: { destination: string, start_date: string, end_date: string, content: FinalReport }) => {
  const response = await fetch("http://127.0.0.1:8000/reports", {
    method: "POST",
    headers: { 
        "Content-Type": "application/json",
        ...getAuthHeader() 
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Erro ao salvar relatório");
  return response.json();
};

// 5. Listar Relatórios
export const getReports = async () => {
  const response = await fetch("http://127.0.0.1:8000/reports", {
    headers: { ...getAuthHeader() },
  });
  if (!response.ok) throw new Error("Erro ao buscar relatórios");
  return response.json();
};

// 6. Deletar Relatório
export const deleteReport = async (id: number) => {
  const response = await fetch(`http://127.0.0.1:8000/reports/${id}`, {
    method: "DELETE",
    headers: { ...getAuthHeader() },
  });
  if (!response.ok) throw new Error("Erro ao deletar");
  return response.json();
};