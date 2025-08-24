import os
import telebot
from telebot import types
import math

# Configuración del bot para Render
TOKEN = os.environ.get('BOT_TOKEN', '7946242296:AAGv-F3mla-yorBl7v8gNaKk1VhcCl4TIz0')
bot = telebot.TeleBot(TOKEN)

# Estados del usuario
user_states = {}

# Precios por material
PRECIOS = {
    "OA": 180000,
    "OR": 180000,
    "OB": 190000,
    "Pt": 190000
}

def calcular_presupuesto(talla, espesor, material, corte):
    peso_base = talla * 0.1 * espesor
    
    if corte == "Clasico":
        peso_final = math.floor(peso_base)
    else:
        peso_final = math.ceil(peso_base)
    
    if material == "OB":
        peso_final += 1
    elif material == "Pt":
        peso_final += 2
    
    precio = peso_final * PRECIOS[material]
    return peso_final, precio

def crear_menu_material():
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("OA (Oro Amarillo)", callback_data="material_OA"),
        types.InlineKeyboardButton("OR (Oro Rojo)", callback_data="material_OR")
    )
    markup.row(
        types.InlineKeyboardButton("OB (Oro Blanco)", callback_data="material_OB"),
        types.InlineKeyboardButton("Pt (Platino)", callback_data="material_Pt")
    )
    return markup

def crear_menu_corte():
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Clasico", callback_data="corte_Clasico"),
        types.InlineKeyboardButton("Ingles", callback_data="corte_Ingles")
    )
    markup.row(
        types.InlineKeyboardButton("Almendra", callback_data="corte_Almendra"),
        types.InlineKeyboardButton("Plano", callback_data="corte_Plano")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = """
Bienvenido al Bot de Presupuesto de Argollas de Matrimonio!

Este bot te ayudara a calcular el presupuesto de tus argollas.

Para comenzar, envia /presupuesto

Comandos disponibles:
/presupuesto - Calcular nuevo presupuesto
/ayuda - Ver esta ayuda
"""
    bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(commands=['presupuesto'])
def iniciar_presupuesto(message):
    user_id = message.from_user.id
    user_states[user_id] = {
        'paso': 'anillo1_talla',
        'anillo1': {},
        'anillo2': {}
    }
    bot.send_message(message.chat.id, "Ingresa la talla del primer anillo (ejemplo: 18):")

@bot.message_handler(commands=['ayuda'])
def ayuda(message):
    help_text = """
Guia de uso:

1. Envia /presupuesto para comenzar
2. El bot te preguntara por cada anillo:
   - Talla (ej: 18, 19, 20)
   - Espesor (ej: 2.5, 3.0)
   - Material (OA, OR, OB, Pt)
   - Tipo de corte (Clasico, Ingles, Almendra, Plano)

3. El bot calcula automaticamente el presupuesto

Tip: Los precios son por gramo:
- OA/OR: $180,000
- OB/Pt: $190,000
"""
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(func=lambda message: True)
def procesar_mensaje(message):
    user_id = message.from_user.id
    
    if user_id not in user_states:
        bot.send_message(message.chat.id, "Envia /presupuesto para comenzar")
        return
    
    estado = user_states[user_id]
    paso = estado['paso']
    
    try:
        if paso == 'anillo1_talla':
            talla = float(message.text)
            if talla <= 0:
                bot.send_message(message.chat.id, "La talla debe ser mayor a 0. Intenta de nuevo:")
                return
            
            estado['anillo1']['talla'] = talla
            estado['paso'] = 'anillo1_espesor'
            bot.send_message(message.chat.id, f"Talla del primer anillo: {talla}\n\nAhora ingresa el espesor (ejemplo: 2.5):")
            
        elif paso == 'anillo1_espesor':
            espesor = float(message.text)
            if espesor <= 0:
                bot.send_message(message.chat.id, "El espesor debe ser mayor a 0. Intenta de nuevo:")
                return
            
            estado['anillo1']['espesor'] = espesor
            estado['paso'] = 'anillo1_material'
            bot.send_message(message.chat.id, f"Espesor del primer anillo: {espesor}\n\nSelecciona el material:", reply_markup=crear_menu_material())
            
        elif paso == 'anillo1_corte':
            estado['paso'] = 'anillo2_talla'
            bot.send_message(message.chat.id, "Primer anillo configurado.\n\nAhora ingresa la talla del segundo anillo (ejemplo: 18):")
            
        elif paso == 'anillo2_talla':
            talla = float(message.text)
            if talla <= 0:
                bot.send_message(message.chat.id, "La talla debe ser mayor a 0. Intenta de nuevo:")
                return
            
            estado['anillo2']['talla'] = talla
            estado['paso'] = 'anillo2_espesor'
            bot.send_message(message.chat.id, f"Talla del segundo anillo: {talla}\n\nAhora ingresa el espesor (ejemplo: 2.5):")
            
        elif paso == 'anillo2_espesor':
            espesor = float(message.text)
            if espesor <= 0:
                bot.send_message(message.chat.id, "El espesor debe ser mayor a 0. Intenta de nuevo:")
                return
            
            estado['anillo2']['espesor'] = espesor
            estado['paso'] = 'anillo2_material'
            bot.send_message(message.chat.id, f"Espesor del segundo anillo: {espesor}\n\nSelecciona el material:", reply_markup=crear_menu_material())
            
        elif paso == 'anillo2_corte':
            calcular_presupuesto_final(message, user_id)
            
    except ValueError:
        bot.send_message(message.chat.id, "Por favor ingresa un numero valido. Intenta de nuevo:")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    
    if user_id not in user_states:
        bot.answer_callback_query(call.id, "Sesion expirada. Envia /presupuesto para comenzar")
        return
    
    estado = user_states[user_id]
    paso = estado['paso']
    
    if call.data.startswith('material_'):
        material = call.data.replace('material_', '')
        if paso == 'anillo1_material':
            estado['anillo1']['material'] = material
            estado['paso'] = 'anillo1_corte'
            bot.edit_message_text(
                f"Material del primer anillo: {material}\n\nSelecciona el tipo de corte:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=crear_menu_corte()
            )
        elif paso == 'anillo2_material':
            estado['anillo2']['material'] = material
            estado['paso'] = 'anillo2_corte'
            bot.edit_message_text(
                f"Material del segundo anillo: {material}\n\nSelecciona el tipo de corte:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=crear_menu_corte()
            )
    
    elif call.data.startswith('corte_'):
        corte = call.data.replace('corte_', '')
        if paso == 'anillo1_corte':
            estado['anillo1']['corte'] = corte
            estado['paso'] = 'anillo2_talla'
            bot.send_message(
                call.message.chat.id,
                f"Corte del primer anillo: {corte}\n\nAhora ingresa la talla del segundo anillo (ejemplo: 18):"
            )
        elif paso == 'anillo2_corte':
            estado['anillo2']['corte'] = corte
            calcular_presupuesto_final(call.message, user_id)
    
    bot.answer_callback_query(call.id)

def calcular_presupuesto_final(message, user_id):
    estado = user_states[user_id]
    anillo1 = estado['anillo1']
    anillo2 = estado['anillo2']
    
    peso1, precio1 = calcular_presupuesto(
        anillo1['talla'], 
        anillo1['espesor'], 
        anillo1['material'], 
        anillo1['corte']
    )
    
    peso2, precio2 = calcular_presupuesto(
        anillo2['talla'], 
        anillo2['espesor'], 
        anillo2['material'], 
        anillo2['corte']
    )
    
    peso_total = peso1 + peso2
    precio_total = precio1 + precio2
    
    resumen = f"""
PRESUPUESTO FINAL

Anillo 1:
• Talla: {anillo1['talla']}
• Espesor: {anillo1['espesor']}
• Material: {anillo1['material']}
• Corte: {anillo1['corte']}
• Peso: {peso1:.2f}g
• Precio: ${precio1:,.0f}

Anillo 2:
• Talla: {anillo2['talla']}
• Espesor: {anillo2['espesor']}
• Material: {anillo2['material']}
• Corte: {anillo2['corte']}
• Peso: {peso2:.2f}g
• Precio: ${precio2:,.0f}

TOTAL: ${precio_total:,.0f}
Peso total: {peso_total:.2f}g

Para calcular otro presupuesto, envia /presupuesto
"""
    
    bot.send_message(message.chat.id, resumen)
    del user_states[user_id]

if __name__ == "__main__":
    print("Bot iniciado en Render...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error: {e}")