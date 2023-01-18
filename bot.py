import os
import json
import logging

from dotenv import load_dotenv
load_dotenv()

import telebot

import api_linketrack




### DIRETÓRIO  ###
diretorio_completo = os.path.realpath(__file__)
diretorio = os.path.dirname(diretorio_completo)

### TEXTOS ###
with open(diretorio + "/textos.json", "r", encoding="utf-8") as _:
	TEXTOS = json.load(_)

### BOT ###
BOT_TOKEN = os.environ.get("BOT_TOKEN")
assert BOT_TOKEN, "TOKEN do bot não foi definido."
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="html")
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)



### COMANDO START ###

# Responder
@bot.message_handler(commands=["start"])
def responder_start(mensagem):
	nome = telebot.util.escape(mensagem.from_user.first_name)
	texto = TEXTOS["inicio"].format(nome)
	bot.reply_to(
		message=mensagem,
		text=texto
	)

		
	
	
### COMANDO RASTREAR ###

# Menu
def menu_rastrear(usuario_id, codigo, retorno):
	menu = [
		[
			telebot.types.InlineKeyboardButton(
				"🗑 Apagar",
				callback_data=f"apagar {usuario_id}"
			)
		]
	]
	if retorno:
		menu[0].append(
			telebot.types.InlineKeyboardButton(
				"↕️ Expandir",
				callback_data=f"informacoes_completas {usuario_id} {codigo}"
			)
		)
	return telebot.types.InlineKeyboardMarkup(menu)
	

# Responder
@bot.message_handler(commands=["rastrear"])
def responder_rastrear(mensagem):
	args = mensagem.text.strip().split(" ")
	args = list(filter(None, args))
	if len(args) != 2:
		bot.reply_to(
			message=mensagem,
			text="Por favor envie o comando da seguinte forma: <code><i>/rastrear codigo</i></code>\n\n<b>Exemplo:</b> <code>/rastrear LX002249507BR</code>"
		)
	else:
		codigo = args[1]
		informacoes = api_linketrack.obter_informacoes(codigo)
		if not informacoes["retorno"]:
			texto = informacoes["mensagem"]
		else:
			conteudo = informacoes["conteudo"]
			texto = TEXTOS["informacoes_resumo"].format(
				conteudo["codigo"],
				conteudo["servico"],
				conteudo["eventos"][0]["data"],
				conteudo["eventos"][0]["hora"],
				conteudo["eventos"][0]["local"],
				conteudo["eventos"][0]["status"]
			)
		bot.reply_to(
			message=mensagem,
			text=texto,
			reply_markup=menu_rastrear(
				usuario_id=mensagem.from_user.id,
				codigo=codigo,
				retorno=informacoes["retorno"]
			)
		)
		
		
# Apagar a mensagem
@bot.callback_query_handler(func=lambda _:_.data.startswith("apagar"))
def apagar_mensagem(resposta):
	args = resposta.data.split(" ")
	dono = int(args[1])
	if dono == resposta.from_user.id:
		bot.delete_message(
			chat_id=resposta.message.chat.id,
			message_id=resposta.message.message_id
		)
	
	
# Exibir informações completas
@bot.callback_query_handler(func=lambda _:_.data.startswith("informacoes_completas"))
def informacoes_completas(resposta):
	args = resposta.data.split(" ")
	dono = int(args[1])
	codigo = args[2]
	if dono == resposta.from_user.id:
		informacoes = api_linketrack.obter_informacoes(codigo)
		if not informacoes["retorno"]:
			texto = informacoes["mensagem"]
		else:
			conteudo = informacoes["conteudo"]
			texto = TEXTOS["informacoes_resumo"].format(
				conteudo["codigo"],
				conteudo["servico"],
				conteudo["eventos"][0]["data"],
				conteudo["eventos"][0]["hora"],
				conteudo["eventos"][0]["local"],
				conteudo["eventos"][0]["status"]
			)
			if len(conteudo["eventos"]) > 1:
				texto += "\n\n\n<b><u>ATUALIZAÇÕES ANTERIORES</u></b>"
				for e in conteudo["eventos"][1:]:
					texto += "\n\n• <b>Data:</b> {}\n• <b>Hora:</b> {}\n• <b>Local:</b> {}\n• <b>Status:</b> {}".format(
						e["data"],
						e["hora"],
						e["local"],
						e["status"]
					)
		bot.edit_message_text(
			text=texto,
			chat_id=resposta.message.chat.id,
			message_id=resposta.message.message_id,
			reply_markup=menu_rastrear(
				usuario_id=resposta.from_user.id,
				codigo=None,
				retorno=False
			)
		)
		
		
		
		
### COMANDO CÓDIGO FONTE ###

# Responder
@bot.message_handler(commands=["codigo_fonte"])
def codigo_fonte(mensagem):
	bot.send_message(
		chat_id=mensagem.from_user.id,
		text="Para mais informações acesse: https://github.com/KingRotiv/RastreiaAiBot"
	)
	
	
	
	
### INCIANDO BOT ###
if __name__ == "__main__":
	bot.infinity_polling()