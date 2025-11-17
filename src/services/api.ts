// --- DEFINIÇÕES DOS DADOS BRUTOS (com image_url) ---

export interface ApiFlight {
  id: string;       
  airline: string;  
  departure: string;
  arrival: string;  
  duration: string; 
  price: string;    
  stops: number;    
  image_url: string | null; // <-- NOVO
}

export interface ApiHotel {
  id: string;       
  name: string;     
  location: string; 
  rating: number;   
  price: string;    
  amenities: string[];
  image_url: string | null; // <-- NOVO
}

export interface ApiActivity {
  id: string;         
  title: string;      
  description: string;
  duration: string;   
  price: string;      
  capacity: string;   
  image_url: string | null; // <-- NOVO
}

// --- DEFINIÇÕES DO NOVO RELATÓRIO CURADO ---

export interface CuratedRecommendation<T> {
  data: T; // T será ApiFlight, ApiHotel, ou ApiActivity
  justification: string;
}

export interface FinalReport {
  summary_text: string;
  curated_flights: CuratedRecommendation<ApiFlight>[];
  curated_hotels: CuratedRecommendation<ApiHotel>[];
  curated_activities: CuratedRecommendation<ApiActivity>[];
  closing_text: string;
}

// --- A RESPOSTA FINAL DA API ---

export interface TripDataResponse {
  final_report: FinalReport | null;
  destination: string | null;
  start_date: string | null;
  end_date: string | null;
  error: string | null;
}

// A função de fetch permanece a MESMA
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