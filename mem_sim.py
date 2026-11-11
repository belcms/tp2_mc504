import collections


# funcionamento TBL e memoria virtual com substituicao de paginas
# metodos de substituicao: LRU e SecondChance


class MemorySimulator:
    def __init__(self, page_size, num_tlb_entries, num_frames, rep_policy):
        self.page_size = page_size # tam pag em bytes; pot 2
        self.num_tlb_entries = num_tlb_entries # Num de entradas na TLB (recomendado maior que 16) ; pot 2
        self.num_frames = num_frames  # Num de quadros na memoria fisica ; pot 2
        self.rep_policy = rep_policy # Politica de substituicao de paginas (LRU ou SecondChance)

        self.lru_frames = []

        if rep_policy not in ['LRU', 'SecondChance']:
            raise ValueError("Política de substituição inválida. Use 'LRU' ou 'SecondChance'.")

        self.tlb = []  # pode ser lista de tuplas (page number, frame number) ou OrderedDict para facilitar LRU
        self.page_table = {}  # mapeia {page number -> frame number}
        self.frames = [None] * num_frames # memoria fisica simulada, array que armazena qual pag esta em cada quadro

        # contadores de estatisticas
        self.tlb_hits = 0 # num acertos TLB
        self.tlb_misses = 0 # num faltas TLB --> valor eh carregado na TLB para que o prox acesso seja mais rapido
        self.page_faults = 0 # num page faults -> n ta no frame

# Observacao: A politica de substituicao da TLB eh obrigatoriamente LRU. 
# O parametro rep_policy eh apenas para substituicao em caso de tratamento de page fault. Alem disso, assuma que todos os enderecos de entrada pertencem ao espaco de enderecamento do processo.


    def access_memory(self, virtual_address):
        """
        Simula o acesso a um endereço virtual.
        Deve atualizar os contadores e aplicar a política de substituição se necessário.
        """
        pg = virtual_address // self.page_size


        for i in range(len(self.tlb)): #verifica todo o tlb para ver se a pg está
            if pg == self.tlb[i][0]:
                self.tlb_hits += 1
                pg_tlb, frame_tlb = self.tlb.pop(i)
                self.tlb.append((pg_tlb, frame_tlb)) 
                end_fisico = self.calcula_end_fisico(virtual_address, frame_tlb)
                self.lru_frames.remove(pg)
                self.lru_frames.append(pg)
                return end_fisico #conferir se calculo do end fisico está correto

        self.tlb_misses += 1  # se chegou aqui é pq a pg n está na TLB

        if pg in self.page_table: # pg está na tabela de paginas
            end_fisico = self.calcula_end_fisico(virtual_address, self.page_table[pg])
            self.lru_frames.remove(pg)
            self.lru_frames.append(pg)
        else:
            self.page_faults += 1 #se não está na tabela de pgs ocorre um page fault
            self.alocacao_frame(pg)
            end_fisico = self.calcula_end_fisico(virtual_address, self.page_table[pg])
        self.insercao_tlb(pg, self.page_table[pg])
        return end_fisico
            

    def calcula_end_fisico(self, virtual_address, frame):
        # confirmar: pega o virtual adress, divide pelo page_size, acha a pg, ai acessa TLB, se n tiver LRU na TLB
        deslocamento = virtual_address % self.page_size
        end_fisico = frame * self.page_size + deslocamento
        return end_fisico


    def insercao_tlb(self, pg, frame):
        """
        Insercao na TLB, removendo o mais antigo se não houver mais espaço
        """
        if len(self.tlb) == self.num_tlb_entries:
            self.tlb.pop(0)
        self.tlb.append((pg, frame))
        return 

    def alocacao_frame(self, pg):
        """
        Alocacao de frame
        """
        for i in range(self.num_frames):
            if self.frames[i] == None: #encontrou frame livre
                self.frames[i] = pg 
                self.page_table[pg] = i
                self.lru_frames.append(pg)
                return 

        #se chegar aqui é pq n tem frame livre
        if self.rep_policy == "LRU":
            self.LRU(pg)
        else:
            self.SecondChance(pg)


    def LRU(self, pg):
        # LRU: Least Recently Used; subtituir a pg q n eh usada ha mais tempo
        # considerando que o mais antigo vai estar posicionado na posicao 0, remove da posicao 0 e adiciona o novo frame no final
        """
        Algoritmo LRU
        """
        pg_remover = self.lru_frames.pop(0)
        frame_remover = self.page_table.pop(pg_remover)
        self.frames[frame_remover] = pg
        self.page_table[pg] = frame_remover
        self.lru_frames.append(pg)

        

    def SecondChance(self, pg):
        """
        Algoritmo SecondChance
        """


    def print_statistics(self):
        print("=" * 60)
        print("SIMULADOR DE MEMÓRIA - Estatísticas de Acesso")
        print("=" * 60)
        print(f"Política de Substituição:   {self.rep_policy}")
        print(f"Tamanho da Página:          {self.page_size} bytes")
        print(f"Entradas na TLB:            {self.num_tlb_entries}")
        print(f"Número de Frames:           {self.num_frames}")
        print("-" * 60)
        print(f"TLB Hits:                   {self.tlb_hits:,}")
        print(f"TLB Misses:                 {self.tlb_misses:,}")
        print(f"Page Faults:                {self.page_faults:,}")
        print("=" * 60)



