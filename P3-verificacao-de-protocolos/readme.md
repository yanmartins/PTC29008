**Instituto Federal de Santa Catarina**

# Projeto de Protocolos

Terceiro projeto da disciplina de Projeto de Protocolos (PTC29008) do curso de Engenharia de Telecomunicações do Instituto Federal de Santa Catarina - câmpus São José, realizada em 2019.2.

## Verificação de Protocolos

Serão verificadas as seguintes FSM do protocolo desenvolvido no projeto 1:

- **Sessão desconexão:** término de sessão eventualmente será concluído para ambas as partes
- **Sessão conexão:** duas entidades são capazes de estabelecerem uma sessão, independente de qual delas iniciar a sessão
- **ARQ:** eventualmente, transmissor de um quadro sabe se sua entrega teve sucesso
- **Enquadramento:** Perdas de sincronismo no enquadramento são recuperadas em algum momento futuro

## Geração do verificador

A geração do verificador deve ser feita com os comandos a seguir:

```
spin -a modelo.pml
gcc -o pan pan.c
```

Por fim, deve-se executá-lo desta form:

```
./pan -a
```