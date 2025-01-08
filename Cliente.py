from communication.client.client import MountainClient
import time
from math import radians
import math
iteraciones=0
#Registro
cliente=MountainClient()
cliente.add_team("Elite del ascenso",["jugador1","jugador4", "jugador2", "jugador3"])
cliente.finish_registration()
def ubicacion_nuestra():
    """Devuelve la información de cada uno de los integrante de nuestro equipo en 'tiempo real'"""
    nuestro_equipo=cliente.get_data().get("Elite del ascenso")
    jugador1_ubi=nuestro_equipo.get("jugador1")
    jugador4_ubi=nuestro_equipo.get("jugador4")
    jugador2_ubi=nuestro_equipo.get("jugador2")
    jugador3_ubi=nuestro_equipo.get("jugador3")
    return jugador1_ubi, jugador4_ubi, jugador2_ubi, jugador3_ubi
jugador1_ubi, jugador4_ubi, jugador2_ubi, jugador3_ubi = ubicacion_nuestra()
# Chequea si alguien ya llego
def llego_alguien():
    """Chequea si llego alguien. i alguien llego, nos devuelve las coordenadas de la cima"""
    info=cliente.get_data()
    for equipo in info:
        datos_equipo = info.get(equipo)
        for escalador in datos_equipo:
            dato_escalador=datos_equipo.get(escalador)
            if dato_escalador.get("cima")==True:
                print(f"{escalador}llego")
                cima = [dato_escalador.get("x"), dato_escalador.get("y")]
                return cima
    return False
# Clase de escaladores con estrategias
class escaladores:
    def __init__(self,ubi,nombre):
        self.nombre=nombre
        self.x=ubi.get("x")
        self.y=ubi.get("y")
        self.z=ubi.get("z")
        self.dx=ubi.get("inclinacion_x")
        self.dy=ubi.get("inclinacion_y")
        self.cima=ubi.get("cima")
    def verificacion(self):
        """Verifica que el jugador no se este yendo de los limites.
        En caso de irse, lo envia hacia el lado contrario, e invierte el orden
        Al invertir el orden, todos iran en direccion contraria a la que estaban yendo"""
        if (((self.x - 50) ** 2 + self.y ** 2) ** 0.5) > 22900:
            self.cambio()
            return radians(0)
        if (((self.x + 50) ** 2 + self.y ** 2) ** 0.5) > 22900:
            self.cambio()
            return radians(180)
        if (((self.x) ** 2 + (self.y - 50) ** 2) ** 0.5) > 22900:
            self.cambio()
            return radians(90)
        if (((self.x) ** 2 + (self.y + 50) ** 2) ** 0.5) > 22900:
            self.cambio()
            return radians(270)
        return self.donde_va()
    def cambio(self):
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
        """Segun el orden, indica a cada jugador hacia que direccion dirigirse"""
        if self.nombre=="jugador1" and orden_jugador1:
            return self.arriba()
        if self.nombre=="jugador4" and orden_jugador4:
            return self.izquierda()
        if self.nombre=="jugador2" and orden_jugador2:
            return self.derecha()
        if self.nombre=="jugador3" and orden_jugador3:
            return self.abajo()
        if self.nombre=="jugador1":
            return self.abajo()
        if self.nombre=="jugador4":
            return self.derecha()
        if self.nombre=="jugador2":
            return self.izquierda()
        if self.nombre=="jugador3":
            return self.arriba()
    def arriba(self):
        """Envía al jugador en busca de montañas en dy>0
        Esto lo mantiene en el area superior del mapa"""
        if self.dx>0 and self.dy>0:
            return math.atan2(self.dy,self.dx)
        if self.dx<0 and self.dy>0:
            return math.atan2(self.dy,self.dx)
        if self.dx>0 and self.dy<0:
            return math.atan2(self.dy*-1,self.dx*-1)
        if self.dx<0 and self.dy<0:
            return math.atan2(self.dy*-1,self.dx*-1)
    def izquierda(self):
        """Envía al jugador en busca de montañas en x<0
        Esto lo mantiene en el area izquierdo del mapa"""
        if self.dx>0 and self.dy>0:
            return math.atan2(self.dy*-1,self.dx*-1)
        if self.dx<0 and self.dy>0:
            return math.atan2(self.dy,self.dx)
        if self.dx>0 and self.dy<0:
            return math.atan2(self.dy*-1,self.dx*-1)
        if self.dx<0 and self.dy<0:
            return math.atan2(self.dy,self.dx)
    def derecha(self):
        """Envía al jugador en busca de montañas en x>0
        Esto lo mantiene del lado derecho del mapa"""
        if self.dx>0 and self.dy>0:
            return math.atan2(self.dy,self.dx)
        if self.dx<0 and self.dy>0:
            return math.atan2(self.dy*-1,self.dx*-1)
        if self.dx>0 and self.dy<0:
            return math.atan2(self.dy,self.dx)
        if self.dx<0 and self.dy<0:
            return math.atan2(self.dy*-1,self.dx*-1)
    def abajo(self):
        """Envía al jugador en busca de montañas en y<0
        Esto lo mantiene en el area inferior del mapa"""
        if self.dx>0 and self.dy>0:
            return math.atan2(self.dy*-1,self.dx*-1)
        if self.dx<0 and self.dy>0:
            return math.atan2(self.dy*-1,self.dx*-1)
        if self.dx>0 and self.dy<0:
            return math.atan2(self.dy,self.dx)
        if self.dx<0 and self.dy<0:
            return math.atan2(self.dy,self.dx)
orden_jugador1=True
orden_jugador2=True
orden_jugador3=True
orden_jugador4=True
#Mientras el juego siga, le mando
while cliente.is_over()==False:
    if llego_alguien():
        break
    time.sleep(0.05) # Esta es una funcion para que no me tire toda la info a los pedos
    print(cliente.get_data())
    #Guarda las data de cada uno individual
    jugador1_ubi, jugador4W_ubi, jugador2_ubi, jugador3_ubi = ubicacion_nuestra()
    direcciones={}
    jugador1=escaladores(jugador1_ubi, "jugador1")
    jugador4=escaladores(jugador4_ubi, "jugador4")
    jugador2=escaladores(jugador2_ubi, "jugador2")
    jugador3=escaladores(jugador3_ubi, "jugador3")
    direcciones["jugador1"]= {'direction': jugador1.verificacion(), 'speed': 50}
    direcciones["jugador4"]= {'direction': jugador4.verificacion(), 'speed': 50}
    direcciones["jugador2"]= {'direction': jugador2.verificacion(), 'speed': 50}
    direcciones["jugador3"]= {'direction': jugador3.verificacion(), 'speed': 50}
    print(f"\nproximas direcciones:{direcciones}\n")
    cliente.next_iteration("Elite del ascenso", direcciones)
    iteraciones+=1
    print(iteraciones)
llego_alguien()