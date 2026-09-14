from PIL import Image
import os

def converter_cor_gimp_para_rgb(gimp_r, gimp_g, gimp_b):
    """
    Converte valores do GIMP (0-100) para RGB (0-255)
    """
    r = int((gimp_r / 100) * 255)
    g = int((gimp_g / 100) * 255)
    b = int((gimp_b / 100) * 255)
    return (r, g, b)

def verificar_faixa_cor(pixels, x, y_inicio, altura, cor_alvo, tolerancia=15):
    """
    Auxiliar para verificar se um bloco vertical de 'altura' pixels possui a cor desejada
    """
    for dy in range(altura):
        pixel = pixels[x, y_inicio + dy]
        r, g, b = pixel[:3]
        if (abs(r - cor_alvo[0]) > tolerancia or 
            abs(g - cor_alvo[1]) > tolerancia or 
            abs(b - cor_alvo[2]) > tolerancia):
            return False
    return True

def encontrar_padrao_vertical(imagem, tolerancia=15):
    """
    Procura no último pixel da direita o padrão:
    - Faixa 1: (35, 31, 32) com altura 4 (margem 1 a 7 px)
    - Faixa 2: (255, 255, 255) com altura 5 (margem 2 a 8 px)
    - Faixa 3: (35, 31, 32) com altura 4 (margem 1 a 7 px)
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    x = largura - 1  # Último pixel da direita
    
    cor_escura = (35, 31, 32)
    cor_branca = (255, 255, 255)
    
    posicoes_corte = []
    
    y = 0
    while y < altura - 20: # Garante espaço suficiente na busca
        padrao_encontrado = False
        altura_total_padrao = 0
        
        # Testa as variações de altura permitidas pela margem de erro (±3px)
        for h1 in range(1, 8):      # Altura 4 ± 3 -> [1 a 7]
            for h2 in range(2, 9):  # Altura 5 ± 3 -> [2 a 8]
                for h3 in range(1, 8): # Altura 4 ± 3 -> [1 a 7]
                    
                    if y + h1 + h2 + h3 >= altura:
                        continue
                    
                    # Checa a sequência das três faixas
                    if (verificar_faixa_cor(pixels, x, y, h1, cor_escura, tolerancia) and
                        verificar_faixa_cor(pixels, x, y + h1, h2, cor_branca, tolerancia) and
                        verificar_faixa_cor(pixels, x, y + h1 + h2, h3, cor_escura, tolerancia)):
                        
                        padrao_encontrado = True
                        altura_total_padrao = h1 + h2 + h3
                        break
                if padrao_encontrado:
                    break
            if padrao_encontrado:
                break
        
        if padrao_encontrado:
            # Corta 17 pixels antes do início do padrão
            posicao_corte = y - 17
            if posicao_corte < 0:
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Padrão encontrado em y={y}, cortando em y={posicao_corte}")
            
            # Avança o cursor para além do padrão detectado
            y += altura_total_padrao
        else:
            y += 1
            
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando no padrão encontrado
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_padrao_vertical(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão encontrado na imagem!")
        return
    
    print(f"Encontrados {len(posicoes_corte)} pontos de corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte
    
    # Corta a seção final após o último ponto de corte
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "./inteiras/pagina_enem_23.png"  # Substitua pela sua imagem
    pasta_saida = "pg23"                       # Substitua pelo nome da pasta de saída
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print("Divisão concluída!")