import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import locale

# 1. Find the correct thread URL dynamically
def get_latest_thread_url():
    forum_url = "https://board.pt.metin2.gameforge.com/index.php?board/86-eventos-metin2-pt/"  # Adjust if needed
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(forum_url, headers=headers)
    if response.status_code != 200:
        print("Error accessing the forum page")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    thread_links = soup.find_all("a", class_="wbbTopicLink")

    for link in thread_links:
        if "[Tigerghost]" in link.text:
            return link["href"]
    
    print("Forum thread not found!")
    return None

target_url = get_latest_thread_url()
if not target_url:
    print("Webscraping failed!")
    exit()

# 3. Make the HTTP request
headers = {"User-Agent": "Mozilla/5.0"}  # Avoid basic blocking
response = requests.get(target_url, headers=headers)
if response.status_code != 200:
    print("Error accessing the thread page")
    exit()

# 4. Parse the HTML
soup = BeautifulSoup(response.text, "html.parser")
data = soup.find("table")
rows = data.find_all("tr")
if not data:
    print("Required data not found!")
    exit()

# 5. Extract data
try:
    locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')  # Tente com pt_PT
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')  # Ou pt_BR, se for o caso
    except locale.Error:
        print("Locale de Português não disponível. A conversão de data pode falhar.")

def get_weekday(date_str):
    """
    Recebe uma data no formato "2 de fevereiro de 2025" e retorna o dia da semana em português.
    """
    # Mapeamento dos índices do weekday para o nome em português (segunda-feira é 0)
    weekdays = {
        0: "Segunda-feira",
        1: "Terça-feira",
        2: "Quarta-feira",
        3: "Quinta-feira",
        4: "Sexta-feira",
        5: "Sábado",
        6: "Domingo"
    }
    try:
        # Converte a string para um objeto datetime
        date_obj = datetime.strptime(date_str, "%d de %B de %Y")
        return weekdays[date_obj.weekday()]
    except Exception as e:
        print("Erro ao converter a data:", e)
        return ""

# Abre (ou cria) o arquivo CSV para escrita
mes = datetime.now().strftime("%B")
with open(f"output_{mes}.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    # Escreve o cabeçalho
    writer.writerow(["Dia", "Evento A", "Evento B"])
    
    # Percorre as linhas da tabela, ignorando a primeira (cabeçalho da tabela HTML)
    for row in rows[1:]:
        cells = row.find_all("td")
        if len(cells) >= 3:
            # Extrai e limpa o texto de cada célula
            date_text = cells[0].get_text(strip=True)
            event_a = cells[1].get_text(strip=True)
            event_b = cells[2].get_text(strip=True)
            
            # Extrai o número do dia (primeiro token da string da data)
            day_number = date_text.split()[0]
            weekday = get_weekday(date_text)
            dia_formatado = f"{day_number} | {weekday}"
            
            # Escreve a linha formatada no CSV
            writer.writerow([dia_formatado, event_a, event_b])