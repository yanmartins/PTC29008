## Introdução

- canal
- hello
- if
- pare-e-espere


## Exercícios de introdução

- ex1: produtor e consumidor.
- ex2: dois produtores e um consumidor.
- ex3: protocolo pare-e-espere livre de erros.
- ex4: protocolo pare-e-espere ambiente com erros (perda de mensagens, retransmissões e descarte de mensagens duplicadas).
- ex6: modelo para o enquadramento que foi implementado no protocolo ponto-a-ponto (Projeto 1).

## Exercícios de propriedades

-

## Verificação de condições (assertions)

A verificação de uma condição pode ser feita com o comando assert. Esse comando verifica se uma expressão avalia para verdadeiro e, caso contrário, interrompe a execução do programa. Isso pode ser usado para a verificação pontual de uma propriedade do sistema.

Para verificar condições em um modelo, deve-se compilá-lo da seguinte forma:

```
# opção -a: usada para gerar um verificador, que estará no arquivo pan.c
./spin -a djikstra.pml
 
# Compila o verificador, que será o programa "pan"
gcc -o pan pan.c
 
# Executa o verificador
./pan
```


## Methods

DNP (NP = No progress)