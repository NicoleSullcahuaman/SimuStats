import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
import os
from scipy import stats

# Aumentar el límite de tamaño de imagen para evitar el error de decompression bomb
Image.MAX_IMAGE_PIXELS = None

class GeneradorAleatorios:
    """
    Generador de variables aleatorias sin usar funciones random del lenguaje.
    
    Utiliza el método de Generador Congruencial Lineal (LCG) como base
    para generar números pseudoaleatorios uniformes en [0,1), y luego
    aplica métodos de transformación para generar otras distribuciones.
    
    Parámetros
    ----------
    semilla : int, opcional
        Semilla inicial para el generador. Si no se proporciona,
        se genera automáticamente usando el tiempo del sistema y otros factores.
    
    Métodos
    -------
    uniforme(a, b, n) : Genera n valores de distribución uniforme continua
    exponencial(lambd, n) : Genera n valores de distribución exponencial
    normal(mu, sigma, n) : Genera n valores de distribución normal
    bernoulli(p, n) : Genera n valores de distribución de Bernoulli
    binomial(n_trials, p, n) : Genera n valores de distribución binomial
    poisson(lambd, n) : Genera n valores de distribución de Poisson
    """
    
    def __init__(self, semilla=None):
        if semilla is None:
            # Combinar múltiples fuentes para mejor aleatoriedad
            tiempo = int(time.time() * 1000000)
            pid = os.getpid()
            # Usar bytes del sistema si está disponible
            try:
                random_bytes = int.from_bytes(os.urandom(4), byteorder='big')
                self.semilla = (tiempo ^ pid ^ random_bytes) % (2**31 - 1)
            except:
                self.semilla = (tiempo ^ pid) % (2**31 - 1)
        else:
            self.semilla = semilla
        self.actual = self.semilla
    
    def lcg(self):
        """
        Generador Congruencial Lineal (LCG)
        
        Utiliza los parámetros de Numerical Recipes:
        a = 1664525, c = 1013904223, m = 2^32
        
        Returns
        -------
        float : Número pseudoaleatorio en el intervalo [0,1)
        """
        a = 1664525
        c = 1013904223
        m = 2**32
        self.actual = (a * self.actual + c) % m
        return self.actual / m
    
    def uniforme(self, a=0, b=1, n=1):
        """
        Distribución uniforme continua U(a,b)
        
        Parámetros
        ----------
        a : float, límite inferior (default 0)
        b : float, límite superior (default 1)
        n : int, cantidad de valores a generar (default 1)
        
        Returns
        -------
        list : Lista con n valores uniformes en [a,b)
        """
        return [a + (b - a) * self.lcg() for _ in range(n)]
    
    def exponencial(self, lambd=1.0, n=1):
        """
        Distribución exponencial Exp(λ)
        
        Utiliza el método de transformación inversa.
        
        Parámetros
        ----------
        lambd : float, parámetro de tasa λ (default 1.0)
        n : int, cantidad de valores a generar (default 1)
        
        Returns
        -------
        list : Lista con n valores exponenciales
        """
        return [-np.log(self.lcg()) / lambd for _ in range(n)]
    
    def normal(self, mu=0, sigma=1, n=1):
        """
        Distribución normal N(μ, σ²)
        
        Utiliza el método de Box-Muller para transformar
        variables uniformes en normales.
        
        Parámetros
        ----------
        mu : float, media (default 0)
        sigma : float, desviación estándar (default 1)
        n : int, cantidad de valores a generar (default 1)
        
        Returns
        -------
        list : Lista con n valores normales
        """
        resultados = []
        for _ in range(n):
            u1 = self.lcg()
            u2 = self.lcg()
            z0 = np.sqrt(-2 * np.log(u1)) * np.cos(2 * np.pi * u2)
            resultados.append(mu + sigma * z0)
        return resultados
    
    def bernoulli(self, p=0.5, n=1):
        """
        Distribución de Bernoulli Ber(p)
        
        Parámetros
        ----------
        p : float, probabilidad de éxito (default 0.5)
        n : int, cantidad de valores a generar (default 1)
        
        Returns
        -------
        list : Lista con n valores {0,1}
        """
        return [1 if self.lcg() < p else 0 for _ in range(n)]
    
    def binomial(self, n_trials=10, p=0.5, n=1):
        """
        Distribución binomial B(n,p)
        
        Suma de n_trials ensayos de Bernoulli.
        
        Parámetros
        ----------
        n_trials : int, número de ensayos (default 10)
        p : float, probabilidad de éxito (default 0.5)
        n : int, cantidad de valores a generar (default 1)
        
        Returns
        -------
        list : Lista con n valores binomiales
        """
        return [sum(self.bernoulli(p, n_trials)) for _ in range(n)]
    
    def poisson(self, lambd=1.0, n=1):
        """
        Distribución de Poisson Poi(λ)
        
        Utiliza el algoritmo de Knuth.
        
        Parámetros
        ----------
        lambd : float, parámetro λ (default 1.0)
        n : int, cantidad de valores a generar (default 1)
        
        Returns
        -------
        list : Lista con n valores de Poisson
        """
        resultados = []
        for _ in range(n):
            L = np.exp(-lambd)
            k = 0
            p = 1.0
            while p > L:
                k += 1
                p *= self.lcg()
            resultados.append(k - 1)
        return resultados

class SimuStatsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SimuStats")

        # Obtener dimensiones de la pantalla
        ancho_pantalla = root.winfo_screenwidth()
        alto_pantalla = root.winfo_screenheight()

        # Configurar ventana en pantalla completa o tamaño específico
        self.root.geometry(f"{ancho_pantalla}x{alto_pantalla}")

        # Cargar y configurar imagen de fondo (solo una vez)
        try:
            ruta_fondo = r"C:\Users\user\OneDrive\Documents\SimuStats\fondo.jpg"
            self.img_fondo = Image.open(ruta_fondo)
            self.img_fondo = self.img_fondo.resize((ancho_pantalla, alto_pantalla), Image.Resampling.LANCZOS)
            self.fondo = ImageTk.PhotoImage(self.img_fondo)

            self.canvas = tk.Canvas(root, width=ancho_pantalla, height=alto_pantalla, highlightthickness=0)
            self.canvas.pack(fill="both", expand=True)
            self.canvas.create_image(0, 0, image=self.fondo, anchor="nw")
        except Exception as e:
            print(f"Error al cargar fondo: {e}")
            self.canvas = tk.Canvas(root, width=ancho_pantalla, height=alto_pantalla, bg='#2c3e50', highlightthickness=0)
            self.canvas.pack(fill="both", expand=True)

        self.crear_interfaz()

    def crear_interfaz(self):
        centro_x = self.root.winfo_screenwidth() // 2
        centro_y = self.root.winfo_screenheight() // 2

        # Cargar el logo
        try:
            self.img_logo = Image.open(r"C:\Users\user\OneDrive\Documents\SimuStats\logo.jpg")
            self.img_logo = self.img_logo.resize((400, 200), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(self.img_logo)
            self.canvas.create_image(centro_x, centro_y - 150, image=self.logo, anchor="center")
        except Exception as e:
            print(f"Error al cargar logo: {e}")
            self.canvas.create_text(centro_x, centro_y - 100, text="SimuStats",
                                    font=("Arial", 32, "bold"), fill="white")

        # Botón Continuar
        self.btn_continuar = tk.Button(
            self.canvas,
            text="CONTINUAR",
            font=("Segoe UI", 10, "bold"),
            bg="#B8B8B8",
            fg="black",
            padx=10,
            pady=3,
            cursor="hand2",
            relief="flat",
            borderwidth=0,
            command=self.mostrar_menu_principal
        )
        self.canvas.create_window(centro_x, centro_y + 10, window=self.btn_continuar, anchor="center")

        # Efectos hover
        self.btn_continuar.bind("<Enter>", lambda e: self.btn_continuar.config(bg="#A0A0A0"))
        self.btn_continuar.bind("<Leave>", lambda e: self.btn_continuar.config(bg="#B8B8B8"))

    def mostrar_menu_principal(self):
        """Menú principal dentro de la misma ventana"""
        # Limpiar el canvas
        for widget in self.canvas.winfo_children():
            widget.destroy()
        self.canvas.delete("all")

        # Dibujar fondo nuevamente
        ancho_pantalla = self.root.winfo_screenwidth()
        alto_pantalla = self.root.winfo_screenheight()
        self.canvas.create_image(0, 0, image=self.fondo, anchor="nw")

        # Frame de contenido
        frame_contenido = tk.Frame(self.canvas, bg='', highlightthickness=0)
        frame_contenido.place(relx=0.5, rely=0.5, anchor="center")

        # --- Título ---
        title = tk.Label(frame_contenido,
                         text="SimuStats - Menú Principal",
                         font=("Segoe UI", 32, "bold"),
                         bg='#c19a6b', fg="#181001", padx=40, pady=20)
        title.pack(fill="x", pady=20)

        # --- Estilo de botones ---
        btn_style = {
            'font': ("Segoe UI", 16, "bold"),
            'bg': '#c19a6b',
            'fg': '#4b2e05',
            'activebackground': '#a67c52',
            'activeforeground': '#ffffff',
            'relief': 'flat',
            'borderwidth': 2,
            'cursor': 'hand2',
            'width': 45,
            'height': 2
        }

        # --- Botones del menú ---
        opciones = [
            ("1. Generación de Variables Aleatorias", self.ventana_generacion_aleatorios),
            ("2. Prueba de Ajuste de Distribuciones", self.ventana_prueba_ajuste),
            ("3. Método de Monte Carlo", self.ventana_monte_carlo),
            ("4. Ayuda y Documentación", self.ventana_ayuda),
            ("5. Salir", self.root.destroy)
        ]

        for texto, comando in opciones:
            btn = tk.Button(frame_contenido, text=texto, command=comando, **btn_style)
            btn.pack(pady=12)

            # Efectos hover
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg='#a67c52', fg='#ffffff'))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg='#c19a6b', fg='#4b2e05'))

        # --- Footer ---
        footer = tk.Label(frame_contenido,
                          text="SimuStats",
                          font=("Segoe UI", 12),
                          bg='#000000', fg='#dddddd')
        footer.pack(pady=30)

    def ventana_generacion_aleatorios(self):
        """Ventana para generar variables aleatorias"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Generación de Variables Aleatorias")
        ventana.state('zoomed')
        ventana.configure(bg="#fcdea6")

        # --- Fondo OPTIMIZADO (reutiliza la imagen pre-cargada) ---
        canvas_fondo = tk.Canvas(ventana, 
                        width=self.root.winfo_screenwidth(), 
                        height=self.root.winfo_screenheight(), 
                        highlightthickness=0)
        canvas_fondo.pack(fill="both", expand=True)
        canvas_fondo.create_image(0, 0, image=self.fondo, anchor="nw")
        canvas_fondo.image = self.fondo

        # --- Crear Frame contenedor con scroll ---
        contenedor_scroll = tk.Frame(canvas_fondo, bg="#b8945f")
        contenedor_scroll.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.92)

        # Canvas para el scroll
        canvas_scroll = tk.Canvas(contenedor_scroll, bg="#b8945f", highlightthickness=0)
        scrollbar = tk.Scrollbar(contenedor_scroll, orient="vertical", command=canvas_scroll.yview)
        
        # Frame scrolleable que contendrá todo el contenido
        main_frame = tk.Frame(canvas_scroll, bg="#b8945f")
        
        # Configurar el canvas
        main_frame.bind(
            "<Configure>",
            lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
        )
        
        canvas_scroll.create_window((0, 0), window=main_frame, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar canvas y scrollbar
        canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Habilitar scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas_scroll.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event):
            canvas_scroll.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas_scroll.unbind_all("<MouseWheel>")
        
        canvas_scroll.bind('<Enter>', _bind_mousewheel)
        canvas_scroll.bind('<Leave>', _unbind_mousewheel)

        # Título
        tk.Label(main_frame, text="Generación de Variables Aleatorias",
                font=("Segoe UI", 24, "bold"),
                bg='#4b2e05', fg='#d4a574').pack(pady=15)

        # === Cuadro de Configuración ===
        config_frame = tk.LabelFrame(main_frame, text="Configuración",
                                    font=("Segoe UI", 11, "bold"),
                                    bg='#6b4423', fg='#f5deb3',
                                    relief='solid', bd=2)
        config_frame.pack(fill="x", padx=40, pady=(10, 15))

        # --- Contenedor interno ---
        config_inner = tk.Frame(config_frame, bg='#6b4423')
        config_inner.pack(fill="x", padx=10, pady=10)

        # FILA 1: Tipo y Distribución
        fila1 = tk.Frame(config_inner, bg='#6b4423')
        fila1.pack(fill="x", pady=5)

        # Tipo de variable
        tk.Label(fila1, text="Tipo:", font=("Segoe UI", 10, "bold"),
                bg='#6b4423', fg='#f5deb3').pack(side="left", padx=(0, 10))

        tipo_var = tk.StringVar(value="Discreta")
        tk.Radiobutton(fila1, text="Discreta", variable=tipo_var, value="Discreta",
                    bg='#6b4423', fg='#f5deb3', selectcolor='#8b5a3c',
                    font=("Segoe UI", 9)).pack(side="left", padx=5)
        tk.Radiobutton(fila1, text="Continua", variable=tipo_var, value="Continua",
                    bg='#6b4423', fg='#f5deb3', selectcolor='#8b5a3c',
                    font=("Segoe UI", 9)).pack(side="left", padx=5)

        # Distribución
        tk.Label(fila1, text="Distribución:", font=("Segoe UI", 10, "bold"),
                bg='#6b4423', fg='#f5deb3').pack(side="left", padx=(30, 10))

        dist_var = tk.StringVar()
        dist_combo = ttk.Combobox(fila1, textvariable=dist_var,
                                values=["Bernoulli", "Binomial", "Poisson"],
                                state="readonly", width=15, font=("Segoe UI", 9))
        dist_combo.pack(side="left", padx=5)
        dist_combo.current(0)

        def actualizar_distribuciones(*args):
            if tipo_var.get() == "Discreta":
                dist_combo['values'] = ["Bernoulli", "Binomial", "Poisson"]
            else:
                dist_combo['values'] = ["Uniforme", "Exponencial", "Normal"]
            dist_combo.current(0)
        tipo_var.trace('w', actualizar_distribuciones)

        # FILA 2: Semilla y N valores
        fila2 = tk.Frame(config_inner, bg='#6b4423')
        fila2.pack(fill="x", pady=5)

        tk.Label(fila2, text="Semilla:", font=("Segoe UI", 10, "bold"),
                bg='#6b4423', fg='#f5deb3').pack(side="left", padx=(0, 10))

        semilla_var = tk.StringVar()
        semilla_entry = tk.Entry(fila2, textvariable=semilla_var,
                                width=12, font=("Segoe UI", 9),
                                bg='#d4a574', fg='#4b2e05')
        semilla_entry.pack(side="left", padx=5)

        auto_semilla = tk.BooleanVar(value=True)
        tk.Checkbutton(fila2, text="Auto", variable=auto_semilla,
                    bg='#6b4423', fg='#f5deb3', selectcolor='#8b5a3c',
                    font=("Segoe UI", 9),
                    command=lambda: semilla_entry.config(
                        state='disabled' if auto_semilla.get() else 'normal')).pack(side="left", padx=5)
        semilla_entry.config(state='disabled')

        tk.Label(fila2, text="N° valores:", font=("Segoe UI", 10, "bold"),
                bg='#6b4423', fg='#f5deb3').pack(side="left", padx=(30, 10))

        n_var = tk.StringVar(value="1000")
        tk.Entry(fila2, textvariable=n_var, width=10,
                font=("Segoe UI", 9),
                bg='#d4a574', fg='#4b2e05').pack(side="left", padx=5)

        # FILA 3: Parámetros + Botón Generar
        fila3 = tk.Frame(config_inner, bg='#6b4423')
        fila3.pack(fill="x", pady=5)

        tk.Label(fila3, text="Parámetros:", font=("Segoe UI", 10, "bold"),
                bg='#6b4423', fg='#f5deb3').pack(side="left", padx=(0, 10))

        param1_label = tk.Label(fila3, text="p:", font=("Segoe UI", 10),
                                bg='#6b4423', fg='#f5deb3')
        param1_label.pack(side="left", padx=5)

        param1_var = tk.StringVar(value="0.5")
        tk.Entry(fila3, textvariable=param1_var, width=10,
                font=("Segoe UI", 9),
                bg='#d4a574', fg='#4b2e05').pack(side="left", padx=5)

        param2_label = tk.Label(fila3, text="", font=("Segoe UI", 10),
                                bg='#6b4423', fg='#f5deb3')
        param2_var = tk.StringVar()
        param2_entry = tk.Entry(fila3, textvariable=param2_var, width=10,
                                font=("Segoe UI", 9),
                                bg='#d4a574', fg='#4b2e05')

        # Botón Generar Datos
        btn_generar = tk.Button(fila3, text="Generar Datos",
                font=("Segoe UI", 10, "bold"),
                bg='#c19a6b', fg='#4b2e05',
                activebackground='#a67c52',
                activeforeground='#ffffff',
                relief='flat', cursor='hand2',
                width=15, height=1)
        btn_generar.pack(side="right", padx=10)

        def actualizar_parametros(*args):
            dist = dist_var.get()
            param2_label.pack_forget()
            param2_entry.pack_forget()
            
            if dist == "Bernoulli":
                param1_label.config(text="p:")
                param1_var.set("0.5")
            elif dist == "Binomial":
                param1_label.config(text="n:")
                param1_var.set("10")
                param2_label.config(text="p:")
                param2_var.set("0.5")
                param2_label.pack(side="left", padx=(15, 5))
                param2_entry.pack(side="left", padx=5)
            elif dist == "Poisson":
                param1_label.config(text="λ:")
                param1_var.set("3.0")
            elif dist == "Uniforme":
                param1_label.config(text="a:")
                param1_var.set("0")
                param2_label.config(text="b:")
                param2_var.set("1")
                param2_label.pack(side="left", padx=(15, 5))
                param2_entry.pack(side="left", padx=5)
            elif dist == "Exponencial":
                param1_label.config(text="λ:")
                param1_var.set("1.0")
            elif dist == "Normal":
                param1_label.config(text="μ:")
                param1_var.set("0")
                param2_label.config(text="σ:")
                param2_var.set("1")
                param2_label.pack(side="left", padx=(15, 5))
                param2_entry.pack(side="left", padx=5)
        
        dist_var.trace('w', actualizar_parametros)

        # === ÁREA DE RESULTADOS ===
        resultados_frame = tk.Frame(main_frame, bg='#8b6f47')
        resultados_frame.pack(fill="both", expand=True, padx=40, pady=(0, 10))

        # Gráfico
        grafico_frame = tk.LabelFrame(resultados_frame, text="Visualización", 
                                    font=("Segoe UI", 11, "bold"),
                                    bg='#6b4423', fg='#f5deb3', 
                                    relief='solid', bd=2)
        grafico_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        fig = Figure(figsize=(8, 6), dpi=100, facecolor='#6b4423')
        ax = fig.add_subplot(111, facecolor='#8b5a3c')
        ax.set_xlabel('Valor', color='#f5deb3')
        ax.set_ylabel('Frecuencia', color='#f5deb3')
        ax.tick_params(colors='#f5deb3')

        canvas_grafico = FigureCanvasTkAgg(fig, grafico_frame)
        canvas_grafico.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        # Panel derecho (datos + estadísticas)
        datos_frame = tk.LabelFrame(resultados_frame, text="Datos y Estadísticas", 
                                    font=("Segoe UI", 11, "bold"),
                                    bg='#6b4423', fg='#f5deb3', 
                                    relief='solid', bd=2, width=380)
        datos_frame.pack(side="right", fill="both", padx=0)
        datos_frame.pack_propagate(False)

        # Datos generados
        datos_text = scrolledtext.ScrolledText(datos_frame, wrap=tk.WORD, 
                                            width=40, height=18,
                                            font=("Courier", 9),
                                            bg='#8b5a3c', fg='#f5deb3',
                                            insertbackground='#f5deb3')
        datos_text.pack(fill="both", expand=True, padx=8, pady=8)

        # Estadísticas
        stats_frame = tk.LabelFrame(datos_frame, text="Estadísticas", 
                                    font=("Segoe UI", 10, "bold"),
                                    bg='#6b4423', fg='#f5deb3')
        stats_frame.pack(fill="x", padx=8, pady=(0, 8))

        stats_text = tk.Text(stats_frame, height=6, width=40,
                            font=("Courier", 9), bg='#8b5a3c', 
                            fg='#d4a574', relief='flat')
        stats_text.pack(padx=5, pady=5)

        # Variables para almacenar datos y generador
        datos_generados = []
        generador_actual = [None]  # Lista para permitir modificación en función anidada

        def generar_datos():
            try:
                n = int(n_var.get())
                if n <= 0 or n > 1000000:
                    messagebox.showerror("Error", "El número de valores debe estar entre 1 y 1,000,000", parent=ventana)
                    return
                
                # Obtener o generar semilla
                if auto_semilla.get():
                    semilla = None
                else:
                    semilla_texto = semilla_var.get().strip()
                    if semilla_texto:
                        try:
                            semilla = int(semilla_texto)
                        except:
                            messagebox.showerror("Error", "La semilla debe ser un número entero", parent=ventana)
                            return
                    else:
                        semilla = None
                
                gen = GeneradorAleatorios(semilla)
                generador_actual[0] = gen
                
                dist = dist_var.get()
                
                # Validaciones y generación según distribución
                if dist == "Bernoulli":
                    try:
                        p = float(param1_var.get())
                        if not 0 <= p <= 1:
                            messagebox.showerror("Error", "El parámetro p debe estar entre 0 y 1", parent=ventana)
                            return
                        datos = gen.bernoulli(p, n)
                    except ValueError:
                        messagebox.showerror("Error", "El parámetro p debe ser un número válido", parent=ventana)
                        return
                
                elif dist == "Binomial":
                    try:
                        n_trials = int(param1_var.get())
                        p = float(param2_var.get())
                        if n_trials <= 0:
                            messagebox.showerror("Error", "El parámetro n debe ser mayor a 0", parent=ventana)
                            return
                        if not 0 <= p <= 1:
                            messagebox.showerror("Error", "El parámetro p debe estar entre 0 y 1", parent=ventana)
                            return
                        datos = gen.binomial(n_trials, p, n)
                    except ValueError:
                        messagebox.showerror("Error", "Los parámetros deben ser números válidos", parent=ventana)
                        return
                
                elif dist == "Poisson":
                    try:
                        lambd = float(param1_var.get())
                        if lambd <= 0:
                            messagebox.showerror("Error", "El parámetro λ debe ser mayor a 0", parent=ventana)
                            return
                        datos = gen.poisson(lambd, n)
                    except ValueError:
                        messagebox.showerror("Error", "El parámetro λ debe ser un número válido", parent=ventana)
                        return
                
                elif dist == "Uniforme":
                    try:
                        a = float(param1_var.get())
                        b = float(param2_var.get())
                        if a >= b:
                            messagebox.showerror("Error", "El parámetro a debe ser menor que b", parent=ventana)
                            return
                        datos = gen.uniforme(a, b, n)
                    except ValueError:
                        messagebox.showerror("Error", "Los parámetros deben ser números válidos", parent=ventana)
                        return
                
                elif dist == "Exponencial":
                    try:
                        lambd = float(param1_var.get())
                        if lambd <= 0:
                            messagebox.showerror("Error", "El parámetro λ debe ser mayor a 0", parent=ventana)
                            return
                        datos = gen.exponencial(lambd, n)
                    except ValueError:
                        messagebox.showerror("Error", "El parámetro λ debe ser un número válido", parent=ventana)
                        return
                
                elif dist == "Normal":
                    try:
                        mu = float(param1_var.get())
                        sigma = float(param2_var.get())
                        if sigma <= 0:
                            messagebox.showerror("Error", "La desviación estándar σ debe ser mayor a 0", parent=ventana)
                            return
                        datos = gen.normal(mu, sigma, n)
                    except ValueError:
                        messagebox.showerror("Error", "Los parámetros deben ser números válidos", parent=ventana)
                        return
                
                # Guardar datos generados
                datos_generados.clear()
                datos_generados.extend(datos)
                
                # Actualizar gráfico
                ax.clear()
                if tipo_var.get() == "Discreta":
                    valores_unicos = sorted(set(datos))
                    frecuencias = [datos.count(v) for v in valores_unicos]
                    ax.bar(valores_unicos, frecuencias, color='#c19a6b', alpha=0.8, edgecolor='#4b2e05')
                else:
                    ax.hist(datos, bins=50, color='#c19a6b', alpha=0.8, edgecolor='#f5deb3')
                
                ax.set_title(f'Distribución {dist}', color='#f5deb3', fontsize=12, fontweight='bold')
                ax.set_xlabel('Valor', color='#f5deb3')
                ax.set_ylabel('Frecuencia', color='#f5deb3')
                ax.tick_params(colors='#f5deb3')
                ax.grid(True, alpha=0.3, color='#f5deb3')
                canvas_grafico.draw()
                
                # Mostrar datos
                datos_text.delete(1.0, tk.END)
                datos_text.insert(tk.END, f"═══════════════════════════════════════\n")
                datos_text.insert(tk.END, f"  DATOS GENERADOS\n")
                datos_text.insert(tk.END, f"═══════════════════════════════════════\n\n")
                datos_text.insert(tk.END, f"Primeros 100 valores:\n\n")
                
                for i, valor in enumerate(datos[:100]):
                    datos_text.insert(tk.END, f"{valor:.4f}  ")
                    if (i + 1) % 5 == 0:
                        datos_text.insert(tk.END, "\n")
                
                if len(datos) > 100:
                    datos_text.insert(tk.END, f"\n\n{'─'*39}\n")
                    datos_text.insert(tk.END, f"💾 Se generaron {len(datos)} valores en total\n")
                    datos_text.insert(tk.END, f"📊 Mostrando solo los primeros 100\n")
                    datos_text.insert(tk.END, f"💡 Usa 'Exportar Datos' para ver todos\n")
                    datos_text.insert(tk.END, f"{'─'*39}\n")
                
                # Auto-scroll al inicio
                datos_text.see("1.0")
                
                # Actualizar estadísticas
                stats_text.delete(1.0, tk.END)
                media = np.mean(datos)
                desv_std = np.std(datos)
                varianza = np.var(datos)
                minimo = np.min(datos)
                maximo = np.max(datos)
                mediana = np.median(datos)
                
                stats_info = f"""Media:          {media:.4f}
Desv. Est.:     {desv_std:.4f}
Varianza:       {varianza:.4f}
Mínimo:         {minimo:.4f}
Máximo:         {maximo:.4f}
Mediana:        {mediana:.4f}
Total valores:  {len(datos)}
Semilla usada:  {gen.semilla}"""
                
                stats_text.insert(tk.END, stats_info)
                
                messagebox.showinfo("Éxito", f"Se generaron {len(datos)} valores exitosamente", parent=ventana)
                
            except ValueError as e:
                messagebox.showerror("Error", f"Parámetros inválidos: {str(e)}", parent=ventana)
            except Exception as e:
                messagebox.showerror("Error", f"Error al generar datos: {str(e)}", parent=ventana)

        # Conectar el botón con la función
        btn_generar.config(command=generar_datos)

        def exportar_datos():
            if not datos_generados:
                messagebox.showwarning("Advertencia", "No hay datos para exportar", parent=ventana)
                return
            
            archivo = filedialog.asksaveasfilename(
                parent=ventana,
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("CSV", "*.csv"), ("Todos los archivos", "*.*")]
            )
            
            if archivo:
                try:
                    es_csv = archivo.lower().endswith('.csv')
                    
                    with open(archivo, 'w', encoding='utf-8') as f:
                        if es_csv:
                            # Formato CSV
                            f.write("indice,valor\n")
                            for i, valor in enumerate(datos_generados, 1):
                                f.write(f"{i},{valor:.6f}\n")
                        else:
                            # Formato texto detallado
                            f.write(f"{'='*70}\n")
                            f.write(f"SimuStats - Datos Generados\n")
                            f.write(f"{'='*70}\n\n")
                            f.write(f"Distribución:      {dist_var.get()}\n")
                            f.write(f"Tipo:              {tipo_var.get()}\n")
                            f.write(f"Fecha y hora:      {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write(f"Semilla utilizada: {generador_actual[0].semilla if generador_actual[0] else 'N/A'}\n")
                            f.write(f"Total de valores:  {len(datos_generados)}\n\n")
                            
                            # Parámetros
                            f.write(f"{'='*70}\n")
                            f.write(f"PARÁMETROS DE LA DISTRIBUCIÓN\n")
                            f.write(f"{'='*70}\n")
                            dist = dist_var.get()
                            if dist == "Bernoulli":
                                f.write(f"p: {param1_var.get()}\n")
                            elif dist == "Binomial":
                                f.write(f"n: {param1_var.get()}\n")
                                f.write(f"p: {param2_var.get()}\n")
                            elif dist == "Poisson":
                                f.write(f"λ: {param1_var.get()}\n")
                            elif dist == "Uniforme":
                                f.write(f"a: {param1_var.get()}\n")
                                f.write(f"b: {param2_var.get()}\n")
                            elif dist == "Exponencial":
                                f.write(f"λ: {param1_var.get()}\n")
                            elif dist == "Normal":
                                f.write(f"μ: {param1_var.get()}\n")
                                f.write(f"σ: {param2_var.get()}\n")
                            
                            # Estadísticas
                            f.write(f"\n{'='*70}\n")
                            f.write(f"ESTADÍSTICAS DESCRIPTIVAS\n")
                            f.write(f"{'='*70}\n")
                            f.write(f"Media:              {np.mean(datos_generados):.6f}\n")
                            f.write(f"Desviación estándar: {np.std(datos_generados):.6f}\n")
                            f.write(f"Varianza:           {np.var(datos_generados):.6f}\n")
                            f.write(f"Mínimo:             {np.min(datos_generados):.6f}\n")
                            f.write(f"Máximo:             {np.max(datos_generados):.6f}\n")
                            f.write(f"Mediana:            {np.median(datos_generados):.6f}\n")
                            
                            # Datos
                            f.write(f"\n{'='*70}\n")
                            f.write(f"DATOS GENERADOS\n")
                            f.write(f"{'='*70}\n\n")
                            
                            for i, valor in enumerate(datos_generados, 1):
                                f.write(f"{i:6d}. {valor:.6f}\n")
                    
                    messagebox.showinfo("Éxito", f"Datos exportados exitosamente a:\n{archivo}", parent=ventana)
                except Exception as e:
                    messagebox.showerror("Error", f"Error al exportar: {str(e)}", parent=ventana)

        # === BOTONES INFERIORES ===
        botones_frame = tk.Frame(main_frame, bg='#8b6f47')
        botones_frame.pack(fill="x", padx=40, pady=(5, 10))

        btn_style = {
            'font': ("Segoe UI", 10, "bold"),
            'relief': 'flat',
            'cursor': 'hand2',
            'width': 16,
            'height': 1
        }

        tk.Button(botones_frame, text="Exportar Datos", command=exportar_datos,
                bg='#8b5a3c', fg='#f5deb3',
                activebackground='#6b4423',
                activeforeground='#ffffff',
                **btn_style).pack(side="left", padx=5)

        tk.Button(botones_frame, text="Cerrar Ventana", command=ventana.destroy,
                bg='#a0522d', fg='#f5deb3',
                activebackground='#8b4513',
                activeforeground='#ffffff',
                **btn_style).pack(side="left", padx=5)

        # === BOTÓN VOLVER AL MENÚ ===
        btn_volver = tk.Button(main_frame, text="← Volver al Menú Principal",
                            command=lambda: [ventana.destroy(), self.mostrar_menu_principal()],
                            font=("Segoe UI", 12, "bold"),
                            bg='#c19a6b', fg='#4b2e05',
                            activebackground='#a67c52',
                            activeforeground='#ffffff',
                            relief='flat', cursor='hand2',
                            width=30, height=2)
        btn_volver.pack(pady=12)
            
    def ventana_prueba_ajuste(self):
        """Ventana para generar variables aleatorias"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Generación de Variables Aleatorias")
        ventana.state('zoomed')
        ventana.configure(bg="#fcdea6")

        # --- Fondo OPTIMIZADO (reutiliza la imagen pre-cargada) ---
        canvas = tk.Canvas(ventana, 
                        width=self.root.winfo_screenwidth(), 
                        height=self.root.winfo_screenheight(), 
                        highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=self.fondo, anchor="nw")
        canvas.image = self.fondo

        # --- Frame con Scrollbar ---
        # Crear un canvas para el scroll
        scroll_canvas = tk.Canvas(canvas, bg="#b8945f", highlightthickness=0)
        scroll_canvas.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.92)
        
        # Scrollbar vertical
        scrollbar = tk.Scrollbar(scroll_canvas, orient="vertical", command=scroll_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        # Frame scrolleable
        scrollable_frame = tk.Frame(scroll_canvas, bg="#b8945f")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        )
        
        scroll_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Habilitar scroll con rueda del mouse
        def _on_mousewheel(event):
            scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Usar scrollable_frame en lugar de main_frame
        main_frame = scrollable_frame

        # Título
        tk.Label(main_frame, text="Generación de Variables Aleatorias",
                font=("Segoe UI", 18, "bold"),
                bg='#4b2e05', fg='#d4a574').pack(pady=8)

        # === Cuadro de Configuración ===
        config_frame = tk.LabelFrame(main_frame, text="Configuración",
                                    font=("Segoe UI", 10, "bold"),
                                    bg='#6b4423', fg='#f5deb3',
                                    relief='solid', bd=2)
        config_frame.pack(fill="x", padx=30, pady=(5, 8))

        # --- Contenedor interno ---
        config_inner = tk.Frame(config_frame, bg='#6b4423')
        config_inner.pack(fill="x", padx=8, pady=6)

        # FILA 1: Tipo y Distribución
        fila1 = tk.Frame(config_inner, bg='#6b4423')
        fila1.pack(fill="x", pady=3)

        # Tipo de variable
        tk.Label(fila1, text="Tipo:", font=("Segoe UI", 10, "bold"),
                bg='#6b4423', fg='#f5deb3').pack(side="left", padx=(0, 10))

        tipo_var = tk.StringVar(value="Discreta")
        tk.Radiobutton(fila1, text="Discreta", variable=tipo_var, value="Discreta",
                    bg='#6b4423', fg='#f5deb3', selectcolor='#8b5a3c',
                    font=("Segoe UI", 9)).pack(side="left", padx=5)
        tk.Radiobutton(fila1, text="Continua", variable=tipo_var, value="Continua",
                    bg='#6b4423', fg='#f5deb3', selectcolor='#8b5a3c',
                    font=("Segoe UI", 9)).pack(side="left", padx=5)

        # Distribución
        tk.Label(fila1, text="Distribución:", font=("Segoe UI", 10, "bold"),
                bg='#6b4423', fg='#f5deb3').pack(side="left", padx=(30, 10))

        dist_var = tk.StringVar()
        dist_combo = ttk.Combobox(fila1, textvariable=dist_var,
                                values=["Bernoulli", "Binomial", "Poisson"],
                                state="readonly", width=15, font=("Segoe UI", 9))
        dist_combo.pack(side="left", padx=5)
        dist_combo.current(0)

        def actualizar_distribuciones(*args):
            if tipo_var.get() == "Discreta":
                dist_combo['values'] = ["Bernoulli", "Binomial", "Poisson"]
            else:
                dist_combo['values'] = ["Uniforme", "Exponencial", "Normal"]
            dist_combo.current(0)
        tipo_var.trace('w', actualizar_distribuciones)

        # FILA 2: Semilla y N valores
        fila2 = tk.Frame(config_inner, bg='#6b4423')
        fila2.pack(fill="x", pady=3)

        tk.Label(fila2, text="Semilla:", font=("Segoe UI", 10, "bold"),
                bg='#6b4423', fg='#f5deb3').pack(side="left", padx=(0, 10))

        semilla_var = tk.StringVar()
        semilla_entry = tk.Entry(fila2, textvariable=semilla_var,
                                width=12, font=("Segoe UI", 9),
                                bg='#d4a574', fg='#4b2e05')
        semilla_entry.pack(side="left", padx=5)

        auto_semilla = tk.BooleanVar(value=True)
        tk.Checkbutton(fila2, text="Auto", variable=auto_semilla,
                    bg='#6b4423', fg='#f5deb3', selectcolor='#8b5a3c',
                    font=("Segoe UI", 9),
                    command=lambda: semilla_entry.config(
                        state='disabled' if auto_semilla.get() else 'normal')).pack(side="left", padx=5)
        semilla_entry.config(state='disabled')

        tk.Label(fila2, text="N° valores:", font=("Segoe UI", 10, "bold"),
                bg='#6b4423', fg='#f5deb3').pack(side="left", padx=(30, 10))

        n_var = tk.StringVar(value="1000")
        tk.Entry(fila2, textvariable=n_var, width=10,
                font=("Segoe UI", 9),
                bg='#d4a574', fg='#4b2e05').pack(side="left", padx=5)

        # FILA 3: Parámetros + Botón Generar
        fila3 = tk.Frame(config_inner, bg='#6b4423')
        fila3.pack(fill="x", pady=3)

        tk.Label(fila3, text="Parámetros:", font=("Segoe UI", 10, "bold"),
                bg='#6b4423', fg='#f5deb3').pack(side="left", padx=(0, 10))

        param1_label = tk.Label(fila3, text="p:", font=("Segoe UI", 10),
                                bg='#6b4423', fg='#f5deb3')
        param1_label.pack(side="left", padx=5)

        param1_var = tk.StringVar(value="0.5")
        tk.Entry(fila3, textvariable=param1_var, width=10,
                font=("Segoe UI", 9),
                bg='#d4a574', fg='#4b2e05').pack(side="left", padx=5)

        param2_label = tk.Label(fila3, text="", font=("Segoe UI", 10),
                                bg='#6b4423', fg='#f5deb3')
        param2_var = tk.StringVar()
        param2_entry = tk.Entry(fila3, textvariable=param2_var, width=10,
                                font=("Segoe UI", 9),
                                bg='#d4a574', fg='#4b2e05')

        # Botón Generar Datos
        btn_generar = tk.Button(fila3, text="Generar Datos",
                font=("Segoe UI", 10, "bold"),
                bg='#c19a6b', fg='#4b2e05',
                activebackground='#a67c52',
                activeforeground='#ffffff',
                relief='flat', cursor='hand2',
                width=15, height=1)
        btn_generar.pack(side="right", padx=10)

        def actualizar_parametros(*args):
            dist = dist_var.get()
            param2_label.pack_forget()
            param2_entry.pack_forget()
            
            if dist == "Bernoulli":
                param1_label.config(text="p:")
                param1_var.set("0.5")
            elif dist == "Binomial":
                param1_label.config(text="n:")
                param1_var.set("10")
                param2_label.config(text="p:")
                param2_var.set("0.5")
                param2_label.pack(side="left", padx=(15, 5))
                param2_entry.pack(side="left", padx=5)
            elif dist == "Poisson":
                param1_label.config(text="λ:")
                param1_var.set("3.0")
            elif dist == "Uniforme":
                param1_label.config(text="a:")
                param1_var.set("0")
                param2_label.config(text="b:")
                param2_var.set("1")
                param2_label.pack(side="left", padx=(15, 5))
                param2_entry.pack(side="left", padx=5)
            elif dist == "Exponencial":
                param1_label.config(text="λ:")
                param1_var.set("1.0")
            elif dist == "Normal":
                param1_label.config(text="μ:")
                param1_var.set("0")
                param2_label.config(text="σ:")
                param2_var.set("1")
                param2_label.pack(side="left", padx=(15, 5))
                param2_entry.pack(side="left", padx=5)
        
        dist_var.trace('w', actualizar_parametros)

        # === ÁREA DE RESULTADOS ===
        resultados_frame = tk.Frame(main_frame, bg='#8b6f47', height=450)
        resultados_frame.pack(fill="x", padx=30, pady=(0, 5))
        resultados_frame.pack_propagate(False)

        # Gráfico
        grafico_frame = tk.LabelFrame(resultados_frame, text="Visualización", 
                                    font=("Segoe UI", 10, "bold"),
                                    bg='#6b4423', fg='#f5deb3', 
                                    relief='solid', bd=2, height=440)
        grafico_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))
        grafico_frame.pack_propagate(False)

        fig = Figure(figsize=(6, 4), dpi=90, facecolor='#6b4423')
        ax = fig.add_subplot(111, facecolor='#8b5a3c')
        ax.set_xlabel('Valor', color='#f5deb3')
        ax.set_ylabel('Frecuencia', color='#f5deb3')
        ax.tick_params(colors='#f5deb3')

        canvas_grafico = FigureCanvasTkAgg(fig, grafico_frame)
        canvas_grafico.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        # Panel derecho (datos + estadísticas)
        datos_frame = tk.LabelFrame(resultados_frame, text="Datos y Estadísticas", 
                                    font=("Segoe UI", 10, "bold"),
                                    bg='#6b4423', fg='#f5deb3', 
                                    relief='solid', bd=2, width=350, height=440)
        datos_frame.pack(side="right", fill="both", padx=0)
        datos_frame.pack_propagate(False)

        # Datos generados
        datos_text = scrolledtext.ScrolledText(datos_frame, wrap=tk.WORD, 
                                            width=38, height=15,
                                            font=("Courier", 8),
                                            bg='#8b5a3c', fg='#f5deb3',
                                            insertbackground='#f5deb3')
        datos_text.pack(fill="both", expand=True, padx=6, pady=6)

        # Estadísticas
        stats_frame = tk.LabelFrame(datos_frame, text="Estadísticas", 
                                    font=("Segoe UI", 9, "bold"),
                                    bg='#6b4423', fg='#f5deb3')
        stats_frame.pack(fill="x", padx=6, pady=(0, 6))

        stats_text = tk.Text(stats_frame, height=7, width=38,
                            font=("Courier", 8), bg='#8b5a3c', 
                            fg='#d4a574', relief='flat')
        stats_text.pack(padx=4, pady=4)

        # Variables para almacenar datos y generador
        datos_generados = []
        generador_actual = [None]  # Lista para permitir modificación en función anidada

        def generar_datos():
            try:
                n = int(n_var.get())
                if n <= 0 or n > 1000000:
                    messagebox.showerror("Error", "El número de valores debe estar entre 1 y 1,000,000", parent=ventana)
                    return
                
                # Obtener o generar semilla
                if auto_semilla.get():
                    semilla = None
                else:
                    semilla_texto = semilla_var.get().strip()
                    if semilla_texto:
                        try:
                            semilla = int(semilla_texto)
                        except:
                            messagebox.showerror("Error", "La semilla debe ser un número entero", parent=ventana)
                            return
                    else:
                        semilla = None
                
                gen = GeneradorAleatorios(semilla)
                generador_actual[0] = gen
                
                dist = dist_var.get()
                
                # Validaciones y generación según distribución
                if dist == "Bernoulli":
                    try:
                        p = float(param1_var.get())
                        if not 0 <= p <= 1:
                            messagebox.showerror("Error", "El parámetro p debe estar entre 0 y 1", parent=ventana)
                            return
                        datos = gen.bernoulli(p, n)
                    except ValueError:
                        messagebox.showerror("Error", "El parámetro p debe ser un número válido", parent=ventana)
                        return
                
                elif dist == "Binomial":
                    try:
                        n_trials = int(param1_var.get())
                        p = float(param2_var.get())
                        if n_trials <= 0:
                            messagebox.showerror("Error", "El parámetro n debe ser mayor a 0", parent=ventana)
                            return
                        if not 0 <= p <= 1:
                            messagebox.showerror("Error", "El parámetro p debe estar entre 0 y 1", parent=ventana)
                            return
                        datos = gen.binomial(n_trials, p, n)
                    except ValueError:
                        messagebox.showerror("Error", "Los parámetros deben ser números válidos", parent=ventana)
                        return
                
                # Guardar datos generados
                datos_generados.clear()
                datos_generados.extend(datos)
                
                # Actualizar gráfico
                ax.clear()
                if tipo_var.get() == "Discreta":
                    valores_unicos = sorted(set(datos))
                    frecuencias = [datos.count(v) for v in valores_unicos]
                    ax.bar(valores_unicos, frecuencias, color='#c19a6b', alpha=0.8, edgecolor='#4b2e05')
                else:
                    ax.hist(datos, bins=50, color='#c19a6b', alpha=0.8, edgecolor='#f5deb3')
                
                ax.set_title(f'Distribución {dist}', color='#f5deb3', fontsize=12, fontweight='bold')
                ax.set_xlabel('Valor', color='#f5deb3')
                ax.set_ylabel('Frecuencia', color='#f5deb3')
                ax.tick_params(colors='#f5deb3')
                ax.grid(True, alpha=0.3, color='#f5deb3')
                canvas_grafico.draw()
                
                # Mostrar datos
                datos_text.delete(1.0, tk.END)
                datos_text.insert(tk.END, f"═══════════════════════════════════════\n")
                datos_text.insert(tk.END, f"  DATOS GENERADOS\n")
                datos_text.insert(tk.END, f"═══════════════════════════════════════\n\n")
                datos_text.insert(tk.END, f"Primeros 100 valores:\n\n")
                
                for i, valor in enumerate(datos[:100]):
                    datos_text.insert(tk.END, f"{valor:.4f}  ")
                    if (i + 1) % 5 == 0:
                        datos_text.insert(tk.END, "\n")
                
                if len(datos) > 100:
                    datos_text.insert(tk.END, f"\n\n{'─'*39}\n")
                    datos_text.insert(tk.END, f"💾 Se generaron {len(datos)} valores en total\n")
                    datos_text.insert(tk.END, f"📊 Mostrando solo los primeros 100\n")
                    datos_text.insert(tk.END, f"💡 Usa 'Exportar Datos' para ver todos\n")
                    datos_text.insert(tk.END, f"{'─'*39}\n")
                
                # Auto-scroll al inicio
                datos_text.see("1.0")
                
                # Actualizar estadísticas
                stats_text.delete(1.0, tk.END)
                media = np.mean(datos)
                desv_std = np.std(datos)
                varianza = np.var(datos)
                minimo = np.min(datos)
                maximo = np.max(datos)
                mediana = np.median(datos)
                
                stats_info = f"""Media:          {media:.4f}
Desv. Est.:     {desv_std:.4f}
Varianza:       {varianza:.4f}
Mínimo:         {minimo:.4f}
Máximo:         {maximo:.4f}
Mediana:        {mediana:.4f}
Total valores:  {len(datos)}
Semilla usada:  {gen.semilla}"""
                
                stats_text.insert(tk.END, stats_info)
                
                messagebox.showinfo("Éxito", f"Se generaron {len(datos)} valores exitosamente", parent=ventana)
                
            except ValueError as e:
                messagebox.showerror("Error", f"Parámetros inválidos: {str(e)}", parent=ventana)
            except Exception as e:
                messagebox.showerror("Error", f"Error al generar datos: {str(e)}", parent=ventana)

        # Conectar el botón con la función
        btn_generar.config(command=generar_datos)

        def exportar_datos():
            """
            Exporta los datos generados a un archivo de texto o CSV
            y también guarda el gráfico como imagen PNG.
            """
            if not datos_generados:
                messagebox.showwarning("Advertencia", "No hay datos para exportar", parent=ventana)
                return
            
            archivo = filedialog.asksaveasfilename(
                parent=ventana,
                title="Guardar datos generados",
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("CSV", "*.csv"), ("Todos los archivos", "*.*")]
            )
            
            if archivo:
                try:
                    es_csv = archivo.lower().endswith('.csv')
                    
                    # Exportar datos en texto/CSV con UTF-8
                    with open(archivo, 'w', encoding='utf-8') as f:
                        if es_csv:
                            # Formato CSV
                            f.write("indice,valor\n")
                            for i, valor in enumerate(datos_generados, 1):
                                f.write(f"{i},{valor:.6f}\n")
                        else:
                            # Formato texto detallado
                            f.write(f"{'='*70}\n")
                            f.write(f"SimuStats - Datos Generados\n")
                            f.write(f"{'='*70}\n\n")
                            f.write(f"Distribución:      {dist_var.get()}\n")
                            f.write(f"Tipo:              {tipo_var.get()}\n")
                            f.write(f"Fecha y hora:      {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write(f"Semilla utilizada: {generador_actual[0].semilla if generador_actual[0] else 'N/A'}\n")
                            f.write(f"Total de valores:  {len(datos_generados)}\n\n")
                            
                            # Parámetros
                            f.write(f"{'='*70}\n")
                            f.write(f"PARÁMETROS DE LA DISTRIBUCIÓN\n")
                            f.write(f"{'='*70}\n")
                            dist = dist_var.get()
                            if dist == "Bernoulli":
                                f.write(f"p: {param1_var.get()}\n")
                            elif dist == "Binomial":
                                f.write(f"n: {param1_var.get()}\n")
                                f.write(f"p: {param2_var.get()}\n")
                            elif dist == "Poisson":
                                f.write(f"λ: {param1_var.get()}\n")
                            elif dist == "Uniforme":
                                f.write(f"a: {param1_var.get()}\n")
                                f.write(f"b: {param2_var.get()}\n")
                            elif dist == "Exponencial":
                                f.write(f"λ: {param1_var.get()}\n")
                            elif dist == "Normal":
                                f.write(f"μ: {param1_var.get()}\n")
                                f.write(f"σ: {param2_var.get()}\n")
                            
                            # Estadísticas
                            f.write(f"\n{'='*70}\n")
                            f.write(f"ESTADÍSTICAS DESCRIPTIVAS\n")
                            f.write(f"{'='*70}\n")
                            f.write(f"Media:               {np.mean(datos_generados):.6f}\n")
                            f.write(f"Desviación estándar: {np.std(datos_generados):.6f}\n")
                            f.write(f"Varianza:            {np.var(datos_generados):.6f}\n")
                            f.write(f"Mínimo:              {np.min(datos_generados):.6f}\n")
                            f.write(f"Máximo:              {np.max(datos_generados):.6f}\n")
                            f.write(f"Mediana:             {np.median(datos_generados):.6f}\n")
                            
                            # Datos
                            f.write(f"\n{'='*70}\n")
                            f.write(f"DATOS GENERADOS\n")
                            f.write(f"{'='*70}\n\n")
                            
                            for i, valor in enumerate(datos_generados, 1):
                                f.write(f"{i:6d}. {valor:.6f}\n")
                    
                    # Exportar gráfico como imagen PNG
                    archivo_grafico = archivo.replace('.txt', '_grafico.png').replace('.csv', '_grafico.png')
                    fig.savefig(archivo_grafico, dpi=300, bbox_inches='tight', facecolor='#6b4423')
                    
                    messagebox.showinfo(
                        "Éxito", 
                        f"Datos exportados exitosamente:\n\n"
                        f"Archivo: {archivo}\n"
                        f"Gráfico: {archivo_grafico}",
                        parent=ventana
                    )
                except Exception as e:
                    messagebox.showerror("Error", f"Error al exportar: {str(e)}", parent=ventana)

        # === BOTONES INFERIORES ===
        botones_frame = tk.Frame(main_frame, bg='#b8945f')
        botones_frame.pack(fill="x", padx=30, pady=(3, 5))

        btn_style = {
            'font': ("Segoe UI", 10, "bold"),
            'relief': 'flat',
            'cursor': 'hand2',
            'width': 18,
            'height': 1
        }

        btn_exportar = tk.Button(botones_frame, text="Exportar Datos", command=exportar_datos,
                bg='#8b5a3c', fg='#f5deb3',
                activebackground='#6b4423',
                activeforeground='#ffffff',
                **btn_style)
        btn_exportar.pack(side="left", padx=8)

        btn_cerrar = tk.Button(botones_frame, text="Cerrar Ventana", command=ventana.destroy,
                bg='#a0522d', fg='#f5deb3',
                activebackground='#8b4513',
                activeforeground='#ffffff',
                **btn_style)
        btn_cerrar.pack(side="left", padx=8)

        # Efectos hover
        btn_exportar.bind("<Enter>", lambda e: btn_exportar.config(bg='#6b4423'))
        btn_exportar.bind("<Leave>", lambda e: btn_exportar.config(bg='#8b5a3c'))
        btn_cerrar.bind("<Enter>", lambda e: btn_cerrar.config(bg='#8b4513'))
        btn_cerrar.bind("<Leave>", lambda e: btn_cerrar.config(bg='#a0522d'))

        # === BOTÓN VOLVER AL MENÚ ===
        btn_volver = tk.Button(main_frame, text="Volver al Menú Principal",
                            command=lambda: [ventana.destroy(), self.mostrar_menu_principal()],
                            font=("Segoe UI", 10, "bold"),
                            bg='#c19a6b', fg='#4b2e05',
                            activebackground='#a67c52',
                            activeforeground='#ffffff',
                            relief='flat', cursor='hand2',
                            width=28, height=1)
        btn_volver.pack(pady=5)

    def ventana_prueba_ajuste(self):
        """Ventana para pruebas de ajuste de distribuciones con scroll completo"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Prueba de Ajuste de Distribuciones")
        ventana.state('zoomed')  # ventana maximizada
        ventana.configure(bg='#fcdea6')

        # -------------------- Canvas con scroll --------------------
        canvas = tk.Canvas(ventana, bg='#fcdea6', highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(ventana, orient="vertical", command=canvas.yview, width=12)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        frame_interno = tk.Frame(canvas, bg='#fcdea6')
        frame_interno_id = canvas.create_window((0, 0), window=frame_interno, anchor="nw")

        # Ajusta tamaño del frame interno al canvas
        def actualizar_scroll(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(frame_interno_id, width=canvas.winfo_width())

        frame_interno.bind("<Configure>", actualizar_scroll)
        canvas.bind("<Configure>", actualizar_scroll)

        # Scroll con rueda del mouse
        def scroll_con_mouse(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", scroll_con_mouse)
        
        def scroll_arriba(event):
            canvas.yview_scroll(-1, "units")
        def scroll_abajo(event):
            canvas.yview_scroll(1, "units")
        
        canvas.bind_all("<Button-4>", scroll_arriba)
        canvas.bind_all("<Button-5>", scroll_abajo)
        
        def on_close():
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
            ventana.destroy()
        
        ventana.protocol("WM_DELETE_WINDOW", on_close)

        # -------------------- Marco principal --------------------
        main_frame = tk.Frame(frame_interno, bg='#b8945f')
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(main_frame, text="Prueba de Ajuste de Distribuciones",
                font=("Segoe UI", 24, "bold"),
                bg='#4b2e05', fg='#d4a574').pack(pady=10)

        # -------------------- Entrada de Datos --------------------
        entrada_frame = tk.LabelFrame(main_frame, text="Entrada de Datos",
                                    font=("Segoe UI", 11, "bold"),
                                    bg='#6b4423', fg='#f5deb3', relief='solid', bd=2)
        entrada_frame.pack(fill="x", padx=10, pady=10)

        datos_prueba = []

        def cargar_archivo():
            # Mantener ventana al frente
            ventana.attributes('-topmost', True)
            ventana.attributes('-topmost', False)

            archivo = filedialog.askopenfilename(
                parent=ventana,
                title="Seleccionar archivo de datos",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
            )

            ventana.lift()
            ventana.focus_force()

            if archivo:
                try:
                    with open(archivo, 'r') as f:
                        contenido = f.read()
                        numeros = []
                        for linea in contenido.split('\n'):
                            # Reemplazar comas por espacios y separar valores
                            for valor in linea.replace(',', ' ').split():
                                try:
                                    numeros.append(float(valor))
                                except:
                                    pass
                        if numeros:
                            datos_prueba.clear()
                            datos_prueba.extend(numeros)
                            datos_text.delete(1.0, tk.END)
                            datos_text.insert(tk.END, f"Archivo cargado: {archivo}\n")
                            datos_text.insert(tk.END, f"Total de datos: {len(numeros)}\n\n")
                            datos_text.insert(tk.END, "Primeros 50 valores:\n")
                            for i, val in enumerate(numeros[:50]):
                                datos_text.insert(tk.END, f"{val:.4f}  ")
                                if (i + 1) % 5 == 0:
                                    datos_text.insert(tk.END, "\n")
                            messagebox.showinfo("Éxito", f"Se cargaron {len(numeros)} datos correctamente", parent=ventana)
                        else:
                            messagebox.showwarning("Advertencia", "No se encontraron datos válidos en el archivo", parent=ventana)
                except Exception as e:
                    messagebox.showerror("Error", f"Error al cargar archivo: {str(e)}", parent=ventana)

            ventana.lift()

        def ingresar_manual():
            manual_ventana = tk.Toplevel(ventana)
            manual_ventana.title("Ingresar Datos Manualmente")
            manual_ventana.geometry("500x400")
            manual_ventana.configure(bg='#fcdea6')
            
            manual_ventana.transient(ventana)
            manual_ventana.grab_set()
            
            manual_ventana.update_idletasks()
            x = ventana.winfo_x() + (ventana.winfo_width() // 2) - (manual_ventana.winfo_width() // 2)
            y = ventana.winfo_y() + (ventana.winfo_height() // 2) - (manual_ventana.winfo_height() // 2)
            manual_ventana.geometry(f"+{x}+{y}")

            tk.Label(manual_ventana, text="Ingrese los datos separados por comas o espacios:",
                    font=("Segoe UI", 11, "bold"), bg='#fcdea6', fg='#4b2e05').pack(pady=10)

            text_entrada = scrolledtext.ScrolledText(manual_ventana, width=50, height=15,
                                                    font=("Courier", 10), bg='#d4a574',
                                                    fg='#4b2e05', insertbackground='#4b2e05')
            text_entrada.pack(padx=10, pady=10)
            text_entrada.focus_set()

            def procesar_datos():
                try:
                    texto = text_entrada.get(1.0, tk.END)
                    texto = texto.replace(',', ' ').replace('\n', ' ')
                    numeros = [float(x) for x in texto.split() if x.strip()]
                    if numeros:
                        datos_prueba.clear()
                        datos_prueba.extend(numeros)
                        datos_text.delete(1.0, tk.END)
                        datos_text.insert(tk.END, f"Datos ingresados manualmente\n")
                        datos_text.insert(tk.END, f"Total de datos: {len(numeros)}\n\n")
                        datos_text.insert(tk.END, "Primeros 50 valores:\n")
                        for i, val in enumerate(numeros[:50]):
                            datos_text.insert(tk.END, f"{val:.4f}  ")
                            if (i + 1) % 5 == 0:
                                datos_text.insert(tk.END, "\n")
                        manual_ventana.destroy()
                        messagebox.showinfo("Éxito", f"Se ingresaron {len(numeros)} datos correctamente", parent=ventana)
                        ventana.lift()
                        ventana.focus_force()
                    else:
                        messagebox.showwarning("Advertencia", "No se encontraron datos válidos", parent=manual_ventana)
                except Exception as e:
                    messagebox.showerror("Error", f"Error al procesar datos: {str(e)}", parent=manual_ventana)

            btn_frame = tk.Frame(manual_ventana, bg='#fcdea6')
            btn_frame.pack(pady=10)

            tk.Button(btn_frame, text="Aceptar", command=procesar_datos,
                    font=("Segoe UI", 10, "bold"), bg='#4b2e05', fg='#f5deb3',
                    width=15).pack(side="left", padx=5)
            
            tk.Button(btn_frame, text="Cancelar", command=manual_ventana.destroy,
                    font=("Segoe UI", 10, "bold"), bg='#e74c3c', fg='white',
                    width=15).pack(side="left", padx=5)

        btn_frame = tk.Frame(entrada_frame, bg='#6b4423')
        btn_frame.pack(padx=15, pady=10)

        tk.Button(btn_frame, text="Cargar desde Archivo", command=cargar_archivo,
                font=("Segoe UI", 10, "bold"), bg='#d4a574', fg='#4b2e05',
                width=20).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Ingresar Manualmente", command=ingresar_manual,
                font=("Segoe UI", 10, "bold"), bg='#4b2e05', fg='#f5deb3',
                width=20).pack(side="left", padx=5)

        datos_text = scrolledtext.ScrolledText(entrada_frame, height=8, width=80,
                                            font=("Courier", 9), bg='#d4a574',
                                            fg='#4b2e05', insertbackground='#4b2e05')
        datos_text.pack(padx=15, pady=10)

        # -------------------- Configuración de Prueba --------------------
        config_prueba_frame = tk.LabelFrame(main_frame, text="Configuración de Prueba",
                                            font=("Segoe UI", 11, "bold"),
                                            bg='#6b4423', fg='#f5deb3', relief='solid', bd=2)
        config_prueba_frame.pack(fill="x", padx=10, pady=10)

        dist_prueba_frame = tk.Frame(config_prueba_frame, bg='#6b4423')
        dist_prueba_frame.pack(padx=15, pady=10)

        tk.Label(dist_prueba_frame, text="Distribución a probar:",
                font=("Segoe UI", 10, "bold"), bg='#6b4423', fg='#f5deb3').pack(side="left", padx=5)

        dist_var = tk.StringVar()
        dist_combo = ttk.Combobox(dist_prueba_frame, textvariable=dist_var,
                                values=["Normal", "Exponencial", "Uniforme", "Poisson"],
                                state="readonly", width=20, font=("Segoe UI", 10))
        dist_combo.pack(side="left", padx=10)
        dist_combo.current(0)

        tk.Label(dist_prueba_frame, text="Nivel de significancia α:",
                font=("Segoe UI", 10, "bold"), bg='#6b4423', fg='#f5deb3').pack(side="left", padx=(20,5))

        alpha_var = tk.StringVar(value="0.05")
        tk.Entry(dist_prueba_frame, textvariable=alpha_var, width=8,
                font=("Segoe UI", 10)).pack(side="left", padx=5)

        # -------------------- Resultados --------------------
        resultados_frame = tk.Frame(main_frame, bg='#b8945f')
        resultados_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Gráfico
        grafico_frame = tk.LabelFrame(resultados_frame, text="Gráfico Comparativo",
                                    font=("Segoe UI", 11, "bold"),
                                    bg='#6b4423', fg='#f5deb3', relief='solid', bd=2)
        grafico_frame.pack(side="left", fill="both", expand=True, padx=(0,5))

        fig = Figure(figsize=(6,5), dpi=100, facecolor='#6b4423')
        ax = fig.add_subplot(111, facecolor='#d4a574')
        canvas_grafico = FigureCanvasTkAgg(fig, grafico_frame)
        canvas_grafico.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Resultados texto
        resultado_text_frame = tk.LabelFrame(resultados_frame, text="Resultados de la Prueba",
                                            font=("Segoe UI", 11, "bold"),
                                            bg='#6b4423', fg='#f5deb3', relief='solid', bd=2, width=450)
        resultado_text_frame.pack(side="right", fill="both", expand=False, padx=(5,0))
        resultado_text_frame.pack_propagate(False)

        resultados_text = scrolledtext.ScrolledText(resultado_text_frame, wrap=tk.WORD,
                                                    width=45, height=20, font=("Courier", 9),
                                                    bg='#d4a574', fg='#4b2e05', insertbackground='#4b2e05')
        resultados_text.pack(fill="both", expand=True, padx=10, pady=10)

        # -------------------- Función realizar_prueba --------------------
        def realizar_prueba_local():
            if not datos_prueba:
                messagebox.showwarning("Advertencia", "Debe cargar o ingresar datos primero", parent=ventana)
                return
            
            try:
                alpha = float(alpha_var.get())
                if alpha <= 0 or alpha >= 1:
                    messagebox.showerror("Error", "El nivel de significancia debe estar entre 0 y 1", parent=ventana)
                    return
            except:
                messagebox.showerror("Error", "Nivel de significancia inválido", parent=ventana)
                return
            
            distribucion = dist_var.get()
            datos = np.array(datos_prueba)
            
            # Limpiar resultados anteriores
            resultados_text.delete(1.0, tk.END)
            ax.clear()
            
            resultados_text.insert(tk.END, f"═══════════════════════════════════════════\n")
            resultados_text.insert(tk.END, f"  PRUEBA DE AJUSTE DE DISTRIBUCIÓN\n")
            resultados_text.insert(tk.END, f"═══════════════════════════════════════════\n\n")
            resultados_text.insert(tk.END, f"Distribución a probar: {distribucion}\n")
            resultados_text.insert(tk.END, f"Nivel de significancia (α): {alpha}\n")
            resultados_text.insert(tk.END, f"Tamaño de muestra (n): {len(datos)}\n\n")
            
            # Estadísticos descriptivos
            resultados_text.insert(tk.END, f"╔═══════════════════════════════════════╗\n")
            resultados_text.insert(tk.END, f"║   ESTADÍSTICOS DESCRIPTIVOS           ║\n")
            resultados_text.insert(tk.END, f"╚═══════════════════════════════════════╝\n")
            resultados_text.insert(tk.END, f"Media (x̄):              {np.mean(datos):.4f}\n")
            resultados_text.insert(tk.END, f"Mediana:                {np.median(datos):.4f}\n")
            resultados_text.insert(tk.END, f"Desviación estándar(s): {np.std(datos, ddof=1):.4f}\n")
            resultados_text.insert(tk.END, f"Varianza (s²):          {np.var(datos, ddof=1):.4f}\n")
            resultados_text.insert(tk.END, f"Mínimo:                 {np.min(datos):.4f}\n")
            resultados_text.insert(tk.END, f"Máximo:                 {np.max(datos):.4f}\n")
            resultados_text.insert(tk.END, f"Rango:                  {np.max(datos)-np.min(datos):.4f}\n")
            resultados_text.insert(tk.END, f"Cuartil 25%:            {np.percentile(datos, 25):.4f}\n")
            resultados_text.insert(tk.END, f"Cuartil 75%:            {np.percentile(datos, 75):.4f}\n\n")
            
            try:
                from scipy import stats
                
                # ESTIMACIÓN DE PARÁMETROS USANDO .fit()
                if distribucion == "Normal":
                    params = stats.norm.fit(datos)
                    mu, sigma = params[0], params[1]
                    params_text = f"μ = {mu:.4f}, σ = {sigma:.4f}"
                    
                elif distribucion == "Exponencial":
                    params = stats.expon.fit(datos)
                    # expon.fit retorna (loc, scale), scale = 1/λ
                    loc, scale = params[0], params[1]
                    lambd = 1 / scale if scale != 0 else 1
                    params_text = f"λ = {lambd:.4f}"
                    
                elif distribucion == "Uniforme":
                    params = stats.uniform.fit(datos)
                    a, width = params[0], params[1]
                    b = a + width
                    params_text = f"a = {a:.4f}, b = {b:.4f}"
                    
                elif distribucion == "Poisson":
                    # Para Poisson, estimar λ como la media
                    lambd = np.mean(datos)
                    params_text = f"λ = {lambd:.4f}"
                
                resultados_text.insert(tk.END, f"Parámetros estimados: {params_text}\n\n")
                
                # ========== PRUEBA DE KOLMOGOROV-SMIRNOV ==========
                resultados_text.insert(tk.END, f"╔═══════════════════════════════════════╗\n")
                resultados_text.insert(tk.END, f"║   PRUEBA KOLMOGOROV-SMIRNOV (K-S)     ║\n")
                resultados_text.insert(tk.END, f"╚═══════════════════════════════════════╝\n")
                resultados_text.insert(tk.END, f"Hipótesis nula (H₀): Los datos siguen\n")
                resultados_text.insert(tk.END, f"                     la distribución {distribucion}\n\n")
                
                if distribucion == "Normal":
                    ks_stat, ks_pvalue = stats.kstest(datos, 'norm', args=(mu, sigma))
                elif distribucion == "Exponencial":
                    ks_stat, ks_pvalue = stats.kstest(datos, 'expon', args=(loc, scale))
                elif distribucion == "Uniforme":
                    ks_stat, ks_pvalue = stats.kstest(datos, 'uniform', args=(a, b-a))
                elif distribucion == "Poisson":
                    # Para Poisson discreto, usar método manual
                    datos_sorted = np.sort(datos)
                    cdf_empirica = np.arange(1, len(datos)+1) / len(datos)
                    cdf_teorica = stats.poisson.cdf(datos_sorted, lambd)
                    ks_stat = np.max(np.abs(cdf_empirica - cdf_teorica))
                    ks_pvalue = stats.ksone.sf(ks_stat, len(datos))
                
                # Valor crítico K-S
                ks_critico = stats.kstwo.ppf(1-alpha, len(datos))
                
                resultados_text.insert(tk.END, f"Estadístico D:      {ks_stat:.6f}\n")
                resultados_text.insert(tk.END, f"Valor crítico D:    {ks_critico:.6f}\n")
                resultados_text.insert(tk.END, f"Valor p:            {ks_pvalue:.6f}\n\n")
                
                if ks_pvalue > alpha:
                    resultados_text.insert(tk.END, f"✓ Decisión K-S: NO se rechaza H₀\n")
                    resultados_text.insert(tk.END, f"  (p-value = {ks_pvalue:.4f} > α = {alpha})\n\n")
                    conclusion_ks = "AJUSTA"
                else:
                    resultados_text.insert(tk.END, f"✗ Decisión K-S: Se RECHAZA H₀\n")
                    resultados_text.insert(tk.END, f"  (p-value = {ks_pvalue:.4f} ≤ α = {alpha})\n\n")
                    conclusion_ks = "NO AJUSTA"
                
                # ========== PRUEBA CHI-CUADRADO ==========
                resultados_text.insert(tk.END, f"╔═══════════════════════════════════════╗\n")
                resultados_text.insert(tk.END, f"║   PRUEBA CHI-CUADRADO (χ²)            ║\n")
                resultados_text.insert(tk.END, f"╚═══════════════════════════════════════╝\n")
                resultados_text.insert(tk.END, f"Hipótesis nula (H₀): Los datos siguen\n")
                resultados_text.insert(tk.END, f"                     la distribución {distribucion}\n\n")
                
                # Crear intervalos (regla de Sturges)
                k = int(1 + 3.322 * np.log10(len(datos)))
                k = max(5, min(k, 15))
                
                observed, bins = np.histogram(datos, bins=k)
                
                # Calcular frecuencias esperadas ANTES de mostrar tabla
                expected_list = []
                for i in range(len(bins)-1):
                    if distribucion == "Normal":
                        p = stats.norm.cdf(bins[i+1], mu, sigma) - stats.norm.cdf(bins[i], mu, sigma)
                    elif distribucion == "Exponencial":
                        p = stats.expon.cdf(bins[i+1], loc, scale) - stats.expon.cdf(bins[i], loc, scale)
                    elif distribucion == "Uniforme":
                        p = stats.uniform.cdf(bins[i+1], a, b-a) - stats.uniform.cdf(bins[i], a, b-a)
                    elif distribucion == "Poisson":
                        p = stats.poisson.cdf(bins[i+1], lambd) - stats.poisson.cdf(bins[i], lambd)
                    
                    exp_freq = p * len(datos)
                    expected_list.append(exp_freq)
                
                expected = np.array(expected_list)
                observed_orig = observed.copy()
                
                # Combinar intervalos con frecuencias esperadas < 5 ANTES de mostrar
                indices_combinar = []
                while np.any(expected < 5) and len(expected) > 2:
                    idx = np.argmin(expected)
                    indices_combinar.append(idx)
                    if idx == 0:
                        observed[1] += observed[0]
                        expected[1] += expected[0]
                        observed = observed[1:]
                        expected = expected[1:]
                        bins = bins[1:]
                    elif idx == len(expected) - 1:
                        observed[-2] += observed[-1]
                        expected[-2] += expected[-1]
                        observed = observed[:-1]
                        expected = expected[:-1]
                        bins = bins[:-1]
                    else:
                        observed[idx-1] += observed[idx]
                        expected[idx-1] += expected[idx]
                        observed = np.delete(observed, idx)
                        expected = np.delete(expected, idx)
                        bins = np.delete(bins, idx+1)
                
                resultados_text.insert(tk.END, f"Número de intervalos: {len(observed)}\n\n")
                resultados_text.insert(tk.END, f"{'Intervalo':<20} {'Observado':<12} {'Esperado':<12}\n")
                resultados_text.insert(tk.END, f"{'-'*44}\n")
                
                for i in range(len(observed)):
                    intervalo = f"[{bins[i]:.2f}, {bins[i+1]:.2f})"
                    resultados_text.insert(tk.END, f"{intervalo:<20} {observed[i]:<12} {expected[i]:<12.2f}\n")
                
                # Calcular estadístico Chi-cuadrado
                chi2_stat = np.sum((observed - expected)**2 / expected)
                
                # Grados de libertad corregidos
                if distribucion == "Normal":
                    df = len(observed) - 1 - 2
                elif distribucion == "Exponencial":
                    df = len(observed) - 1 - 1
                elif distribucion == "Uniforme":
                    df = len(observed) - 1 - 2
                elif distribucion == "Poisson":
                    df = len(observed) - 1 - 1
                
                df = max(1, df)
                
                chi2_pvalue = 1 - stats.chi2.cdf(chi2_stat, df)
                chi2_critico = stats.chi2.ppf(1-alpha, df)
                
                resultados_text.insert(tk.END, f"\n")
                resultados_text.insert(tk.END, f"Estadístico χ²:     {chi2_stat:.4f}\n")
                resultados_text.insert(tk.END, f"Grados de libertad: {df}\n")
                resultados_text.insert(tk.END, f"Valor crítico χ²:   {chi2_critico:.4f}\n")
                resultados_text.insert(tk.END, f"Valor p:            {chi2_pvalue:.6f}\n\n")
                
                if chi2_pvalue > alpha:
                    resultados_text.insert(tk.END, f"✓ Decisión χ²: NO se rechaza H₀\n")
                    resultados_text.insert(tk.END, f"  (p-value = {chi2_pvalue:.4f} > α = {alpha})\n\n")
                    conclusion_chi = "AJUSTA"
                else:
                    resultados_text.insert(tk.END, f"✗ Decisión χ²: Se RECHAZA H₀\n")
                    resultados_text.insert(tk.END, f"  (p-value = {chi2_pvalue:.4f} ≤ α = {alpha})\n\n")
                    conclusion_chi = "NO AJUSTA"
                
                # ========== CONCLUSIÓN FINAL ==========
                resultados_text.insert(tk.END, f"╔═══════════════════════════════════════╗\n")
                resultados_text.insert(tk.END, f"║   CONCLUSIÓN FINAL                    ║\n")
                resultados_text.insert(tk.END, f"╚═══════════════════════════════════════╝\n")
                
                if conclusion_ks == "AJUSTA" and conclusion_chi == "AJUSTA":
                    resultados_text.insert(tk.END, f"✓✓ AMBAS PRUEBAS CONCUERDAN:\n")
                    resultados_text.insert(tk.END, f"   Los datos SE AJUSTAN a la\n")
                    resultados_text.insert(tk.END, f"   distribución {distribucion}\n")
                    resultados_text.insert(tk.END, f"   (nivel de confianza {(1-alpha)*100}%)\n")
                elif conclusion_ks == "NO AJUSTA" and conclusion_chi == "NO AJUSTA":
                    resultados_text.insert(tk.END, f"✗✗ AMBAS PRUEBAS CONCUERDAN:\n")
                    resultados_text.insert(tk.END, f"   Los datos NO SE AJUSTAN a la\n")
                    resultados_text.insert(tk.END, f"   distribución {distribucion}\n")
                    resultados_text.insert(tk.END, f"   (nivel de confianza {(1-alpha)*100}%)\n")
                else:
                    resultados_text.insert(tk.END, f"⚠ LAS PRUEBAS NO CONCUERDAN:\n")
                    resultados_text.insert(tk.END, f"   K-S: {conclusion_ks}\n")
                    resultados_text.insert(tk.END, f"   χ²:  {conclusion_chi}\n")
                    resultados_text.insert(tk.END, f"   Se recomienda análisis adicional\n")
                
                # ========== GRAFICAR ==========
                ax.clear()
                
                n, bins_plot, patches = ax.hist(datos, bins=k, density=True, alpha=0.6, 
                                            color='#8b6914', edgecolor='black', 
                                            label='Datos observados')
                
                x = np.linspace(np.min(datos) - 0.1*np.std(datos), 
                            np.max(datos) + 0.1*np.std(datos), 1000)
                
                if distribucion == "Normal":
                    y = stats.norm.pdf(x, mu, sigma)
                    ax.plot(x, y, 'r-', linewidth=2.5, label=f'Distribución {distribucion}')
                elif distribucion == "Exponencial":
                    y = stats.expon.pdf(x, loc, scale)
                    ax.plot(x, y, 'r-', linewidth=2.5, label=f'Distribución {distribucion}')
                elif distribucion == "Uniforme":
                    y = stats.uniform.pdf(x, a, b-a)
                    ax.plot(x, y, 'r-', linewidth=2.5, label=f'Distribución {distribucion}')
                elif distribucion == "Poisson":
                    x_discrete = np.arange(int(np.min(datos)), int(np.max(datos))+1)
                    y_discrete = stats.poisson.pmf(x_discrete, lambd)
                    ax.plot(x_discrete, y_discrete, 'ro-', linewidth=2, 
                        markersize=6, label=f'Distribución {distribucion}')
                
                ax.set_xlabel('Valores', fontsize=11, fontweight='bold', color='#4b2e05')
                ax.set_ylabel('Densidad de Probabilidad', fontsize=11, fontweight='bold', color='#4b2e05')
                ax.set_title(f'Ajuste a Distribución {distribucion}\nK-S: {conclusion_ks} | χ²: {conclusion_chi}', 
                            fontsize=12, fontweight='bold', color='#4b2e05')
                ax.legend(loc='best', facecolor='#f5deb3', edgecolor='#4b2e05', fontsize=10)
                ax.grid(True, alpha=0.3, linestyle='--')
                
                if conclusion_ks == "AJUSTA" and conclusion_chi == "AJUSTA":
                    ax.set_facecolor('#e8f5e9')
                elif conclusion_ks == "NO AJUSTA" and conclusion_chi == "NO AJUSTA":
                    ax.set_facecolor('#ffebee')
                else:
                    ax.set_facecolor('#fff9c4')
                
                canvas_grafico.draw()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al realizar la prueba:\n{str(e)}", parent=ventana)
                import traceback
                traceback.print_exc()
            
            ventana.lift()

        # -------------------- Botones --------------------
        botones_frame = tk.Frame(main_frame, bg='#b8945f')
        botones_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(botones_frame, text="Realizar Prueba", command=realizar_prueba_local,
                font=("Segoe UI", 10, "bold"), bg="#d4a574", fg="#4b2e05",
                relief="flat", width=18, height=1, cursor='hand2').pack(side="left", padx=10)
        def exportar_resultados():
            """
            Exporta los resultados de la prueba de ajuste a un archivo de texto
            y también guarda el gráfico como imagen PNG.
            """
            if not resultados_text.get(1.0, tk.END).strip():
                messagebox.showwarning("Advertencia", "No hay resultados para exportar", parent=ventana)
                return
            
            archivo = filedialog.asksaveasfilename(
                parent=ventana,
                title="Guardar resultados",
                defaultextension=".txt",
                filetypes=[("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")]
            )
            
            if archivo:
                try:
                    # Exportar resultados en texto
                    with open(archivo, 'w', encoding='utf-8') as f:
                        f.write(resultados_text.get(1.0, tk.END))
                    
                    # Exportar gráfico como imagen PNG
                    # Cambiar extensión de .txt a .png
                    archivo_grafico = archivo.replace('.txt', '.png')
                    fig.savefig(archivo_grafico, dpi=300, bbox_inches='tight', facecolor='#6b4423')
                    
                    messagebox.showinfo(
                        "Éxito", 
                        f"Resultados exportados correctamente:\n\n"
                        f"Texto: {archivo}\n"
                        f"Gráfico: {archivo_grafico}",
                        parent=ventana
                    )
                except Exception as e:
                    messagebox.showerror("Error", f"Error al exportar: {str(e)}", parent=ventana)
            
            ventana.lift()

        tk.Button(botones_frame, text="Exportar Resultados", command=exportar_resultados,
                font=("Segoe UI", 10, "bold"), bg="#4b2e05", fg="#f5deb3",
                relief="flat", width=18, height=1, cursor='hand2').pack(side="left", padx=10)

        tk.Button(botones_frame, text="Cerrar", command=on_close,
                font=("Segoe UI", 10, "bold"), bg="#e74c3c", fg="white",
                relief="flat", width=12, height=1, cursor='hand2').pack(side="right", padx=10)
            
    def ventana_monte_carlo(self):
        """
        Ventana principal para simulaciones Monte Carlo.
        
        Permite al usuario elegir entre 6 problemas diferentes:
        - Estimación de π
        - Ruina del Jugador (con visualización progresiva)
        - Sistema de Colas
        - Integral Definida
        - Problema de Inventarios
        - Prueba de Hipótesis
        
        Características:
        - Visualización de pasos de simulación
        - Exportación de resultados a archivo
        - Gráficos interactivos
        - Scroll completo en ventana
        """
        ventana = tk.Toplevel(self.root)
        ventana.title("Método de Monte Carlo - Simulaciones")
        ventana.state('zoomed')
        ventana.configure(bg='#fcdea6')

        # -------------------- Canvas con scroll --------------------
        canvas = tk.Canvas(ventana, bg='#fcdea6', highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(ventana, orient="vertical", command=canvas.yview, width=12)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        main_frame = tk.Frame(canvas, bg='#b8945f')
        main_frame_id = canvas.create_window((0, 0), window=main_frame, anchor="nw")

        def actualizar_scroll(event=None):
            """Actualiza el área scrolleable cuando cambia el tamaño del contenido."""
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(main_frame_id, width=canvas.winfo_width())

        main_frame.bind("<Configure>", actualizar_scroll)
        canvas.bind("<Configure>", actualizar_scroll)

        def scroll_con_mouse(event):
            """Permite scroll con rueda del mouse."""
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", scroll_con_mouse)
        
        def scroll_arriba(event):
            """Scroll hacia arriba (Linux)."""
            canvas.yview_scroll(-1, "units")
        
        def scroll_abajo(event):
            """Scroll hacia abajo (Linux)."""
            canvas.yview_scroll(1, "units")
        
        canvas.bind_all("<Button-4>", scroll_arriba)
        canvas.bind_all("<Button-5>", scroll_abajo)
        
        def on_close():
            """Limpia los bindings al cerrar la ventana."""
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
            ventana.destroy()
        
        ventana.protocol("WM_DELETE_WINDOW", on_close)

        tk.Label(main_frame, text="Simulaciones Monte Carlo",
                font=("Segoe UI", 24, "bold"), bg='#4b2e05', fg='#d4a574').pack(pady=10)

        # -------------------- Selector de Problema --------------------
        selector_frame = tk.LabelFrame(main_frame, text="Seleccionar Problema",
                                    font=("Segoe UI", 11, "bold"),
                                    bg='#6b4423', fg='#f5deb3', relief='solid', bd=2)
        selector_frame.pack(fill="x", padx=10, pady=10)

        problema_var = tk.StringVar(value="pi")
        problemas = [
            ("Estimación de π", "pi"),
            ("Ruina del Jugador", "ruina"),
            ("Sistema de Colas", "colas"),
            ("Integral Definida", "integral"),
            ("Problema de Inventarios", "inventarios"),
            ("Prueba de Hipótesis", "hipotesis")
        ]

        for nombre, valor in problemas:
            tk.Radiobutton(selector_frame, text=nombre, variable=problema_var, value=valor,
                        bg='#6b4423', fg='#f5deb3', selectcolor='#d4a574',
                        command=lambda: actualizar_problema()).pack(side="left", padx=5)

        # -------------------- Frame Principal de Contenido --------------------
        contenido_frame = tk.Frame(main_frame, bg='#b8945f')
        contenido_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # -------------------- Frame de Configuración --------------------
        config_frame = tk.LabelFrame(contenido_frame, text="Configuración",
                                    font=("Segoe UI", 11, "bold"),
                                    bg='#6b4423', fg='#f5deb3', relief='solid', bd=2)
        config_frame.pack(fill="x", padx=10, pady=5)

        config_labels = {}
        config_entries = {}
        config_defaults = {
            'pi': {'Número de simulaciones': '5000'},
            'ruina': {'Capital inicial': '100', 'Apuesta por ronda': '1', 'Probabilidad de ganar': '0.5', 'Simulaciones': '1000'},
            'colas': {'Clientes por hora': '30', 'Tiempo servicio promedio (min)': '2', 'Simulaciones': '1000'},
            'integral': {'Número de puntos': '5000', 'Función': 'x**2'},
            'inventarios': {'Demanda promedio': '50', 'Costo unitario': '10', 'Costo ordenar': '100', 'Simulaciones': '1000'},
            'hipotesis': {'Media hipotética (μ₀)': '100', 'Desv. estándar (σ)': '15', 'Tamaño muestra (n)': '30', 'Simulaciones': '5000', 'Nivel significancia (α)': '0.05'}
        }

        def actualizar_problema():
            """Actualiza los campos de configuración según el problema seleccionado."""
            for widget in config_frame.winfo_children():
                if isinstance(widget, tk.Label) or isinstance(widget, tk.Entry):
                    widget.destroy()

            config_labels.clear()
            config_entries.clear()

            problema = problema_var.get()
            defaults = config_defaults.get(problema, {})

            for i, (label_text, default_val) in enumerate(defaults.items()):
                lbl = tk.Label(config_frame, text=f"{label_text}:",
                            font=("Segoe UI", 10, "bold"), bg='#6b4423', fg='#f5deb3')
                lbl.grid(row=i, column=0, padx=10, pady=5, sticky="w")

                var = tk.StringVar(value=default_val)
                entry = tk.Entry(config_frame, textvariable=var, width=20, font=("Segoe UI", 10))
                entry.grid(row=i, column=1, padx=10, pady=5)

                config_labels[label_text] = lbl
                config_entries[label_text] = var

        actualizar_problema()

        # -------------------- Frame de Resultados --------------------
        resultados_frame = tk.Frame(contenido_frame, bg='#b8945f')
        resultados_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Gráfico
        grafico_frame = tk.LabelFrame(resultados_frame, text="Visualización",
                                    font=("Segoe UI", 11, "bold"),
                                    bg='#6b4423', fg='#f5deb3', relief='solid', bd=2)
        grafico_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        fig = Figure(figsize=(7, 5), dpi=100, facecolor='#6b4423')
        ax = fig.add_subplot(111, facecolor='#d4a574')
        canvas_grafico = FigureCanvasTkAgg(fig, grafico_frame)
        canvas_grafico.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Resultados texto
        texto_frame = tk.LabelFrame(resultados_frame, text="Resultados",
                                font=("Segoe UI", 11, "bold"),
                                bg='#6b4423', fg='#f5deb3', relief='solid', bd=2)
        texto_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        resultados_text = scrolledtext.ScrolledText(texto_frame, wrap=tk.WORD,
                                                width=35, height=20, font=("Courier", 9),
                                                bg='#d4a574', fg='#4b2e05', insertbackground='#4b2e05')
        resultados_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Variable para almacenar resultados actuales
        resultados_actuales = {'titulo': '', 'datos': ''}

        # -------------------- Funciones de Simulación --------------------
        def simular_pi():
            """Estima π usando método de Monte Carlo (círculo en cuadrado)."""
            try:
                N = int(config_entries['Número de simulaciones'].get())
                if N <= 0 or N > 2000000:
                    messagebox.showerror("Error", "Ingrese N entre 1 y 2,000,000", parent=ventana)
                    return

                gen = GeneradorAleatorios()
                xs_dentro, ys_dentro = [], []
                xs_fuera, ys_fuera = [], []
                dentro = 0

                for i in range(N):
                    x = gen.lcg()
                    y = gen.lcg()
                    if (x - 0.5)**2 + (y - 0.5)**2 <= 0.25:
                        xs_dentro.append(x)
                        ys_dentro.append(y)
                        dentro += 1
                    else:
                        xs_fuera.append(x)
                        ys_fuera.append(y)

                pi_est = 4 * (dentro / N)
                error = abs(pi_est - np.pi)
                porcentaje_error = (error / np.pi) * 100

                ax.clear()
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.set_aspect('equal', 'box')

                circulo = plt.Circle((0.5, 0.5), 0.5, fill=False, edgecolor='#2c3e50', linewidth=2.5)
                ax.add_patch(circulo)

                ax.scatter(xs_dentro, ys_dentro, s=2, color='#27ae60', alpha=0.7, label=f'Dentro ({dentro})')
                ax.scatter(xs_fuera, ys_fuera, s=2, color='#e74c3c', alpha=0.7, label=f'Fuera ({N-dentro})')
                ax.set_title(f'Estimación de π = {pi_est:.6f}', color='#2c3e50', fontweight='bold', fontsize=12)
                ax.legend(facecolor='#ecf0f1', edgecolor='#2c3e50', labelcolor='#2c3e50')
                ax.tick_params(colors='#2c3e50')
                ax.grid(True, alpha=0.3, color='#95a5a6')
                ax.set_facecolor('#f8f9fa')

                resultados_text.delete(1.0, tk.END)
                resultado_str = f"ESTIMACIÓN DE π\n"
                resultado_str += f"{'='*33}\n\n"
                resultado_str += f"π estimado:    {pi_est:.6f}\n"
                resultado_str += f"π real:        {np.pi:.6f}\n"
                resultado_str += f"Error:         {error:.6f}\n"
                resultado_str += f"Error %:       {porcentaje_error:.4f}%\n"
                resultado_str += f"Puntos dentro: {dentro}\n"
                resultado_str += f"Puntos fuera:  {N-dentro}\n"
                resultado_str += f"Total puntos:  {N}\n"
                
                resultados_text.insert(tk.END, resultado_str)
                resultados_actuales['titulo'] = 'Estimación de π'
                resultados_actuales['datos'] = resultado_str

                canvas_grafico.draw()
            except Exception as e:
                messagebox.showerror("Error", f"Error en simulación: {str(e)}", parent=ventana)

        def simular_ruina():
            """
            Simula la ruina del jugador con visualización de evolución de capital.
            Muestra gráficamente cómo disminuye el capital con el tiempo.
            """
            try:
                capital = int(config_entries['Capital inicial'].get())
                apuesta = int(config_entries['Apuesta por ronda'].get())
                prob_ganar = float(config_entries['Probabilidad de ganar'].get())
                sims = int(config_entries['Simulaciones'].get())

                gen = GeneradorAleatorios()
                capitales_finales = []
                rondas_totales = []
                capital_por_ronda = []

                for _ in range(sims):
                    cap = capital
                    rondas = 0
                    capital_ronda = [cap]
                    
                    while cap > 0 and rondas < 10000:
                        if gen.lcg() < prob_ganar:
                            cap += apuesta
                        else:
                            cap -= apuesta
                        rondas += 1
                        capital_ronda.append(cap)
                    
                    capitales_finales.append(cap)
                    rondas_totales.append(rondas)
                    capital_por_ronda.append(capital_ronda)

                # Visualización: mostrar evolución de 5 simulaciones
                ax.clear()
                for i in range(min(5, len(capital_por_ronda))):
                    ax.plot(capital_por_ronda[i], linewidth=1.5, alpha=0.7, label=f'Jugador {i+1}')
                
                ax.axhline(y=0, color='red', linestyle='--', linewidth=2, label='Ruina')
                ax.set_xlabel('Ronda', color='#4b2e05', fontweight='bold')
                ax.set_ylabel('Capital ($)', color='#4b2e05', fontweight='bold')
                ax.set_title('Evolución del Capital - Ruina del Jugador', color='#4b2e05', fontweight='bold')
                ax.legend(facecolor='#6b4423', edgecolor='#4b2e05', labelcolor='#4b2e05', fontsize=8)
                ax.tick_params(colors='#4b2e05')
                ax.grid(True, alpha=0.3)
                ax.set_facecolor('#d4a574')

                ruinas = sum(1 for c in capitales_finales if c == 0)
                prob_ruina = ruinas / sims

                resultados_text.delete(1.0, tk.END)
                resultado_str = f"RUINA DEL JUGADOR\n"
                resultado_str += f"{'='*33}\n\n"
                resultado_str += f"Capital inicial:     ${capital}\n"
                resultado_str += f"Apuesta/ronda:       ${apuesta}\n"
                resultado_str += f"P(ganar):            {prob_ganar:.4f}\n"
                resultado_str += f"Simulaciones:        {sims}\n\n"
                resultado_str += f"Pasos de simulación:\n"
                resultado_str += f"1. Se generan {sims} jugadores\n"
                resultado_str += f"2. Cada jugador juega hasta arruinarse\n"
                resultado_str += f"3. Se registra capital y rondas\n\n"
                resultado_str += f"Jugadores arruinados: {ruinas}\n"
                resultado_str += f"Probabilidad ruina:  {prob_ruina:.4f}\n"
                resultado_str += f"Capital promedio:    ${np.mean(capitales_finales):.2f}\n"
                resultado_str += f"Capital máximo:      ${np.max(capitales_finales)}\n"
                resultado_str += f"Rondas promedio:     {np.mean(rondas_totales):.0f}\n"
                
                resultados_text.insert(tk.END, resultado_str)
                resultados_actuales['titulo'] = 'Ruina del Jugador'
                resultados_actuales['datos'] = resultado_str

                canvas_grafico.draw()
            except Exception as e:
                messagebox.showerror("Error", f"Error en simulación: {str(e)}", parent=ventana)

        def simular_colas():
            """Simula un sistema de colas M/M/1 y calcula estadísticas."""
            try:
                clientes_hora = int(config_entries['Clientes por hora'].get())
                tiempo_servicio = float(config_entries['Tiempo servicio promedio (min)'].get())
                sims = int(config_entries['Simulaciones'].get())

                gen = GeneradorAleatorios()
                tiempos_espera = []
                largos_cola = []

                for _ in range(sims):
                    tiempo_llegada = 60 / clientes_hora
                    cola = []
                    tiempo_actual = 0
                    tiempos_espera_sim = []

                    for i in range(clientes_hora):
                        tiempo_actual += tiempo_llegada + gen.lcg() * 2
                        inicio_espera = max(tiempo_actual, cola[-1] if cola else 0)
                        tiempo_espera = max(0, inicio_espera - tiempo_actual)
                        tiempos_espera_sim.append(tiempo_espera)
                        cola.append(inicio_espera + tiempo_servicio)

                    tiempos_espera.extend(tiempos_espera_sim)
                    largos_cola.append(len(cola))

                ax.clear()
                ax.hist(tiempos_espera, bins=40, color='#8b6914', edgecolor='#4b2e05', alpha=0.7)
                ax.set_xlabel('Tiempo de Espera (min)', color='#4b2e05', fontweight='bold')
                ax.set_ylabel('Frecuencia', color='#4b2e05', fontweight='bold')
                ax.set_title('Distribución de Tiempos de Espera', color='#4b2e05', fontweight='bold')
                ax.tick_params(colors='#4b2e05')
                ax.grid(True, alpha=0.3)
                ax.set_facecolor('#d4a574')

                resultados_text.delete(1.0, tk.END)
                resultado_str = f"SISTEMA DE COLAS M/M/1\n"
                resultado_str += f"{'='*33}\n\n"
                resultado_str += f"Clientes/hora:       {clientes_hora}\n"
                resultado_str += f"Tiempo servicio:     {tiempo_servicio:.2f} min\n"
                resultado_str += f"Simulaciones:        {sims}\n\n"
                resultado_str += f"Pasos de simulación:\n"
                resultado_str += f"1. Generar llegadas de clientes\n"
                resultado_str += f"2. Calcular tiempo en cola\n"
                resultado_str += f"3. Simular tiempo de servicio\n\n"
                resultado_str += f"Tiempo esp. promedio: {np.mean(tiempos_espera):.2f} min\n"
                resultado_str += f"Tiempo esp. máximo:  {np.max(tiempos_espera):.2f} min\n"
                resultado_str += f"Percentil 90%:       {np.percentile(tiempos_espera, 90):.2f} min\n"
                resultado_str += f"Largo cola promedio: {np.mean(largos_cola):.2f}\n"
                resultado_str += f"Tasa utilización:    {(clientes_hora*tiempo_servicio)/60:.2%}\n"
                
                resultados_text.insert(tk.END, resultado_str)
                resultados_actuales['titulo'] = 'Sistema de Colas'
                resultados_actuales['datos'] = resultado_str

                canvas_grafico.draw()
            except Exception as e:
                messagebox.showerror("Error", f"Error en simulación: {str(e)}", parent=ventana)

        def simular_integral():
            """Estima una integral definida usando Monte Carlo."""
            try:
                N = int(config_entries['Número de puntos'].get())
                funcion_str = config_entries['Función'].get()

                gen = GeneradorAleatorios()
                dentro = 0

                for i in range(N):
                    x = gen.lcg()
                    y = gen.lcg()
                    try:
                        y_func = eval(funcion_str, {"x": x, "np": np})
                        if y <= y_func:
                            dentro += 1
                    except:
                        pass

                area_est = dentro / N

                x_plot = np.linspace(0, 1, 1000)
                y_plot = []
                for x_val in x_plot:
                    try:
                        y_val = eval(funcion_str, {"x": x_val, "np": np})
                        y_plot.append(y_val)
                    except:
                        y_plot.append(0)

                ax.clear()
                ax.plot(x_plot, y_plot, 'r-', linewidth=2, label=f'y = {funcion_str}')
                ax.fill_between(x_plot, 0, y_plot, alpha=0.3, color='#d4a574')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.set_xlabel('x', color='#4b2e05', fontweight='bold')
                ax.set_ylabel('y', color='#4b2e05', fontweight='bold')
                ax.set_title(f'Integral: ∫y={funcion_str}dx', color='#4b2e05', fontweight='bold')
                ax.legend(facecolor='#6b4423', edgecolor='#4b2e05', labelcolor='#4b2e05')
                ax.tick_params(colors='#4b2e05')
                ax.grid(True, alpha=0.3)
                ax.set_facecolor('#d4a574')

                resultados_text.delete(1.0, tk.END)
                resultado_str = f"INTEGRACIÓN POR MONTE CARLO\n"
                resultado_str += f"{'='*33}\n\n"
                resultado_str += f"Función: ∫y={funcion_str}dx\n"
                resultado_str += f"Límites: [0, 1]\n"
                resultado_str += f"Puntos: {N}\n\n"
                resultado_str += f"Pasos de simulación:\n"
                resultado_str += f"1. Generar puntos aleatorios\n"
                resultado_str += f"2. Contar puntos bajo la curva\n"
                resultado_str += f"3. Estimar área\n\n"
                resultado_str += f"Área estimada:  {area_est:.6f}\n"
                resultado_str += f"Puntos dentro:  {dentro}\n"
                resultado_str += f"Puntos fuera:   {N-dentro}\n"
                
                resultados_text.insert(tk.END, resultado_str)
                resultados_actuales['titulo'] = 'Integral Definida'
                resultados_actuales['datos'] = resultado_str

                canvas_grafico.draw()
            except Exception as e:
                messagebox.showerror("Error", f"Error en simulación: {str(e)}", parent=ventana)

        def simular_inventarios():
            """Encuentra la cantidad óptima de orden en un problema de inventarios."""
            try:
                demanda = int(config_entries['Demanda promedio'].get())
                costo_unit = float(config_entries['Costo unitario'].get())
                costo_ord = float(config_entries['Costo ordenar'].get())
                sims = int(config_entries['Simulaciones'].get())

                gen = GeneradorAleatorios()
                costos_totales = []
                cantidades_opt = []

                for q in range(10, 200, 10):
                    costos_sim = []
                    for _ in range(sims):
                        demanda_sim = demanda + int(gen.lcg() * 40 - 20)
                        if q >= demanda_sim:
                            costo = (q / 2) * costo_unit + costo_ord
                        else:
                            costo = (q / 2) * costo_unit + (demanda_sim - q) * costo_unit * 2 + costo_ord
                        costos_sim.append(costo)
                    costos_totales.append(np.mean(costos_sim))
                    cantidades_opt.append(q)

                q_optimo = cantidades_opt[np.argmin(costos_totales)]

                ax.clear()
                ax.plot(cantidades_opt, costos_totales, 'o-', color='#8b6914', linewidth=2, markersize=6)
                ax.axvline(q_optimo, color='#e74c3c', linestyle='--', linewidth=2, label=f'Q óptimo: {q_optimo}')
                ax.set_xlabel('Cantidad a Ordenar (Q)', color='#4b2e05', fontweight='bold')
                ax.set_ylabel('Costo Total Promedio ($)', color='#4b2e05', fontweight='bold')
                ax.set_title('Análisis de Costo - Problema de Inventarios', color='#4b2e05', fontweight='bold')
                ax.legend(facecolor='#6b4423', edgecolor='#4b2e05', labelcolor='#4b2e05')
                ax.tick_params(colors='#4b2e05')
                ax.grid(True, alpha=0.3)
                ax.set_facecolor('#d4a574')

                resultados_text.delete(1.0, tk.END)
                resultado_str = f"PROBLEMA DE INVENTARIOS\n"
                resultado_str += f"{'='*33}\n\n"
                resultado_str += f"Demanda promedio:    {demanda} unid/período\n"
                resultado_str += f"Costo unitario:      ${costo_unit:.2f}\n"
                resultado_str += f"Costo de orden:      ${costo_ord:.2f}\n"
                resultado_str += f"Simulaciones:        {sims}\n\n"
                resultado_str += f"Pasos de simulación:\n"
                resultado_str += f"1. Variar cantidad de orden\n"
                resultado_str += f"2. Simular demanda aleatoria\n"
                resultado_str += f"3. Calcular costo total\n"
                resultado_str += f"4. Encontrar Q óptima\n\n"
                resultado_str += f"Cantidad óptima (Q): {q_optimo} unid\n"
                resultado_str += f"Costo mínimo:        ${min(costos_totales):.2f}\n"
                resultado_str += f"Rango Q evaluado:    {min(cantidades_opt)}-{max(cantidades_opt)} unid\n"
                
                resultados_text.insert(tk.END, resultado_str)
                resultados_actuales['titulo'] = 'Problema de Inventarios'
                resultados_actuales['datos'] = resultado_str

                canvas_grafico.draw()
            except Exception as e:
                messagebox.showerror("Error", f"Error en simulación: {str(e)}", parent=ventana)

        def simular_hipotesis():
            """
            Simula una prueba de hipótesis Monte Carlo.
            H0: μ = μ₀ vs H1: μ ≠ μ₀
            """
            try:
                mu_0 = float(config_entries['Media hipotética (μ₀)'].get())
                sigma = float(config_entries['Desv. estándar (σ)'].get())
                n = int(config_entries['Tamaño muestra (n)'].get())
                sims = int(config_entries['Simulaciones'].get())
                alpha = float(config_entries['Nivel significancia (α)'].get())

                gen = GeneradorAleatorios()
                medias_muestra = []
                rechazos = 0

                for _ in range(sims):
                    muestra = []
                    for _ in range(n):
                        # Generar N(μ₀, σ²)
                        u1 = gen.lcg()
                        u2 = gen.lcg()
                        z = np.sqrt(-2 * np.log(u1)) * np.cos(2 * np.pi * u2)
                        x = mu_0 + sigma * z
                        muestra.append(x)
                    
                    media = np.mean(muestra)
                    medias_muestra.append(media)
                    
                    # Test: ¿rechazamos H0?
                    se = sigma / np.sqrt(n)
                    z_stat = (media - mu_0) / se
                    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
                    
                    if p_value < alpha:
                        rechazos += 1

                from scipy import stats as sp_stats
                
                ax.clear()
                ax.hist(medias_muestra, bins=40, color='#8b6914', edgecolor='#4b2e05', alpha=0.7, density=True)
                
                x_range = np.linspace(min(medias_muestra), max(medias_muestra), 100)
                se = sigma / np.sqrt(n)
                pdf = sp_stats.norm.pdf(x_range, mu_0, se)
                ax.plot(x_range, pdf, 'r-', linewidth=2, label='N(μ₀, SE²)')
                ax.axvline(mu_0, color='green', linestyle='--', linewidth=2, label=f'μ₀ = {mu_0}')
                ax.set_xlabel('Media Muestral', color='#4b2e05', fontweight='bold')
                ax.set_ylabel('Densidad', color='#4b2e05', fontweight='bold')
                ax.set_title('Prueba de Hipótesis - Distribución de Medias Muestrales', color='#4b2e05', fontweight='bold')
                ax.legend(facecolor='#6b4423', edgecolor='#4b2e05', labelcolor='#4b2e05')
                ax.tick_params(colors='#4b2e05')
                ax.grid(True, alpha=0.3)
                ax.set_facecolor('#d4a574')

                potencia = rechazos / sims
                
                resultados_text.delete(1.0, tk.END)
                resultado_str = f"PRUEBA DE HIPÓTESIS - MONTE CARLO\n"
                resultado_str += f"{'='*33}\n\n"
                resultado_str += f"H₀: μ = {mu_0}\n"
                resultado_str += f"H₁: μ ≠ {mu_0}\n"
                resultado_str += f"Nivel significancia: {alpha}\n\n"
                resultado_str += f"Parámetros:\n"
                resultado_str += f"- Desv. estándar:    {sigma}\n"
                resultado_str += f"- Tamaño muestra:    {n}\n"
                resultado_str += f"- Simulaciones:      {sims}\n\n"
                resultado_str += f"Pasos de simulación:\n"
                resultado_str += f"1. Generar {sims} muestras N({mu_0}, {sigma}²)\n"
                resultado_str += f"2. Calcular media de cada muestra\n"
                resultado_str += f"3. Realizar test Z para cada muestra\n"
                resultado_str += f"4. Contar rechazos de H₀\n\n"
                resultado_str += f"Resultados:\n"
                resultado_str += f"Media de medias:     {np.mean(medias_muestra):.4f}\n"
                resultado_str += f"Error estándar:      {se:.4f}\n"
                resultado_str += f"Rechazos H₀:         {rechazos}\n"
                resultado_str += f"Potencia (tipo II):  {potencia:.4f}\n"
                resultado_str += f"Min media:           {np.min(medias_muestra):.4f}\n"
                resultado_str += f"Max media:           {np.max(medias_muestra):.4f}\n"
                
                resultados_text.insert(tk.END, resultado_str)
                resultados_actuales['titulo'] = 'Prueba de Hipótesis'
                resultados_actuales['datos'] = resultado_str

                canvas_grafico.draw()
            except Exception as e:
                messagebox.showerror("Error", f"Error en simulación: {str(e)}", parent=ventana)

        # -------------------- Función Ejecutar --------------------
        def ejecutar_simulacion():
            """Ejecuta la simulación del problema seleccionado."""
            problema = problema_var.get()
            if problema == "pi":
                simular_pi()
            elif problema == "ruina":
                simular_ruina()
            elif problema == "colas":
                simular_colas()
            elif problema == "integral":
                simular_integral()
            elif problema == "inventarios":
                simular_inventarios()
            elif problema == "hipotesis":
                simular_hipotesis()

        def exportar_resultados():
            """
            Exporta los resultados de la simulación a un archivo de texto
            y también guarda el gráfico como imagen PNG.
            """
            if not resultados_actuales['datos']:
                messagebox.showwarning("Advertencia", "No hay resultados para exportar", parent=ventana)
                return
            
            archivo = filedialog.asksaveasfilename(
                parent=ventana,
                title="Guardar resultados",
                defaultextension=".txt",
                filetypes=[("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")]
            )
            
            if archivo:
                try:
                    # Exportar resultados en texto con UTF-8
                    with open(archivo, 'w', encoding='utf-8') as f:
                        f.write("="*50 + "\n")
                        f.write("RESULTADOS - SIMULACIÓN MONTE CARLO\n")
                        f.write("="*50 + "\n\n")
                        f.write(f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Problema: {resultados_actuales['titulo']}\n\n")
                        f.write(resultados_actuales['datos'])
                        f.write("\n\n" + "="*50 + "\n")
                        f.write("Fin del reporte\n")
                        f.write("="*50 + "\n")
                    
                    # Exportar gráfico como imagen PNG
                    archivo_grafico = archivo.replace('.txt', '_grafico.png')
                    fig.savefig(archivo_grafico, dpi=300, bbox_inches='tight', facecolor='#6b4423')
                    
                    messagebox.showinfo(
                        "Éxito", 
                        f"Resultados exportados correctamente:\n\n"
                        f"Texto: {archivo}\n"
                        f"Gráfico: {archivo_grafico}",
                        parent=ventana
                    )
                except Exception as e:
                    messagebox.showerror("Error", f"Error al exportar: {str(e)}", parent=ventana)

        # -------------------- Botones --------------------
        botones_frame = tk.Frame(main_frame, bg='#b8945f')
        botones_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(botones_frame, text="Ejecutar Simulación", command=ejecutar_simulacion,
                font=("Segoe UI", 10, "bold"), bg="#d4a574", fg="#4b2e05",
                relief="flat", width=20, cursor='hand2').pack(side="left", padx=10)

        tk.Button(botones_frame, text="Exportar Resultados", command=exportar_resultados,
                font=("Segoe UI", 10, "bold"), bg="#4b2e05", fg="#f5deb3",
                relief="flat", width=18, cursor='hand2').pack(side="left", padx=10)

        tk.Button(botones_frame, text="Cerrar", command=on_close,
                font=("Segoe UI", 10, "bold"), bg="#e74c3c", fg="white",
                relief="flat", width=12, cursor='hand2').pack(side="right", padx=10)

    def ventana_ayuda(self):
        """
        Ventana de Ayuda con manual de usuario profesional.
        
        Explica cómo usar cada funcionalidad sin información académica.
        Estilo: software profesional.
        """
        ventana = tk.Toplevel(self.root)
        ventana.title("Ayuda - Manual de Usuario")
        ventana.geometry("1000x700")
        ventana.configure(bg='#fcdea6')
        
        # -------------------- Frame Superior --------------------
        header_frame = tk.Frame(ventana, bg='#4b2e05')
        header_frame.pack(fill="x", pady=0)
        
        tk.Label(header_frame, text="SIMUSTATS - Manual de Usuario",
                font=("Segoe UI", 18, "bold"), bg='#4b2e05', fg='#d4a574').pack(pady=10)
        
        # -------------------- Canvas con Scroll --------------------
        canvas = tk.Canvas(ventana, bg='#fcdea6', highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(ventana, orient="vertical", command=canvas.yview, width=12)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        main_frame = tk.Frame(canvas, bg='#b8945f')
        main_frame_id = canvas.create_window((0, 0), window=main_frame, anchor="nw")

        def actualizar_scroll(event=None):
            """Actualiza el área scrolleable."""
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(main_frame_id, width=canvas.winfo_width())

        main_frame.bind("<Configure>", actualizar_scroll)
        canvas.bind("<Configure>", actualizar_scroll)

        def scroll_con_mouse(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", scroll_con_mouse)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
        def on_close():
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
            ventana.destroy()
        
        ventana.protocol("WM_DELETE_WINDOW", on_close)

        # -------------------- Contenido de Ayuda --------------------
        def crear_seccion(titulo, contenido):
            """Crea una sección de ayuda con título y contenido."""
            frame = tk.LabelFrame(main_frame, text=titulo,
                                font=("Segoe UI", 12, "bold"),
                                bg='#6b4423', fg='#f5deb3', relief='solid', bd=2)
            frame.pack(fill="x", padx=15, pady=10)
            
            label = tk.Label(frame, text=contenido,
                            font=("Segoe UI", 10), bg='#6b4423', fg='#d4a574',
                            justify="left", wraplength=900)
            label.pack(padx=15, pady=10, anchor="w")

        # ═══════════════════════════════════════════════════════════════════════════
        crear_seccion(
            "1. GENERACIÓN DE VARIABLES ALEATORIAS",
            """
    DESCRIPCIÓN:
    Genere variables aleatorias de distribuciones discretas o continuas. 
    Esta herramienta es útil para simulaciones, pruebas de hipótesis y 
    análisis estadísticos.

    PASOS:
    1. Seleccione si desea una distribución DISCRETA o CONTINUA
    2. Elija la distribución específica de la lista
    3. Configure la SEMILLA (manual o automática)
    • Semilla manual: números reproducibles con valor específico
    • Semilla automática: genera valores diferentes cada ejecución
    4. Ingrese la CANTIDAD de valores a generar
    5. Configure los parámetros según la distribución elegida
    6. Presione "Generar Datos"

    DISTRIBUCIONES DISPONIBLES:

    Discretas:
    • Bernoulli(p): Genera 0 o 1 con probabilidad p
    • Binomial(n,p): Número de éxitos en n ensayos
    • Poisson(λ): Número de eventos en intervalo fijo

    Continuas:
    • Uniforme(a,b): Valores entre a y b (uniforme)
    • Exponencial(λ): Tiempos entre eventos
    • Normal(μ,σ): Distribución gaussiana (campana)

    EXPORTACIÓN:
    Presione "Exportar Datos" para guardar los valores generados en 
    un archivo de texto para uso posterior.
            """
        )

        # ═══════════════════════════════════════════════════════════════════════════
        crear_seccion(
            "2. PRUEBA DE AJUSTE DE DISTRIBUCIONES",
            """
    DESCRIPCIÓN:
    Determine si un conjunto de datos sigue una distribución específica.
    Utiliza pruebas estadísticas rigurosas para validar hipótesis.

    PASOS:
    1. CARGAR DATOS: 
    • Opción A: "Cargar desde Archivo" - archivo .txt con números
    • Opción B: "Ingresar Manualmente" - copiar/pegar valores
    2. Seleccione la DISTRIBUCIÓN a probar (Normal, Exponencial, etc.)
    3. Configure el NIVEL DE SIGNIFICANCIA (α) - típicamente 0.05
    4. Presione "Realizar Prueba"

    INTERPRETACIÓN DE RESULTADOS:

    Estadísticos Descriptivos:
    • Media, Mediana, Desv. Estándar: resumen de los datos
    • Mínimo, Máximo, Rango: dispersión
    • Cuartiles: división de datos en 4 partes

    Prueba Kolmogorov-Smirnov (K-S):
    • Compara la distribución empírica vs teórica
    • Estadístico D: máxima diferencia encontrada
    • Valor-p: probabilidad de observar D bajo H₀
    • Decisión: si p > α → datos AJUSTAN a la distribución

    Prueba Chi-Cuadrado (χ²):
    • Compara frecuencias observadas vs esperadas
    • Estadístico χ²: suma de diferencias cuadradas
    • Valor-p: probabilidad de χ² bajo H₀
    • Decisión: si p > α → datos AJUSTAN a la distribución

    Conclusión Final:
    • ✓✓ Ambas pruebas concuerdan: resultado confiable
    • ✗✗ Ambas pruebas concuerdan: resultado confiable
    • ⚠ Pruebas no concuerdan: se recomienda análisis adicional

    EXPORTACIÓN:
    Presione "Exportar Resultados" para guardar el reporte completo 
    con todos los estadísticos y conclusiones.
            """
        )

        # ═══════════════════════════════════════════════════════════════════════════
        crear_seccion(
            "3. MÉTODO DE MONTE CARLO - 6 PROBLEMAS",
            """
    DESCRIPCIÓN:
    Realice simulaciones Monte Carlo para resolver diversos problemas 
    prácticos de ingeniería, negocios y ciencia.

    SELECCIONAR PROBLEMA:
    Use los radio buttons para elegir entre 6 problemas diferentes:

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    PROBLEMA 1: ESTIMACIÓN DE π
    Estima el valor de π generando puntos aleatorios en un cuadrado.
    Parámetro: Número de simulaciones (5000-2000000)
    Resultado: Valor estimado de π, error y porcentaje de error

    PROBLEMA 2: RUINA DEL JUGADOR
    Simula jugadores apostando dinero hasta perder todo.
    Parámetros: 
    • Capital inicial: dinero de inicio
    • Apuesta por ronda: cantidad por juego
    • Probabilidad de ganar: entre 0 y 1
    Resultado: Gráfico de evolución de capital, probabilidad de ruina

    PROBLEMA 3: SISTEMA DE COLAS
    Simula una fila de espera (ej: banco, tienda).
    Parámetros:
    • Clientes por hora: llegadas
    • Tiempo de servicio: cuánto atienden
    Resultado: Tiempo de espera promedio, máximo, percentiles

    PROBLEMA 4: INTEGRAL DEFINIDA
    Estima el área bajo una curva matemática.
    Parámetro: Función a integrar (ej: x**2, np.sin(x))
    Resultado: Área estimada bajo la curva

    PROBLEMA 5: PROBLEMA DE INVENTARIOS
    Determina cantidad óptima de orden para minimizar costos.
    Parámetros:
    • Demanda promedio
    • Costo unitario
    • Costo de ordenar
    Resultado: Cantidad óptima y costo mínimo

    PROBLEMA 6: PRUEBA DE HIPÓTESIS
    Simula una prueba de hipótesis estadística.
    Parámetros:
    • Media hipotética (H₀)
    • Desviación estándar
    • Tamaño de muestra
    Resultado: Distribución de medias, potencia de prueba

    EJECUCIÓN:
    1. Seleccione el problema
    2. Configure los parámetros según necesite
    3. Presione "Ejecutar Simulación"
    4. Observe el gráfico y resultados
    5. Opcionalmente exporte con "Exportar Resultados"

    VISUALIZACIÓN:
    • Gráficos dinámicos muestran resultados en tiempo real
    • Panel de resultados con estadísticas detalladas
    • Pasos de simulación explicados en texto
            """
        )

        # ═══════════════════════════════════════════════════════════════════════════
        crear_seccion(
            "CONSEJOS Y BUENAS PRÁCTICAS",
            """
    VALIDACIÓN DE DATOS:
    ✓ Asegúrese que los datos cargados sean números válidos
    ✓ Use puntos (.) como separador decimal, no comas
    ✓ Un valor por línea en archivos de texto

    CONFIGURACIÓN RECOMENDADA:
    ✓ Nivel de significancia (α): 0.05 (por defecto)
    ✓ Número de simulaciones: 1000-10000 (balance velocidad/precisión)
    ✓ Semilla manual: use cuando quiera reproducir resultados

    INTERPRETACIÓN:
    ✓ Valor-p > 0.05: Datos probablemente siguen la distribución
    ✓ Valor-p ≤ 0.05: Evidencia contra la hipótesis
    ✓ Gráficos: siempre verifique visualmente los resultados

    EXPORTACIÓN:
    ✓ Exporte resultados importantes para documentación
    ✓ Los archivos se guardan en formato texto plano
    ✓ Puede editarlos en cualquier editor de texto

    RENDIMIENTO:
    ⚠ No simule más de 2,000,000 puntos (puede ralentizar)
    ⚠ Para pruebas: comience con valores pequeños
    ⚠ Aumente gradualmente para resultados finales
            """
        )

        # ═══════════════════════════════════════════════════════════════════════════
        crear_seccion(
            "SOLUCIÓN DE PROBLEMAS",
            """
    PROBLEMA: "Error al cargar archivo"
    → Verifique que el archivo esté en formato .txt
    → Asegúrese que contenga solo números
    → Intente abrir el archivo en un editor de texto para verificar

    PROBLEMA: "Valores generados no son lo esperado"
    → Verifique los parámetros de la distribución
    → Para resultados reproducibles, use semilla manual
    → Con semilla automática, cada ejecución es diferente

    PROBLEMA: "La prueba de ajuste es lenta"
    → Esto es normal con muchos datos
    → Espere a que termine la simulación
    → Use menos puntos si necesita rapidez

    PROBLEMA: "Gráfico no se actualiza"
    → Presione nuevamente "Ejecutar Simulación"
    → Cierre y reabra la ventana
    → Verifique que los valores sean válidos

    PROBLEMA: "No puedo exportar los resultados"
    → Verifique permisos de escritura en la carpeta
    → Elija una ubicación diferente
    → Intente con un nombre de archivo diferente

    ¿Necesita más ayuda? Verifique que todos los datos sean válidos 
    y los parámetros sean razonables.
            """
        )

        # -------------------- Botón Cerrar --------------------
        botones_frame = tk.Frame(ventana, bg='#fcdea6')
        botones_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Button(botones_frame, text="Cerrar Ayuda", command=on_close,
                font=("Segoe UI", 11, "bold"), bg="#e74c3c", fg="white",
                relief="flat", width=20, height=2, cursor='hand2').pack(side="right")

# ═══════════════════════════════════════════════════════════════════════════════
# EJECUCIÓN DE LA APLICACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuStatsApp(root)
    root.mainloop()