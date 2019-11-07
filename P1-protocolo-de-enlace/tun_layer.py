#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import layer

class TunLayer(layer.Layer):
    '''
    Classe TunLayer, responsável por garantir a integração com o subsistema
    de rede linux criando interfaces de rede tun.
    '''

    # Campo ID Proto
    id_proto_ipv4 = 0x800
    id_proto_ipv6 = 0x866d

    def __init__(self, tun):
        '''
        Cria um objeto TunLayer.
        :param obj: objeto tun que será monitorado pelo poller
        '''
        layer.Layer.__init__(self, tun.fd)

        self.upper = None  # Camada superior
        self.lower = None  # Camada inferior

        self.enable()  			# Ativa o monitoramento do objeto
        self.disable_timeout()  # Desativa o Timeout

        self._tun = tun

    def handle(self):
        '''
        Monitora a interface tun criada.
        '''
        proto, dados = self._tun.get_frame()
        self.envia(dados)

    def envia(self, data):
        '''
        Envia os dados lidos da interface tun
        para a subcamada inferior (Sessão).
        :param data: Mensagem lida
        '''
        self.lower.envia(data)

    def notifica(self, data):
        '''
        Envia as mensagens vindas da camada inferior (Sessão) pela interface tun.
        :param data: Mensagem recebida
        '''
        self._tun.send_frame(data, self.id_proto_ipv4)