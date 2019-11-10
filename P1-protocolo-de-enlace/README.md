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

#### Emulador de link serial

O programa serialemu emula um link serial com determinada taxa de bits, BER e atraso de propagação. Para usá-lo siga as seguintes instruções:

1. Descompacte o arquivo Serialemu.zip, e entre no subdiretório Serialemu.

2. Compile-o com este comando:

```
make
```

3. Copie o programa compilado para algum subdiretório mais conveniente, por exemplo, `/home/usuario`, e depois mude para esse subdiretório:

```
cp -a dist/Debug/GNU-Linux/serialemu /home/usuario/
cd /home/usuario
```

4. Execute-o de forma que ele apresente suas opções de execução:
```
./serialemu -h

Uso: ./serialemu [-b BER][-a atraso][-f][-B taxa_bits] | -h
 
BER: taxa de erro de bit, que deve estar no intervalo  [0,1]
atraso: atraso de propagação, em milissegundos.
taxa_bits: taxa de bits em bits/segundo
-f: executa em primeiro plano (nao faz fork)
```

5. Execute-o então da forma desejada, selecionando a taxa de bits (default: ilimitada), BER (default: 0) e atraso de propagação (default: 0). O serialemu automaticamente vai para segundo plano (daemonize), liberando o terminal. Ex:

```
./serialemu -B 9600

/dev/pts/17 /dev/pts/2
```

Anote os dois caminhos informados pelo serialemu: eles são as duas portas seriais que correspondem às pontas do link serial emulado.

6. Execute o protocolo usando essas portas virtuais caso utilize o cenário com uma FakeLayer.