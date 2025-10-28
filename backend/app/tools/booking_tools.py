from typing import List, Dict

def confirm_booking(flight_details: Dict, hotel_details: Dict, activity_details: List[Dict], user_info: Dict) -> Dict:
    print(f"Confirmando reserva para {user_info.get('name', 'Usuário')}...")
    print("Detalhes do Voo:", flight_details)
    print("Detalhes do Hotel:", hotel_details)
    print("Detalhes das Atividades:", activity_details)

    booking_id = f"BKNG_{random.randint(10000, 99999)}"
    print(f"Reserva {booking_id} simulada com sucesso.")
    return {"status": "success", "booking_id": booking_id, "message": "Reserva confirmada com sucesso!"}

def process_payment(payment_info: Dict, amount: float) -> Dict:
    card_number = payment_info.get('card_number', '**** **** **** ****')
    last_digits = card_number[-4:] if len(card_number) >= 4 else "****"
    print(f"Processando pagamento de R$ {amount:.2f} para o cartão terminado em {last_digits}...")

    transaction_id = f"PAY_{random.randint(100000, 999999)}"
    print(f"Pagamento {transaction_id} simulado com sucesso.")
    return {"status": "success", "transaction_id": transaction_id, "message": "Pagamento processado com sucesso!"}

import random # Adicionado para gerar IDs aleatórios