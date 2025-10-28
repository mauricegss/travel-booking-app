import { FlightCardProps } from "@/components/FlightCard";
import { HotelCardProps } from "@/components/HotelCard";
import { ActivityCardProps } from "@/components/ActivityCard";

// Define interfaces parciais baseadas nas props dos cards,
// assumindo que os dados da API correspondem (ajuste se necessário)
interface ApiFlight extends Omit<FlightCardProps, 'onSelect'> {}
interface ApiHotel extends Omit<HotelCardProps, 'onSelect'> {}
interface ApiActivity extends Omit<ActivityCardProps, 'onSelect'> {}


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