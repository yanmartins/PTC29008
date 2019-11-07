import poller

class Layer(poller.Callback):
    '''
    Classe Layer, que deve ser implementada por todas
    as subcamadas do protocolo
    '''

    def __init__(self, obj, tout=0):
        '''
        Construtor onde são definidos as camadas superior e inferior
        '''
        poller.Callback.__init__(self, obj, tout)
        self.upper = None
        self.lower = None

    def set_upper(self, upper):
        '''
        Define camada superior
        :param upper: objeto da camada superior
        '''
        self.upper = upper

    def set_lower(self, lower):
        '''
        Define camada inferior
        :param lower: objeto da camada inferior
        '''
        self.lower = lower

    def handle(self):
        pass

    def handle_timeout(self):
        pass

    def envia(self, data):
        '''
        Mensagens que são recebidas da camada superior
        :param data: mensagem a ser tratada
        '''
        pass

    def notifica(self, data):
        '''
        Mensagens que são recebidas da camada inferior
        :param data: mensagem a ser tratada
        '''
        pass

    def notifica_erro(self):
        '''
        Informa a camada superior que um erro fatal
        ocorreu em sua camada inferior
        '''
        pass

    def disable_all_upper(self):
        '''
        Desabilita o monitoramento do obejto Callback de todas
        as camadas superiores
        '''
        self.disable()
        if not self.upper == None:
            self.upper.disable_all_upper()

    def enable_all_upper(self):
        '''
        Habilita o monitoramento do obejto Callback de todas
        as camadas superiores
        '''
        self.enable()
        if not self.upper == None:
            self.upper.enable_all_upper()