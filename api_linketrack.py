import os
import requests




# Requisitar informações
def obter_informacoes(codigo):
	url = "https://api.linketrack.com/track/json"
	usuario = os.environ.get("USUARIO_LINKETRACK")
	assert usuario, "Nome de usuário não definido."
	token = os.environ.get("TOKEN_LINKETRACK")
	assert token, "TOKEN do usuário não definido."
	
	dados = {
		"user": usuario,
		"token": token,
		"codigo": codigo
	}
	resposta = requests.get(url=url, params=dados)
	if resposta.status_code == 200:
		informacoes = resposta.json()
		if informacoes["quantidade"] == 0:
			return {
				"retorno": False,
				"mensagem": "Pacote sem atualizações."
			}
		else:
			return {
				"retorno": True,
				"conteudo": informacoes
			}
	elif resposta.status_code == 401:
		return {
			"retorno": False,
			"mensagem": "Código invalido."
		}
	else:
		return {
			"retorno": False,
			"mensagem": "Algo deu errado! Tente mais tarde."
		}