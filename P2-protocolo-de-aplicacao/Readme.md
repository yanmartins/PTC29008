**Instituto Federal de Santa Catarina**

# Projeto de Protocolos

Segundo projeto da disciplina de Projeto de Protocolos (PTC29008) do curso de Engenharia de Telecomunicações do Instituto Federal de Santa Catarina - câmpus São José, realizada em 2019.2.

## Protocolo de aplicação


### Implementação

A aplicação `coap_client.py`, permite realizar os métodos:__
- GET
- POST

A seguir é exibido o formato do quadro de uma mensagem CoAP.

![Mesage format](https://github.com/yanmartins/PTC29008/blob/master/P2-protocolo-de-aplicacao/imagens/message_format_coap.png)

A partir da tabela acima, temos que a quantidade de bits por campo é:

Campo   | Número de bits
--------- | ------
Versão (Ver)| 2
Tipo (T)| 2
Tamanho do token (TKL) | 4
Código | 8
ID da Mensagem | 16