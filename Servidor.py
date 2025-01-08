from communication.server.mountain.rastrigin_mountain import RastriginMountain

from communication.server.server import MountainServer 

montaña=RastriginMountain(50,23000)
s=MountainServer(montaña,(14000,14000),50)
s.start()