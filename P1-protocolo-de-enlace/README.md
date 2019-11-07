**Instituto Federal de Santa Catarina**

# Projeto de Protocolos

Primeiro projeto da disciplina de Projeto de Protocolos (PTC29008) do curso de Engenharia de Telecomunicações do Instituto Federal de Santa Catarina - câmpus São José, realizada em 2019.2.

##### Equipe:

- [Ameliza Souza Corrêa](https://github.com/ameliza)
- [Luiza Alves da Silva](https://github.com/luizaalves)
- [Yan Lucas Martins](https://github.com/yanmartins)

## Protocolo de enlace

Consiste em um protocolo que visa estabelecer enlaces ponto-a-ponto entre dois computadores.

#### Serviços implementados

- Integração com subsistema de rede do Linux
- Enquadramento (Sentinela)
- Controle de erros
- Garantia de entrega
- Controle de acesso ao meio (Slotted Aloha)
- Gerenciamento de sessão

### Manual do Projeto

#### Emulador de link serial

O programa serialemu emula um link serial com determinada taxa de bits, BER e atraso de propagação. Para usá-lo deve-se seguir as instuções contidas em: [serialemu](https://wiki.sj.ifsc.edu.br/wiki/index.php/PTC29008:_Projeto_1:_um_protocolo_de_comunicação#Emulador_de_link_serial)

#### Executando o protocolo

Para executar o protocolo é necessário usar o interpretador `python3`, e executar o arquivo `protocolo.py`. Além disso, é
obrigatório informar o caminho da serial utilizada com o comando `--serial /dev/XXX`. Este caminho pode ser obtido através dos passos vistos na seção *Emulador de link serial*. Portanto, insira no terminal Linux a seguinte instrução:

`sudo python3 protocolo.py --serial /dev/XXX`

O protocolo tem suporte à algumas opções, dentre elas a `--fakelayer`, esta que substitui o uso de uma interface *tun*.
Caso esta seja a sua opção, utilize a instrução a seguir:

`python3 protocolo.py --serial /dev/XXX --fakelayer`

Outras opções podem ser vistas através do comando `-h`, o qual exibe as demais opções suportadas:

``` 
Uso: ./protocolo --serial /dev/XXX [opções]

Uso obrigatório:

--serial /dev/XXX:   caminho da serial

Opções:
-h:                  mostra esta ajuda
--fakelayer:         usa o terminal para enviar e receber dados, ao invés da interface tun
--maxretries n:      limite de retransmissões do ARQ (default: 3)
--arqtimeout t:      tempo de espera por ACK no ARQ, em segundos (default: 1)
--idsessao id:       número de identificação de sessão (default: 2)
```

Todas as demais opções não são de uso obrigatório, elas possuem um valor pré-definido que será utilizado durante a execução.
