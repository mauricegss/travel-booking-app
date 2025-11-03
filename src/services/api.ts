// As props dos cards agora são diferentes.
// Vamos criar interfaces simples para os resultados da busca.

interface WebSearchResult {
  id: string;       // No nosso caso, esta será a URL
  title: string;    // O título da página
  description: string; // O snippet da busca
  source: string;   // O domínio (ex: tripadvisor.com)
  price: string;    // O texto (ex: "Verificar no site")
}

// Mapeamos as props dos cards para esta nova interface genérica
// (Note que os nomes das props nos cards antigos não batem 100% com os da Tavily,
// por isso adaptamos no backend e aqui)

// Para FlightCard
export interface ApiFlight {
  id: string;       // url
  airline: string;  // source (ex: skyscanner.com)
  departure: string; // "N/A"
  arrival: string;   // "N/A"
  duration: string;  // title
  price: string;     // "Verificar no site"
  stops: number;     // 0
}

// Para HotelCard
export interface ApiHotel {
  id: string;       // url
  name: string;     // title
  location: string; // source
  rating: number;   // 0
  price: string;    // "Verificar no site"
  amenities: string[]; // [description]
}

// Para ActivityCard
export interface ApiActivity {
  id: string;         // url
  title: string;      // title
  description: string; // description
  duration: string;   // "N/A"
  price: string;      // "Verificar no site"
  capacity: string;   // source
}


export interface TripDataResponse {
  flights: ApiFlight[] | null;
  hotels: ApiHotel[] | null;
  activities: ApiActivity[] | null;
  itinerary: string;
  destination: string | null;
  start_date: string | null;
  end_date: string | null;
  error: string | null;
}

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