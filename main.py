# main.py - NOVO VISUAL DARK E FANTASMAGÓRICO
import tkinter as tk
from tkinter import filedialog, messagebox, font as tkfont
from converter import processar_e_converter # Importa a função principal
import os
import threading
# Tentativa de importação da PIL para suportar PNG/JPG
try:
    from PIL import Image, ImageTk
except ImportError:
    # Se a PIL não estiver instalada, define como None
    Image = None
    ImageTk = None

# =========================================================
# CONFIGURAÇÕES DE TEMA E LOGO
# =========================================================
BG_DARK = "#1e1e1e"  # Fundo principal (Dark Grey)
FG_LIGHT = "#00FF00" # Cor do texto (Verde Néon para um toque Fantasma)
TITLE_COLOR = "#00ffff" # Ciano brilhante para o título
BTN_BG = "black"     # Fundo dos botões de seleção
BTN_FG = "white"     # Texto dos botões de seleção
GENERATE_BTN_BG = "#cc0000" # Vermelho escuro para o botão principal
GENERATE_BTN_FG = "white"
FONT_FAMILY = "Helvetica" 

# Caminho para a logo (COLOQUE O NOME DO SEU ARQUIVO DE LOGO AQUI)
# Se o arquivo 'logo.png' não existir, nada será exibido.
LOGO_PATH = "logo.png" 

class App:
    def __init__(self, root):
        self.root = root
        
        # Configuração do tema principal da janela
        root.title("EndConversor | IOC Converter")
        root.config(bg=BG_DARK)
        root.geometry("600x350")
        root.resizable(False, False)
        
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        
        # MUDANÇA: Define as caixas de texto vazias
        self.input_dir.set("")
        self.output_dir.set("")
        
        self.logo_img = None
        self._load_logo()

        self._setup_ui()

    def _load_logo(self):
        """ Carrega a logo, suportando transparência e redimensionamento. """
        if Image and ImageTk and os.path.exists(LOGO_PATH):
            try:
                img = Image.open(LOGO_PATH).convert("RGBA")
                img.thumbnail((100, 100)) 
                self.logo_img = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Erro ao carregar a logo ({LOGO_PATH}): {e}")
                self.logo_img = None
        elif not Image and os.path.exists(LOGO_PATH):
            print("Aviso: O módulo Pillow (PIL) não está instalado. Não é possível carregar PNGs/JPGs. Tente 'pip install Pillow'.")

    def _setup_ui(self):
        """ Configura a interface com o tema Dark/Fantasmagórico. """
        # Fonte "Times New Roman" para um look mais "fantasmagórico"
        title_font = tkfont.Font(family="Times New Roman", size=24, weight="bold")
        label_font = tkfont.Font(family=FONT_FAMILY, size=10, weight="bold")
        
        # --- TÍTULO CENTRALIZADO (EndConversor) e LOGO ---
        title_frame = tk.Frame(self.root, bg=BG_DARK)
        title_frame.pack(pady=10)
        
        if self.logo_img:
            logo_label = tk.Label(title_frame, image=self.logo_img, bg=BG_DARK)
            logo_label.pack(side="left", padx=10)
        
        tk.Label(title_frame, 
                 text="ENDCONVERSOR", 
                 font=title_font, 
                 fg=TITLE_COLOR, 
                 bg=BG_DARK, 
                 pady=5).pack(side="left")

        # --- SELEÇÃO DE PASTA DE ENTRADA ---
        frm_input = tk.Frame(self.root, padx=10, pady=5, bg=BG_DARK)
        frm_input.pack(fill='x')

        tk.Label(frm_input, text="Pasta de Arquivos (.yar / .dmp):", fg=FG_LIGHT, bg=BG_DARK, font=label_font).pack(anchor='w')
        # Caixa de texto (Entry) com tema escuro e letras claras
        tk.Entry(frm_input, textvariable=self.input_dir, width=60, bg="#333333", fg=FG_LIGHT, insertbackground=FG_LIGHT, borderwidth=2).pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Botão Preto com Letras Brancas e Destacadas
        tk.Button(frm_input, text="Selecionar Entrada", 
                  command=lambda: self._select(self.input_dir), 
                  bg=BTN_BG, fg=BTN_FG, activebackground="#333333", activeforeground=BTN_FG, 
                  font=label_font, relief=tk.FLAT, padx=10, borderwidth=2).pack(side='left')

        # --- SELEÇÃO DE PASTA DE SAÍDA ---
        frm_output = tk.Frame(self.root, padx=10, pady=5, bg=BG_DARK)
        frm_output.pack(fill='x')

        tk.Label(frm_output, text="Pasta de Saída (Relatórios JSON/JS):", fg=FG_LIGHT, bg=BG_DARK, font=label_font).pack(anchor='w')
        # Caixa de texto (Entry) com tema escuro e letras claras
        tk.Entry(frm_output, textvariable=self.output_dir, width=60, bg="#333333", fg=FG_LIGHT, insertbackground=FG_LIGHT, borderwidth=2).pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Botão Preto com Letras Brancas e Destacadas
        tk.Button(frm_output, text="Selecionar Saída", 
                  command=lambda: self._select(self.output_dir), 
                  bg=BTN_BG, fg=BTN_FG, activebackground="#333333", activeforeground=BTN_FG, 
                  font=label_font, relief=tk.FLAT, padx=10, borderwidth=2).pack(side='left')

        # --- BOTÃO PRINCIPAL (GERAR E ENVIAR) ---
        self.btn = tk.Button(self.root, text="GERAR E ENVIAR", 
                             bg=GENERATE_BTN_BG, fg=GENERATE_BTN_FG, 
                             command=self._start_thread,
                             font=tkfont.Font(family=FONT_FAMILY, size=14, weight="bold"),
                             activebackground="#990000", activeforeground="white",
                             relief=tk.RAISED, borderwidth=3)
        self.btn.pack(padx=20, pady=25, fill='x')

    def _select(self, var):
        """ Abre a caixa de diálogo para seleção de pasta. """
        d = filedialog.askdirectory()
        if d:
            var.set(d)

    def _start_thread(self):
        inpath = self.input_dir.get()
        outpath = self.output_dir.get()
        
        # Verifica se as pastas foram realmente selecionadas/digitadas
        if not inpath or not outpath:
            messagebox.showerror("Erro", "Por favor, selecione ambas as pastas de Entrada e Saída.")
            return
            
        # Cria as pastas necessárias antes de processar
        os.makedirs(inpath, exist_ok=True)
        os.makedirs(outpath, exist_ok=True)
            
        self.btn.config(state="disabled", text="PROCESSANDO E ENVIANDO...", bg="gray")
        # Roda a conversão em uma thread separada (não trava a GUI)
        t = threading.Thread(target=self._run_conversion, args=(inpath, outpath))
        t.start()

    def _run_conversion(self, inpath, outpath):
        try:
            # CORREÇÃO: processo de conversão e envio
            success, total_iocs, report_path = processar_e_converter(inpath, outpath)

            if success:
                messagebox.showinfo("Sucesso Fantasmagórico", f"👻 Gerado: {total_iocs} IOCs. Webhooks enviados. Verifique {os.path.basename(report_path)}.")
            else:
                # O status 'False' pode indicar que o envio falhou (erros de webhook) ou que não há IOCs.
                messagebox.showwarning("Aviso Sobrenatural", "💀 A conversão ou o envio falhou. Verifique o console para mais detalhes.")
                
        except Exception as e:
            messagebox.showerror("Erro Crítico", f"💥 Erro fatal ao processar: {e}")
        finally:
            self.btn.config(state="normal", text="GERAR E ENVIAR", bg=GENERATE_BTN_BG)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()