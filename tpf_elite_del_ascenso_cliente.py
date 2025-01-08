from communication.client.client import MountainClient
import time
from math import radians
import math
from math import pi
import argparse

# La libreria Argparse nos permite establecer una conexión con un servidor utilizando la terminal como interfaz.
# En la terminal, se introduce, por ejemplo: python tpf_NOMBRE_DE_GRUPO_cliente.py --ip 127.0.0.1:8000
parser = argparse.ArgumentParser()
parser.add_argument('--ip')
args = parser.parse_args()
print(args.ip)
ip_puerto = args.ip.split(":")
ip = ip_puerto[0]
puerto=int(ip_puerto[1])
cliente=MountainClient(ip,puerto)

# Registramos nuestro equipo
cliente.add_team("Elite del ascenso",["jugador1","jugador4", "jugador2", "jugador3"])
cliente.finish_registration()

# Variables generales del servidor
radio=23000
speed=50
iteraciones=0

# Creamos listas vacías para almacenar las coordenadas
coordenadas_x_jugador1=[]
coordenadas_y_jugador1=[]

coordenadas_x_jugador2=[]
coordenadas_y_jugador2=[]

coordenadas_x_jugador3=[]
coordenadas_y_jugador3=[]

coordenadas_x_jugador4=[]
coordenadas_y_jugador4=[]

def ubicacion_nuestra():
    """Proporciona los datos actualizados de cada miembro de nuestro equipo en 'tiempo real'."""
    nuestro_equipo=cliente.get_data().get("Elite del ascenso")
    jugador1_ubicacion=nuestro_equipo.get("jugador1")
    jugador4_ubicacion=nuestro_equipo.get("jugador4")
    jugador2_ubicacion=nuestro_equipo.get("jugador2")
    jugador3_ubicacion=nuestro_equipo.get("jugador3")
    return jugador1_ubicacion, jugador4_ubicacion, jugador2_ubicacion, jugador3_ubicacion

def llego_alguien():
    """Verifica si alguien ha alcanzado la cima y, en caso afirmativo, proporciona sus coordenadas correspondientes."""
    info=cliente.get_data()
    for equipo in info:
        datos_equipo = info.get(equipo)
        for escalador in datos_equipo:
            dato_escalador=datos_equipo.get(escalador)
            if dato_escalador.get("cima")==True:
                cima = [dato_escalador.get("x"), dato_escalador.get("y")]
                return cima
    return False

# Clase de movimientos, segun estrategias
class movimientos:
    def __init__(self,ubicacion:dict,nombre:str):
        """Almacenamos la información del integrante ingresado"""
        self.nombre=nombre
        self.x=ubicacion.get("x")
        self.y=ubicacion.get("y")
        self.z=ubicacion.get("z")
        self.dx=ubicacion.get("inclinacion_x")
        self.dy=ubicacion.get("inclinacion_y")
        self.cima=ubicacion.get("cima")
        
    def verificacion(self):
        """La verificación da prioridad a ciertos movimientos por sobre las estrategias pensadas.
        En orden de prioridad, nos aseguramos de no salir de los límites del mapa, dirigirnos a la cima si tenemos sus coordenadas,
        y sacar al personaje de un bucle si accidentalmente cae en uno. 
        Si ninguna de estas situaciones se presenta, procedemos a ejecutar una de las estrategias establecidas"""

        # Utilizamos variables globales para que la clase pueda utilizarlas.
        global speed
        global loop_jugador4
        global loop_jugador2
        global loop_jugador1
        global loop_jugador3

        # Evitar limites del mapa
        if (((self.x - 50) ** 2 + self.y ** 2) ** 0.5) > radio-100:
            self.cambio()
            return radians(0)
        if (((self.x + 50) ** 2 + self.y ** 2) ** 0.5) > radio-100:
            self.cambio()
            return radians(180)
        if (((self.x) ** 2 + (self.y - 50) ** 2) ** 0.5) > radio-100:
            self.cambio()
            return radians(90)
        if (((self.x) ** 2 + (self.y + 50) ** 2) ** 0.5) > radio-100:
            self.cambio()
            return radians(270)
        
        # Ir a coordenadas de cima (si las hay)
        if llego_alguien():
            cima=llego_alguien()
            diferenciax=cima[0]-self.x
            diferenciay=cima[1]-self.y
            return math.atan2(diferenciay,diferenciax)
        
        # Nos aseguramos de que si algún miembro de nuestro equipo se encuentra en la cima, se detenga su movimiento.
        if self.cima:
            speed=0
        
        # Si detectamos un bucle, intentamos sacar al jugador de el.
        if loop_jugador4 and self.nombre=="jugador4":
            return math.atan2(self.y,self.x)+pi
        if loop_jugador1 and self.nombre=="jugador1":
            return math.atan2(self.y,self.x)+pi
        if loop_jugador3 and self.nombre=="jugador3":
            return math.atan2(self.y,self.x)+pi
        if loop_jugador2 and self.nombre=="jugador2":
            return math.atan2(self.y,self.x)+pi
        
        return self.donde_va()
    
    def cambio(self):
        """Si llegamos a tocar un límite del mapa, debemos ajustar nuestra estrategia y modificar los movimientos en consecuencia. 
        No podemos continuar moviéndonos en la misma dirección que nos llevó al límite.
        Entonces, cambiamos el orden de estrategia y con el, sus movimientos"""

        # Utilizamos variables globales para que la clase pueda utilizarlas.
        global orden_jugador1
        global orden_jugador2
        global orden_jugador4
        global orden_jugador3

        if self.nombre=="jugador1":
            orden_jugador1=not(orden_jugador1)
        if self.nombre=="jugador2":
            orden_jugador2=not(orden_jugador2)
        if self.nombre=="jugador4":
            orden_jugador4=not(orden_jugador4)
        if self.nombre=="jugador3":
            orden_jugador3=not(orden_jugador3)
    def donde_va(self):
        """Segun el orden establecido, indica a cada jugador que movimientos adaptar"""
        if self.nombre=="jugador1" and orden_jugador1:
            return self.norte()
        elif self.nombre=="jugador4" and orden_jugador4:
            return self.oeste()
        elif self.nombre=="jugador2" and orden_jugador2:
            return self.este()
        elif self.nombre=="jugador3" and orden_jugador3:
            return self.sur()
        elif self.nombre=="jugador1":
            return self.suroeste()
        elif self.nombre=="jugador4":
            return self.sureste()
        elif self.nombre=="jugador2":
            return self.noroeste()
        elif self.nombre=="jugador3":
            return self.noreste()
        
    # Las siguientes cuatro estrategias, que serán las iniciales, se enfocan en solamente ascender y descender.
    # Estas estrategias permiten a los jugadores desplazarse a una velocidad más rápida, pero cubren una menor área en el mapa.
    # Serán las primeras en ser utilizadas en un intento de ganar en el menor tiempo posible

    def norte(self):
        """Envía al jugador en busca de montañas en coordenadas y > 0
        Esto lo mantiene en el area superior del mapa"""
        if self.dx>0 and self.dy>0:
            return math.atan2(self.dy,self.dx)
        elif self.dx<0 and self.dy>0:
            return math.atan2(self.dy,self.dx)
        elif self.dx>0 and self.dy<0:
            return math.atan2(self.dy*-1,self.dx*-1)
        elif self.dx<0 and self.dy<0:
            return math.atan2(self.dy*-1,self.dx*-1)
    def oeste(self):
        """Envía al jugador en busca de montañas en coordenadas x < 0
        Esto lo mantiene en el area izquierda del mapa"""
        if self.dx>0 and self.dy>0:
            return math.atan2(self.dy*-1,self.dx*-1)
        if self.dx<0 and self.dy>0:
            return math.atan2(self.dy,self.dx)
        if self.dx>0 and self.dy<0:
            return math.atan2(self.dy*-1,self.dx*-1)
        if self.dx<0 and self.dy<0:
            return math.atan2(self.dy,self.dx)
    def este(self):
        """Envía al jugador en busca de montañas en coordenadas x > 0
        Esto lo mantiene en el area derecha del mapa"""
        if self.dx>0 and self.dy>0:
            return math.atan2(self.dy,self.dx)
        if self.dx<0 and self.dy>0:
            return math.atan2(self.dy*-1,self.dx*-1)
        if self.dx>0 and self.dy<0:
            return math.atan2(self.dy,self.dx)
        if self.dx<0 and self.dy<0:
            return math.atan2(self.dy*-1,self.dx*-1)
    def sur(self):
        """Envía al jugador en busca de montañas en coordenadas y < 0
        Esto lo mantiene en el area inferior del mapa"""
        if self.dx>0 and self.dy>0:
            return math.atan2(self.dy*-1,self.dx*-1)
        if self.dx<0 and self.dy>0:
            return math.atan2(self.dy*-1,self.dx*-1)
        if self.dx>0 and self.dy<0:
            return math.atan2(self.dy,self.dx)
        if self.dx<0 and self.dy<0:
            return math.atan2(self.dy,self.dx)
        
    # Estas siguientes cuatro estrategias son menos veloces,
    # Lo que significa que no son tan eficientes pero permiten cubrir una mayor área en el mapa.
    # Se ejecutan en caso de cambio en el orden inicial, y son más adecuadas para la búsqueda amplia.

    def noreste(self):
        """Envía al jugador en busca de montañas en coordenadas x>0, y>0
        Esto lo mantiene en el sector superior derecho del mapa"""
        if self.dx>0 and self.dy>0:
            return math.atan2(self.dy,self.dx)
        if self.dx>0 and self.dy<0:
            return radians(90)
        if self.dx<0 and self.dy>0:
            return radians(90)
        if self.dx<0 and self.dy<0:
            return radians(0)
    def noroeste(self):
        """Envía al jugador en busca de montañas en coordenadas x<0 e y>0
        Esto lo mantiene en el sector superior izquierdo del mapa"""
        if self.dx>0 and self.dy>0:
            return radians(90)
        if self.dx<0 and self.dy>0:
            return math.atan2(self.dy,self.dx)
        if self.dx>0 and self.dy<0:
            return radians(180)
        if self.dx<0 and self.dy<0:
            return radians(90)
    def sureste(self):
        """Envía al jugador en busca de montañas en coordenadas x>0 e y<0
        Esto lo mantiene en el sector inferior derecho del mapa"""
        if self.dx>0 and self.dy>0:
            return radians(270)
        if self.dx<0 and self.dy>0:
            return radians(0)
        if self.dx>0 and self.dy<0:
            return math.atan2(self.dy,self.dx)
        if self.dx<0 and self.dy<0:
            return radians(270)
    def suroeste(self):
        """Envía al jugador en busca de montañas en coordenadas x<0 e y<0
        Esto lo mantiene en el sector inferior izquierdo del mapa"""
        if self.dx>0 and self.dy>0:
            return radians(180)
        if self.dx<0 and self.dy>0:
            return radians(270)
        if self.dx>0 and self.dy<0:
            return radians(270)
        if self.dx<0 and self.dy<0:
            return math.atan2(self.dy,self.dx)
        
# Estas variables corresponden al orden con el que comenzarán a moverse los jugadores.
orden_jugador1=True
orden_jugador2=True
orden_jugador3=True
orden_jugador4=True
# Variables que luego identificarán los bucles
loop_jugador2=False
loop_jugador3=False
loop_jugador1=False
loop_jugador4=False

def bucle(loop_jugador1,loop_jugador2,loop_jugador4,loop_jugador3):
    """ Realizamos una verificación cada diez iteraciones para comprobar si la última coordenada es diferente 
    De las últimas treinta coordenadas registradas. Si se repite al menos tres veces, interpretamos que 
    el jugador se encuentra en un bucle y actualizamos la variable llamada 'loop'.
    Además, redondeamos las variables involucradas para obtener una mayor precisión en los cálculos."""
    if iteraciones%10==0:
        contadorx=0
        for x in coordenadas_x_jugador1[-30:-1]:
            if round(x,0)//10== round(jugador1_ubicacion.get('x'),0)//10:
                contadorx+=1
        contadory=0
        for x in coordenadas_y_jugador1[-30:-1]:
            if round(x,0)//10== round(jugador1_ubicacion.get('y'),0)//10:
                    contadory+=1
        if contadorx>2 and contadory>2:
            loop_jugador1=True
        else:
            loop_jugador1=False
        
        contadory=0
        for x in coordenadas_y_jugador2[-30:-1]:
                if round(x,0)//10== round(jugador2_ubicacion.get('y'),0)//10:
                    contadory+=1
        contadorx=0
        for x in coordenadas_x_jugador2[-30:-1]:
                if round(x,0)//10== round(jugador2_ubicacion.get('x'),0)//10:
                    contadorx+=1
        if contadorx>2 and contadory>2:
            loop_jugador2=True
        else:
            loop_jugador2=False
       
        contadorx=0
        for x in coordenadas_x_jugador3[-30:-1]:
                if round(x,0)//10== round(jugador3_ubicacion.get('x'),0)//10:
                    contadorx+=1
        contadory=0
        for x in coordenadas_y_jugador3[-30:-1]:
            if round(x,0)//10== round(jugador3_ubicacion.get('y'),0)//10:
                contadory+=1
        if contadorx>2 and contadory>2:
            loop_jugador3=True
        else:
            loop_jugador3=False
            
        contadorx=0
        for x in coordenadas_x_jugador4[-30:-1]:
            if round(x,0)//10== round(jugador4_ubicacion.get('x'),0)//10:
                contadorx+=1
        contadory=0
        for x in coordenadas_y_jugador4[-30:-1]:
            if round(x,0)//10== round(jugador4_ubicacion.get('y'),0)//10:
                contadory+=1
        if contadorx>2 and contadory>2:
            loop_jugador4=True
        else:
            loop_jugador4=False
        return loop_jugador1,loop_jugador2,loop_jugador4,loop_jugador3
        
    elif iteraciones%75==0:
        loop_jugador2=False
        loop_jugador3=False
        loop_jugador1=False
        loop_jugador4=False
        return loop_jugador1,loop_jugador2,loop_jugador4,loop_jugador3

# El código seguirá ejecutándose mientras el juego esté en curso.
while cliente.is_over()==False :
    # Una vez finalizada la fase de registro, el código saldrá del bucle y dará inicio al juego.
    while cliente.is_registering_teams():
        continue
    # Es importante que el codigo se ejecute cada 0.05 segundos para que el servidor se ejecute de manera correcta.
    time.sleep(0.05)
    
    # Actualizamos las variables con la información en tiempo real.
    jugador1_ubicacion, jugador4_ubicacion, jugador2_ubicacion, jugador3_ubicacion = ubicacion_nuestra()
    direcciones={}
    jugador1=movimientos(jugador1_ubicacion, "jugador1")
    jugador4=movimientos(jugador4_ubicacion, "jugador4")
    jugador2=movimientos(jugador2_ubicacion, "jugador2")
    jugador3=movimientos(jugador3_ubicacion, "jugador3")
    
    # Almacenamos las direcciones, seleccionadas por la clase, en un diccionario
    # Almacenamos nuestras coordenadas en listas separadas
    direcciones["jugador1"]= {'direction': jugador1.verificacion(), 'speed': speed}
    
    coordenadas_x_jugador1.append(jugador1_ubicacion.get("x"))
    coordenadas_y_jugador1.append(jugador1_ubicacion.get("y"))
    
    direcciones["jugador4"]= {'direction': jugador4.verificacion(), 'speed': speed}
    
    coordenadas_x_jugador4.append(jugador4_ubicacion.get("x"))
    coordenadas_y_jugador4.append(jugador4_ubicacion.get("y"))
    
    direcciones["jugador2"]= {'direction': jugador2.verificacion(), 'speed': speed}
    
    coordenadas_x_jugador2.append(jugador2_ubicacion.get("x"))
    coordenadas_y_jugador2.append(jugador2_ubicacion.get("y"))
    
    direcciones["jugador3"]= {'direction': jugador3.verificacion(), 'speed': speed}
    
    coordenadas_x_jugador3.append(jugador3_ubicacion.get("x"))
    coordenadas_y_jugador3.append(jugador3_ubicacion.get("y"))

    iteraciones+=1
    # Realizamos una verificación en busca de posibles bucles.
    if bucle(loop_jugador1,loop_jugador2,loop_jugador4,loop_jugador3):
        loop_jugador1,loop_jugador2,loop_jugador4,loop_jugador3 = bucle(loop_jugador1,loop_jugador2,loop_jugador4,loop_jugador3)

    # Enviamos las direcciones
    cliente.next_iteration("Elite del ascenso", direcciones)