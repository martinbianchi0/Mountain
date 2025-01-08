import time
import threading
from tkinter import *
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import mpl_toolkits.mplot3d.axes3d as p3
import random
from communication.client.client import MountainClient
import math
import tkinter as ttk
import argparse

# Con la libreria Argparse, podemos conectarnos con un codigo a un servidor desde la terminal.
# En la terminal, ingresarías por ejemplo: python tpf_NOMBRE_DE_GRUPO_dashboard.py --ip 127.0.0.1:8000

class Dashboard:
    def __init__(self, client: MountainClient):
        self.root = Tk()
        self.root.title("Dashboard")
        self.client = client
        self.data = client.get_data()
        self.time_step = 500  # ms
        self.animations = []  # for animations to stay alive in memory
        self.figsize = (4.5, 3)

        self.root.configure(bg="black")
        self.frame = Frame(self.root)
        self.frame.pack(side=LEFT)
        # Insertamos cada uno de los dashboards
        self.listbox = Listbox(self.frame, selectmode=SINGLE, width=35, bg="black", fg="white")
        self.listbox.pack(side=TOP, padx=10, pady=10, fill=BOTH, expand=True, anchor='center')
        self.listbox.insert(END, "Altura de los escaladores")
        self.listbox.insert(END, "Ranking de altura")
        self.listbox.insert(END, "Leaderboard")
        self.listbox.insert(END, "Ubicacion 3D")
        self.listbox.insert(END, "Trayectoria 3D")
    
        self.listbox.bind("<<ListboxSelect>>", self.cambiar)
        self.listbox.columnconfigure(0, weight=1)
        self.visualization_frame = Frame(self.root)
        self.visualization_frame.pack(side=LEFT, fill=BOTH, expand=True)
        self.current_visualization = None
        self.current_frame = None

    def cambiar(self,e):
        seleccionado = self.listbox.curselection()
        if seleccionado:
            visualización = self.listbox.get(seleccionado[0])
            self.mostrar(visualización)

    def mostrar(self,visualización):
        """Renueva las visualizaciones por iteración con información nueva"""
        if self.current_visualization is not None :
            self.current_visualization.destroy()  # borrar la visualización anterior
            self.current_frame.destroy()  # borrar el marco de la visualización anterior
        if visualización == "Altura de los escaladores":
            self.current_visualization = self.alturas()
        elif visualización == "Ranking de altura":
            self.current_visualization = self.height_rank()  
        elif visualización == "Leaderboard":
            self.current_visualization = self.leaderboard()
        elif visualización == "Ubicacion 3D":
            self.current_visualization = self.ubi_3D()
        elif visualización == "Trayectoria 3D":
            self.current_visualization = self.Trayectoria_3D()
        

        if self.current_visualization is not None:  
            self.current_frame = Frame(self.visualization_frame)
            self.current_visualization.pack(fill=BOTH, expand=True)
            self.current_frame.pack(fill=BOTH, expand=True)
            
    
    def alturas(self):
        """Este gráfico muestra las alturas correspondientes a cada equipo respectivo."""
        frame = Frame(self.visualization_frame)
        fig, ax = plt.subplots(figsize=self.figsize)

        equipos = list(self.data.keys()) 
        c = StringVar(self.root)
        c.set(equipos[0])  

        menu = OptionMenu(frame, c, *equipos)
        menu.pack(side=TOP, padx=10, pady=10)

        def animate(i):
            data = self.client.get_data()
            ax.clear()
            nombres_escaladores = []
            alturas = []
            equipo_elegido = c.get()
            team_data = data.get(equipo_elegido, {})
            
            for escalador, info in team_data.items():
                nombres_escaladores.append(escalador)
                alturas.append(info['z'])
                ax.text(nombres_escaladores[-1], alturas[-1] + 0.5, str(round(info['z'], 2)), ha='center')
                
            ax.bar(nombres_escaladores, alturas)
            ax.set_xlabel('Escaladores')
            ax.set_ylabel('Altura')

        animation = FuncAnimation(fig, animate, interval=self.time_step)
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        self.current_visualization = frame

        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        self.animations.append(animation)
        return frame


    def height_rank(self):
        """Este gráfico representa el ranking de los 10 escaladores con la mayor altura alcanzada"""
        frame = Frame(self.visualization_frame)
        frame.grid(row=0, column=0, sticky=(N, S, E, W))
        l = Listbox(frame, height=5, width=50)  
        l.grid(column=0, row=0, padx=10, pady=10, sticky=(N, W, E, S))
        s = ttk.Scrollbar(frame, orient=VERTICAL, command=l.yview)
        s.grid(column=1, row=0, sticky=(N, S))
        l['yscrollcommand'] = s.set
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        graph_frame = Frame(frame)
        graph_frame.grid(row=0, column=2, rowspan=3, sticky=(N, S, E, W))
        fig, ax = plt.subplots(figsize=(6, 4))
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, graph_frame)
        toolbar.pack(side=BOTTOM, fill=X)
        toolbar.update()

        def update_heights():
            data = self.client.get_data()
            l.delete(0, END)
            escaladores = []
            for equipo, team_data in data.items():
                for escalador, info in team_data.items():
                    escaladores.append((escalador, info['z'], equipo))
            
            escaladores.sort(key=lambda x: x[1], reverse=True)
            top_10 = escaladores[:10]  # los mejores 10
            
            for i, (escalador, altura, equipo) in enumerate(top_10, 1):
                l.insert(END, f"{i}. {equipo.upper()}: {escalador}: {altura:.0f} mts de altura")

            jugadores = [f"{equipo.upper()}: {escalador}" for escalador, _, equipo in top_10]
            alturas = [altura for _, altura, _ in top_10]
            colores = ['black'] * 10  

            altura_max = max(alturas)
            max_index = alturas.index(altura_max)
            
            # el mas alto es amarillo
            colores[max_index] = 'yellow'
            ax.clear()
            ax.bar(jugadores, alturas, color=colores)
            ax.set_ylabel('Altura')
            ax.set_xlabel('Escaladores')
            ax.set_title('Ranking de Alturas (Top 10)')
            ax.tick_params(axis='x', rotation=90)
            canvas.draw()

            self.visualization_frame.after(self.time_step, update_heights)

        update_heights()
        return frame
    
    def leaderboard(self):
        """Leaderboard con los 10 mejores puestos"""
        frame = Frame(self.visualization_frame)
        frame.pack(fill=BOTH, expand=True)

        title_label = ttk.Label(frame, text="Los 10 Mejores", fg="black",font=("algerian", 26), anchor=W)
        title_label.pack(pady=(10, 5))

        l = Listbox(frame, height=50, width=40, font=("arial",18), bg="black", fg="white")
        l.pack(side=TOP, padx=10, pady=(0, 10), fill=BOTH, expand=True)


        def update_leaderboard():
            data = self.client.get_data()
            l.delete(0, END) 
            todos = []
            for equipo,team_data in data.items():
                for escalador, info in team_data.items():
                    nombre = escalador
                    altura = info['z']
                    todos.append((nombre, altura, equipo))
            todos.sort(key=lambda x: x[1], reverse=True)
            for i, (nombre, altura, equipo) in enumerate(todos[:10],1):
                l.insert(END,  f"{i}) {nombre}: con una altura de {altura:.0f} mts, del equipo '{equipo}'")
            self.visualization_frame.after(self.time_step, update_leaderboard)  
        update_leaderboard()
        return frame
    
    def ubi_3D(self):
        """Proporciona la ubicación actual de cualquier equipo seleccionado en un mapa tridimensional."""
        frame = Frame(self.visualization_frame)
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(111, projection='3d')
        equipos = list(self.data.keys()) 
        c = StringVar(self.root)
        c.set(equipos[0])  
        menu = OptionMenu(frame, c, *equipos)
        menu.pack(side=TOP, padx=10, pady=10)
        colores = ['red', 'green', 'blue', 'yellow']  
        
        climbers_colors = {}  
        def animate(i):
            data = self.client.get_data()
            ax.clear()
            nombres_escaladores = []
            posiciones_x = []
            posiciones_y = []
            alturas = []
            equipo_elegido = c.get()
            team_data = data.get(equipo_elegido, {})
            e=0
            
            for escalador, info in team_data.items():
                nombres_escaladores.append(escalador)
                posiciones_x.append(info['x'])
                posiciones_y.append(info['y'])
                alturas.append(info['z'])
                
                if escalador not in climbers_colors:
                    climbers_colors[escalador] = colores[e]
                    e+=1
                
                ax.scatter(info['x'], info['y'], info['z'], color=climbers_colors[escalador]) 
                ax.text(info['x'], info['y'], info['z'] - 4, f"({round(info['x'])},{round(info['y'])},{round(info['z'])})", ha='center')                
                ax.text(info['x'], info['y'], info['z'] + 3, escalador, ha='center', va='center')
                    
            ax.set_xlabel('Posición X')
            ax.set_ylabel('Posición Y')
            ax.set_zlabel('Altura')

        animation = FuncAnimation(fig, animate, interval=self.time_step)
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        self.current_visualization = frame

        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        self.animations.append(animation)
        return frame


    def Trayectoria_3D(self):
        """Nos proporciona un mapa tridimensional que visualiza los desplazamientos de nuestro equipo, 
        permitiéndonos observar su trayectoria a lo largo del tiempo."""
        coordenadas_x_jugador1=[]
        coordenadas_y_jugador1=[]
        coordenadas_z_jugador1=[]


        coordenadas_x_jugador2=[]
        coordenadas_y_jugador2=[]
        coordenadas_z_jugador2=[]


        coordenadas_x_jugador3=[]
        coordenadas_y_jugador3=[]
        coordenadas_z_jugador3=[]


        coordenadas_x_jugador4=[]
        coordenadas_y_jugador4=[]
        coordenadas_z_jugador4=[]
        frame = Frame(self.visualization_frame)
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(111, projection='3d')
    
        def animate(i):
            data = self.client.get_data()
            ax.clear()
            
            nuestro_equipo=data.get("Elite del ascenso")
            jugador1=nuestro_equipo.get("jugador1")
            coordenadas_x_jugador1.append(jugador1.get("x"))
            coordenadas_y_jugador1.append(jugador1.get("y"))
            coordenadas_z_jugador1.append(jugador1.get("z"))
            ax.scatter(coordenadas_x_jugador1,coordenadas_y_jugador1,coordenadas_z_jugador1,color="green")
            ax.text(jugador1.get("x"),jugador1.get("y"),jugador1.get("z"),"jugador1")
                
            jugador2_ubi=nuestro_equipo.get("jugador2")
            ax.text(jugador2_ubi.get("x"),jugador2_ubi.get("y"),jugador2_ubi.get("z"),'jugador2')
            ax.scatter(coordenadas_x_jugador2,coordenadas_y_jugador2,coordenadas_z_jugador2,color='blue')
            coordenadas_x_jugador2.append(jugador2_ubi.get("x"))
            coordenadas_y_jugador2.append(jugador2_ubi.get("y"))
            coordenadas_z_jugador2.append(jugador2_ubi.get("z"))
                
            jugador4_ubi=nuestro_equipo.get("jugador4")
            ax.text(jugador4_ubi.get("x"),jugador4_ubi.get("y"),jugador4_ubi.get("z"),'jugador4')
            ax.scatter(coordenadas_x_jugador4,coordenadas_y_jugador4,coordenadas_z_jugador4,color='yellow')
            coordenadas_x_jugador4.append(jugador4_ubi.get("x"))
            coordenadas_y_jugador4.append(jugador4_ubi.get("y"))
            coordenadas_z_jugador4.append(jugador4_ubi.get("z"))
                
            jugador3_ubi=nuestro_equipo.get("jugador3")
            ax.text(jugador3_ubi.get("x"),jugador3_ubi.get("y"),jugador3_ubi.get("z"),'jugador3')
            ax.scatter(coordenadas_x_jugador3,coordenadas_y_jugador3,coordenadas_z_jugador3,color='magenta')
            coordenadas_x_jugador3.append(jugador3_ubi.get("x"))
            coordenadas_y_jugador3.append(jugador3_ubi.get("y"))
            coordenadas_z_jugador3.append(jugador3_ubi.get("z"))
                
                
        ax.set_xlabel('Posición X')
        ax.set_ylabel('Posición Y')
        ax.set_zlabel('Altura')

        animation = FuncAnimation(fig, animate, interval=self.time_step)
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        self.current_visualization = frame

        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        self.animations.append(animation)
        return frame
        
    def start(self):
        # No modificar
        t = threading.Thread(target=self.update_data)
        t.start()
        self.root.mainloop()

    def update_data(self):
        # No modificar
        
        while not self.client.is_over():
            self.data = self.client.get_data()
            
            time.sleep(self.time_step / 1000)
            

    def stop(self):
        # No modificar
        self.root.quit()
    
def main():
    # Con la libreria Argparse, podemos conectarnos con un codigo a un servidor desde la terminal.
    # En la terminal, ingresarías por ejemplo: python tpf_NOMBRE_DE_GRUPO_dashboard.py --ip 127.0.0.1:8000
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip')
    args = parser.parse_args()
    print(args.ip)
    ip_puerto = args.ip.split(":")
    ip = ip_puerto[0]
    puerto=int(ip_puerto[1])
    cliente=MountainClient(ip,puerto)
    d = Dashboard(cliente)
    d.start()

if __name__ == "__main__":
    main()