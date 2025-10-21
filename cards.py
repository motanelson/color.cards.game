import pygame
import random
import csv
import time
import sys

# --- 1. Configurações e Cores ---

# 15 Cores VGA (sem Amarelo) e seus valores RGB e Hexadecimais
# O valor Hexadecimal de cada cor será o "valor" visível na carta.
VGA_COLORS = {
    "PRETO": ((0, 0, 0), "000000"),
    "AZUL": ((0, 0, 170), "0000AA"),
    "VERDE": ((0, 170, 0), "00AA00"),
    "CIANO": ((0, 170, 170), "00AAAA"),
    "VERMELHO": ((170, 0, 0), "AA0000"),
    "MAGENTA": ((170, 0, 170), "AA00AA"),
    "CASTANHO": ((170, 85, 0), "AA5500"), # Brown / Laranja Escuro
    "CINZENTO CLARO": ((170, 170, 170), "AAAAAA"),
    "CINZENTO ESCURO": ((85, 85, 85), "555555"),
    "AZUL CLARO": ((85, 85, 255), "5555FF"),
    "VERDE CLARO": ((85, 255, 85), "55FF55"),
    "CIANO CLARO": ((85, 255, 255), "55FFFF"),
    "VERMELHO CLARO": ((255, 85, 85), "FF5555"),
    "MAGENTA CLARO": ((255, 85, 255), "FF55FF"),
    "BRANCO": ((255, 255, 255), "FFFFFF"),
}

# Cor Amarela para o Fundo da Mesa (Board) - Cor Excluída da lista principal
YELLOW = (255, 255, 0)
BACKGROUND_COLOR = (40, 40, 40) # Cinzento para o resto do ecrã

# Constantes do Jogo
NUM_CORES = 15
CARTAS_POR_COR = 8
TOTAL_CARTAS = NUM_CORES * CARTAS_POR_COR # 120 Cartas

CARD_WIDTH = 120
CARD_HEIGHT = 180
CARD_BACK_COLOR = (170, 170, 170) # Cinzento VGA para o verso das cartas
TABLE_FILE = 'table.csv'

# Setup da Janela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CARD_DECK_POS = (SCREEN_WIDTH // 2 - CARD_WIDTH - 20, SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2)
CARD_PILE_POS = (SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2)

# --- 2. Funções Auxiliares de Dados e Placar ---

def load_scores():
    """Carrega o placar do arquivo CSV e retorna ordenado por tempo."""
    scores = []
    try:
        with open(TABLE_FILE, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None) # Pula o cabeçalho
            for row in reader:
                scores.append({'nome': row[0], 'tempo': float(row[1])})
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Erro ao carregar scores: {e}")
    
    scores.sort(key=lambda x: x['tempo'])
    return scores

def save_scores(scores):
    """Salva o placar no arquivo CSV."""
    scores.sort(key=lambda x: x['tempo'])
    try:
        with open(TABLE_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Nome', 'Tempo (segundos)'])
            for score in scores:
                writer.writerow([score['nome'], f"{score['tempo']:.2f}"])
    except Exception as e:
        print(f"Erro ao salvar scores: {e}")

def create_deck():
    """Cria e baralha o baralho de 120 cartas."""
    deck = []
    # Cria 8 cartas para cada uma das 15 cores
    for name, (rgb, hex_val) in VGA_COLORS.items():
        for _ in range(CARTAS_POR_COR):
            deck.append({
                'name': name,
                'rgb': rgb,
                'hex': hex_val
            })
    random.shuffle(deck)
    return deck

def rgb_to_hex(rgb):
    """Converte uma tupla RGB para uma string hexadecimal."""
    return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'.upper()

def get_text_color(rgb):
    """Retorna Preto ou Branco para garantir contraste na carta."""
    # Calcula a luminância (fórmula simples)
    luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])
    return (0, 0, 0) if luminance > 128 else (255, 255, 255)

# --- 3. Inicialização do Pygame ---
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font_time = pygame.font.SysFont('Arial', 24, bold=True)
font_card = pygame.font.SysFont('Arial', 32, bold=True)
font_message = pygame.font.SysFont('Arial', 40, bold=True)
font_score = pygame.font.SysFont('Arial', 20)

# --- 4. Variáveis do Jogo ---
deck = create_deck()
current_pile = [] # Cartas recolhidas

# A primeira carta define a cor alvo
target_card = deck.pop(0) # Remove a primeira carta do baralho
target_color_name = target_card['name']
target_color_rgb = target_card['rgb']
target_color_hex = target_card['hex']

# Estado do Jogo
game_started = False
game_over = False
start_time = 0.0
total_time = 0.0
cards_collected = 1
running = True

# --- 5. Funções de Desenho ---

def draw_card(surface, card, pos, is_face_up=True):
    """Desenha uma carta no ecrã."""
    rect = pygame.Rect(pos[0], pos[1], CARD_WIDTH, CARD_HEIGHT)
    
    if is_face_up:
        # Fundo da Carta (Cor da Carta)
        pygame.draw.rect(surface, card['rgb'], rect, border_radius=10)
        
        # Valor Hexadecimal (Texto)
        text_color = get_text_color(card['rgb'])
        hex_text = font_card.render(card['hex'], True, text_color)
        surface.blit(hex_text, (rect.centerx - hex_text.get_width() // 2, rect.centery - hex_text.get_height() // 2))
    else:
        # Verso da Carta
        pygame.draw.rect(surface, CARD_BACK_COLOR, rect, border_radius=10)
        pygame.draw.rect(surface, (0, 0, 0), rect, 5, border_radius=10) # Borda
        back_text = font_card.render("PY", True, (0, 0, 0))
        surface.blit(back_text, (rect.centerx - back_text.get_width() // 2, rect.centery - back_text.get_height() // 2))
        
    return rect # Retorna o retângulo para deteção de cliques

def draw_info_panel(elapsed_time):
    """Desenha o painel de informação e atualiza o título da janela."""
    
    # Atualiza o Título
    title_text = f"Hexa-Sort | Tempo: {elapsed_time:.2f}s | Cartas Recolhidas: {cards_collected}/{CARTAS_POR_COR}"
    pygame.display.set_caption(title_text)
    
    # Desenha o Fundo da Mesa (Board) - Cor Amarela
    board_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 100)
    pygame.draw.rect(screen, YELLOW, board_rect)
    
    # Texto da Cor Alvo
    target_text = font_time.render(f"Cor Alvo: {target_color_name} ({target_color_hex})", True, (0, 0, 0))
    screen.blit(target_text, (SCREEN_WIDTH // 2 - target_text.get_width() // 2, 35))

def draw_game_over_screen():
    """Desenha o placar e a mensagem de fim de jogo."""
    global total_time
    
    # Fundo semi-transparente
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((255, 255, 0))
    screen.blit(overlay, (0, 0))

    # Título
    title_text = font_message.render("COR COMPLETA!", True, (0, 255, 0))
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
    
    # Tempo total
    time_text = font_message.render(f"O Seu Tempo: {total_time:.2f} segundos", True, (255, 255, 255))
    screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, 120))
    
    # Pedir nome e salvar score
    player_name = get_player_name_for_score()
    scores = load_scores()
    scores.append({'nome': player_name, 'tempo': total_time})
    save_scores(scores)
    
    # Placar (Scores)
    score_title = font_time.render("Quadro de Pontuação (Top 10):", True, (0, 255, 255))
    screen.blit(score_title, (50, 200))

    y_offset = 230
    # Desenha os 10 melhores
    for i, score in enumerate(scores[:10]):
        text = font_score.render(f"{i+1}. {score['nome']} - {score['tempo']:.2f}s", True, (255, 255, 255))
        screen.blit(text, (50, y_offset + i * 25))
        
    # Mensagem de reinício
    restart_text = font_time.render("Pressione ESC para Sair ou ENTER para Reiniciar", True, (255, 165, 0))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT - 50))
    r=True
    pygame.display.flip()
    while r:
        clock.tick(30)
        for event in pygame.event.get():
            if event.key == pygame.K_q:
                 r=False

def get_player_name_for_score():
    """Permite ao jogador introduzir o seu nome."""
    name = ""
    input_active = True
    input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 50)
    
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name:
                        input_active = False
                        print(name)
                    else:
                        name = "ANÓNIMO"
                        input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if font_message.size(name + event.unicode)[0] < input_rect.width - 10:
                        name += event.unicode
        
        # Desenha tela de fundo e input
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        prompt_text = font_message.render("Introduza o Seu Nome:", True, (255, 255, 255))
        screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
        
        pygame.draw.rect(screen, (255, 255, 255), input_rect, 2)
        txt_surface = font_message.render(name, True, (255, 255, 255))
        screen.blit(txt_surface, (input_rect.x + 5, input_rect.y + 5))
        
        pygame.display.flip()
        clock.tick(30)
        
    return name.upper()

def reset_game():
    """Reinicia o estado do jogo."""
    global deck, current_pile, target_card, target_color_name, target_color_rgb, target_color_hex, \
           game_started, game_over, start_time, total_time, cards_collected
           
    deck = create_deck()
    current_pile = []
    
    # Define a nova cor alvo
    if deck:
        target_card = deck.pop(0)
        target_color_name = target_card['name']
        target_color_rgb = target_card['rgb']
        target_color_hex = target_card['hex']
    else:
        # Raro, mas possível se a função create_deck falhar
        print("Erro: Baralho Vazio.")
        return
        
    game_started = False
    game_over = False
    start_time = 0.0
    total_time = 0.0
    cards_collected = 0
    pygame.display.set_caption("Hexa-Sort | Pressione para Começar")


# --- 6. Game Loop Principal ---

reset_game() # Inicializa o jogo ao iniciar

while running:
    # Lógica de Tempo
    elapsed_time = 0.0
    if game_started and not game_over:
        current_time = time.time()
        elapsed_time = current_time - start_time
    elif game_over:
        elapsed_time = total_time

    # --- 6.1 Tratamento de Eventos ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_RETURN:
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif not game_started and event.key == pygame.K_SPACE:
                # Começar com a barra de espaço
                game_started = True
                start_time = time.time()
        
        if game_started and not game_over and event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            
            # 1. Verifica clique na carta de topo do baralho (Pilha de Recolha)
            if deck:
                # Usa a posição da carta de topo para colisão (rect da carta visível)
                deck_rect = draw_card(screen, deck[-1], CARD_DECK_POS, is_face_up=False) 
                
                if deck_rect.collidepoint(pos):
                    # Tira a carta de topo do baralho
                    pulled_card = deck.pop()
                    
                    # 2. Verifica a Cor
                    if pulled_card['name'] == target_color_name:
                        # Carta CORRETA
                        current_pile.append(pulled_card)
                        cards_collected += 1
                        
                        if cards_collected == 7:
                            # FIM DO JOGO!
                            game_over = True
                            end_time = time.time()
                            total_time = end_time - start_time
                    else:
                        # Carta INCORRETA: Perde a carta e o jogo continua
                        # O utilizador simplesmente descarta a carta errada
                        pass # A carta já foi removida do baralho, apenas não vai para a pilha de recolha

    # --- 6.2 Desenho ---
    screen.fill(BACKGROUND_COLOR) 

    if not game_started and not game_over:
        # Tela de Início
        start_message = font_message.render("Hexa-Sort: Pressione ESPAÇO para Começar", True, (0, 255, 0))
        instructions_line1 = font_time.render("Objetivo: Recolher 8 cartas da mesma cor que a 1ª carta.", True, (255, 255, 255))
        instructions_line2 = font_time.render(f"Cor Alvo: {target_color_name} ({target_color_hex})", True, (255, 255, 0))
        instructions_line3 = font_time.render("Clique na pilha para virar a próxima carta.", True, (255, 255, 255))
        
        screen.blit(start_message, (SCREEN_WIDTH // 2 - start_message.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(instructions_line1, (SCREEN_WIDTH // 2 - instructions_line1.get_width() // 2, SCREEN_HEIGHT // 2 + 0))
        screen.blit(instructions_line2, (SCREEN_WIDTH // 2 - instructions_line2.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
        screen.blit(instructions_line3, (SCREEN_WIDTH // 2 - instructions_line3.get_width() // 2, SCREEN_HEIGHT // 2 + 80))

    elif not game_over:
        # Jogo em Andamento
        
        # 1. Painel de Informação (Fundo Amarelo)
        draw_info_panel(elapsed_time)
        
        # 2. Baralho (Pilha de cartas a puxar)
        if deck:
            # Desenha o verso da carta de topo (visível)
            draw_card(screen, deck[-1], CARD_DECK_POS, is_face_up=False) 
            deck_count_text = font_time.render(f"Cartas Restantes: {len(deck)}", True, (255, 255, 255))
            screen.blit(deck_count_text, (CARD_DECK_POS[0] + CARD_WIDTH // 2 - deck_count_text.get_width() // 2, CARD_DECK_POS[1] + CARD_HEIGHT + 20))

        else:
            empty_deck_text = font_time.render("BARALHO VAZIO", True, (255, 0, 0))
            screen.blit(empty_deck_text, (CARD_DECK_POS[0] + CARD_WIDTH // 2 - empty_deck_text.get_width() // 2, CARD_DECK_POS[1] + CARD_HEIGHT // 2))

        # 3. Pilha de Recolha (Cartas Correta)
        pile_label_text = font_time.render("Cartas Recolhidas", True, (255, 255, 255))
        screen.blit(pile_label_text, (CARD_PILE_POS[0] + CARD_WIDTH // 2 - pile_label_text.get_width() // 2, CARD_PILE_POS[1] - 30))
        
        if current_pile:
            # Desenha a última carta recolhida (visível)
            top_card = current_pile[-1]
            draw_card(screen, top_card, CARD_PILE_POS, is_face_up=True)
            
            pile_count_text = font_time.render(f"Total: {len(current_pile)}", True, (255, 255, 255))
            screen.blit(pile_count_text, (CARD_PILE_POS[0] + CARD_WIDTH // 2 - pile_count_text.get_width() // 2, CARD_PILE_POS[1] + CARD_HEIGHT + 20))
        else:
            # Desenha uma carta com a cor alvo como lembrete
            placeholder_card = {'rgb': target_color_rgb, 'hex': "ALVO"}
            draw_card(screen, placeholder_card, CARD_PILE_POS, is_face_up=True)
            
            empty_pile_text = font_time.render("PILHA VAZIA", True, (255, 255, 255))
            screen.blit(empty_pile_text, (CARD_PILE_POS[0] + CARD_WIDTH // 2 - empty_pile_text.get_width() // 2, CARD_PILE_POS[1] + CARD_HEIGHT + 20))
            
    elif game_over:
        # Tela de Fim de Jogo/Placar
        draw_game_over_screen()

    # Atualiza a janela
    pygame.display.flip()
    
    # Limita o FPS
    clock.tick(60)

pygame.quit()
sys.exit()
