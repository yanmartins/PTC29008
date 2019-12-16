**Instituto Federal de Santa Catarina**

# Projeto de Protocolos

Segundo projeto da disciplina de Projeto de Protocolos (PTC29008) do curso de Engenharia de Telecomunicações do Instituto Federal de Santa Catarina - câmpus São José, realizada em 2019.2.

## Protocolo de aplicação


#### Aplicação de demosntração

A aplicação foi desenvolvida em **Python 3**, a qual simula a coleta de amostras de diferentes sensores, e os envia para o servidor no formato do protocolo **CoAP**, com o campo payload seguindo os padrões do **Protocol Buffers**.

#### Instruções para execução

Em um primeiro terminal, execute:

```
python3 coaps.py
```

Em outro terminal, execute:

```
python3 sensorapp.py
```

Num terceiro, execute a aplicação:

```
python3 coletor.py
```

#### Implementação do CoAP para o lado cliente

Inicialmente é enviada uma mensagem de configuração para o servidor. Contendo período, nome da placa e lista de sensores.

```
|      |
+----->|     Header: POST (T=CON, Code=0.02, MID=0x7d40)
| GET  |      Token: 0x75
|      |   Uri-Path: "ptc"
|      |    Payload: "configuração"
|      |
|<-----+     Header: 2.01 Created (T=ACK, Code=2.01, MID=0x7d40)
| 2.01 |      Token: 0x75
|      |   Uri-Path: "ptc"
|      |    Payload: "configuração"
|      |
```

Após a confirmação da configuração, então, incia-se o envio das amostras:

```
|      |
+----->|     Header: POST (T=CON, Code=0.02, MID=0x8d42)
| GET  |      Token: 0x12
|      |   Uri-Path: "ptc"
|      |    Payload: "amostras"
|      |
|<-----+     Header: 2.03 Valid (T=ACK, Code=2.03, MID=0x8d42)
| 2.03 |      Token: 0x12
|      |   Uri-Path: "ptc"
|      |    
```

Essa implementação pode ser observada em: `coap.py`