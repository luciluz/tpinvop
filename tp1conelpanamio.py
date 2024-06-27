import sys
#importamos el modulo cplex
import cplex
from recordclass import recordclass
#%%
TOLERANCE =10e-6 
Orden = recordclass('Orden', 'id beneficio cant_trab')

class InstanciaAsignacionCuadrillas:
    def __init__(self):
        self.cantidad_trabajadores = 0
        self.cantidad_ordenes = 0
        self.ordenes = []
        self.conflictos_trabajadores = []
        self.ordenes_correlativas = []
        self.ordenes_conflictivas = []
        self.ordenes_repetitivas = []
        
    def leer_datos(self,nombre_archivo):

        # Se abre el archivo
        f = open(nombre_archivo)

        # Lectura cantidad de trabajadores
        self.cantidad_trabajadores = int(f.readline())
        
        # Lectura cantidad de ordenes
        self.cantidad_ordenes = int(f.readline())
        
        # Lectura de las ordenes
        self.ordenes = []
        for i in range(self.cantidad_ordenes):
            linea = f.readline().rstrip().split(' ')
            self.ordenes.append(Orden(linea[0],linea[1],linea[2]))
        
        # Lectura cantidad de conflictos entre los trabajadores
        cantidad_conflictos_trabajadores = int(f.readline())
        
        # Lectura conflictos entre los trabajadores
        self.conflictos_trabajadores = []
        for i in range(cantidad_conflictos_trabajadores):
            linea = f.readline().split(' ')
            self.conflictos_trabajadores.append(list(map(int,linea)))
            
        # Lectura cantidad de ordenes correlativas
        cantidad_ordenes_correlativas = int(f.readline())
        
        # Lectura ordenes correlativas
        self.ordenes_correlativas = []
        for i in range(cantidad_ordenes_correlativas):
            linea = f.readline().split(' ')
            self.ordenes_correlativas.append(list(map(int,linea)))
            
        # Lectura cantidad de ordenes conflictivas
        cantidad_ordenes_conflictivas = int(f.readline())
        
        # Lectura ordenes conflictivas
        self.ordenes_conflictivas = []
        for i in range(cantidad_ordenes_conflictivas):
            linea = f.readline().split(' ')
            self.ordenes_conflictivas.append(list(map(int,linea)))
        
        # Lectura cantidad de ordenes repetitivas
        cantidad_ordenes_repetitivas = int(f.readline())
        
        # Lectura ordenes repetitivas
        self.ordenes_repetitivas = []
        for i in range(cantidad_ordenes_repetitivas):
            linea = f.readline().split(' ')
            self.ordenes_repetitivas.append(list(map(int,linea)))
        
        # Se cierra el archivo de entrada
        f.close()


def cargar_instancia():
    # El 1er parametro es el nombre del archivo de entrada 	
    nombre_archivo = sys.argv[1].strip()
    # Crea la instancia vacia
    instancia = InstanciaAsignacionCuadrillas()
    # Llena la instancia con los datos del archivo de entrada 
    instancia.leer_datos(nombre_archivo)
    return instancia

def agregar_variables(prob, instancia):
    # Definir y agregar las variables:
    # Variables x_ijhk 
        
	# metodo 'add' de 'variables', con parametros:
	# obj: costos de la funcion objetivo
	# lb: cotas inferiores
    # ub: cotas superiores
    # types: tipo de las variables
    # names: nombre (como van a aparecer en el archivo .lp)
    
    T = instancia.cantidad_trabajadores
    N = instancia.cantidad_ordenes
    dias = 6
    turnos = 5
    
    # cantidad de cada una de los tipos de variables
    var_A = N*dias*turnos*T	
    var_x = N*dias*turnos
    var_w = dias*turnos*T
    var_y = N*T
    
    # cantidad total de variables
    cantVar = var_A + var_x + var_w + var_y
    
    # Llenar coef\_funcion\_objetivo
    coeficientes_funcion_objetivo = .... # no sé bien que es esto

    # Poner nombre a las variables
    coeficientes_funcion_objetivo = []
    nombres = []
    types = []
    
    for i in range(N):          # Variables A_ijhk
        for j in range(dias):       # 1 si la orden i se realiza el día j en el turno h por el trabajador k
            for h in range(turnos): # 0 c.c.
                for k in range(T):
                    coeficientes_funcion_objetivo.append(0) # wtf is this?
                    nombres.append(f"A_{i+1}_{j+1}_{h+1}_{k+1}")
                    types.append("B")  # esto le dice que la variable es binaria
    
    for i in range(N):          # Variables X_ijh:
        for j in range(dias):       # 1 si la orden i se realiza el dia j en el turno h
            for h in range(turnos): # 0 c.c.
                coeficientes_funcion_objetivo.append(0) # me parece que esto es para las  restric. deseables? o función obj?
                nombres.append(f"x_{i+1}_{j+1}_{h+1}")
                types.append("B")  # binarias
    
    for j in range(dias):       # Variables w_jhk:
        for h in range(turnos):     # 1 si el trabajador k trabaja en el día j en el turno h
            for k in range(T):      # 0 c.c.
                coeficientes_funcion_objetivo.append(0)  # igual capaz es la función obj 
                nombres.append(f"w_{j+1}_{h+1}_{k+1}")
                types.append("B")  # qe poco progre
    
                            # Variables y_ik
    for i in range(N):          # 1 si el trabajador k es asignado a la orden i
        for k in range(T):      # 0 c.c.
            coeficientes_funcion_objetivo.append(0)  # la verdad ni idea para qué es esto :P
            nombres.append(f"y_{i+1}_{k+1}")
            types.append("B")  # abajo el binarismo
    
    # Agregar todas las variables
    prob.variables.add(obj=coeficientes_funcion_objetivo, lb = [0]*cantVar, ub = [1]*cantVar, types=types, names=nombres)


def agregar_restricciones(prob, instancia):
    # Agregar las restricciones ax <= (>= ==) b:
	# funcion 'add' de 'linear_constraints' con parametros:
	# lin_expr: lista de listas de [ind,val] de a
    # sense: lista de 'L', 'G' o 'E'
    # rhs: lista de los b
    # names: nombre (como van a aparecer en el archivo .lp)
	
    # Notar que cplex espera "una matriz de restricciones", es decir, una
    # lista de restricciones del tipo ax <= b, [ax <= b]. Por lo tanto, aun cuando
    # agreguemos una unica restriccion, tenemos que hacerlo como una lista de un unico
    # elemento.
        
    # Que los A tengan coherencia con las demás variables
    # A_ijhk <--> (x_ijh ∧ w_jhk ∧ y_ik)  para todo i,j,h,k
    # es decir:
        # 3*A_ijhk <= x_ijh + w_jhk + y_ik  (1)
        # 2+A_ijk <= x_ijh + w_jhk + y_ik   (2)
    for i in range(N):
            for j in range(dias):
                for h in range(turnos):
                    for k in range(T):
                        # 3*A_ijhk - x_ijh - w_jhk - y_ik <= 0
                        indices = [f"A_{i+1}_{j+1}_{h+1}_{k+1}", f"x_{i+1}_{j+1}_{h+1}", f"w_{j+1}_{h+1}_{k+1}", f"y_{i+1}_{k+1}"]
                        valores = [3, -1, -1, -1]  # coeficientes de las variables de arriba
                        prob.linear_constraints.add(
                            lin_expr=[[indices, valores]],
                            senses=['L'],  # L es <=, G es >=, E es ==
                            rhs=[0],
                            names=[f"coherencia1_{i+1}_{j+1}_{h+1}_{k+1}"]
                        )
                        
                        # -A_ijhk + x_ijh + w_jhk + y_ik <= 2
                        indices = [f"A_{i+1}_{j+1}_{h+1}_{k+1}", f"x_{i+1}_{j+1}_{h+1}", f"w_{j+1}_{h+1}_{k+1}", f"y_{i+1}_{k+1}"]
                        valores = [-1, 1, 1, 1]  
                        prob.linear_constraints.add(
                            lin_expr=[[indices, valores]],
                            senses=['L'],
                            rhs=[2],
                            names=[f"coherencia2_{i+1}_{j+1}_{h+1}_{k+1}"]
                        )
    
    # Si una orden se realiza, entonces debe tener exactamente t_i (ordenes[i]) trabajadores asignados
    for i in range(N):
        for j in range(dias):
            for h in range(turnos):
                # t_i*x_ijh == Σ_k A_ijhk
                indices = [f"x_{i+1}_{j+1}_{h+1}"] + [f"A_{i+1}_{j+1}_{h+1}_{k+1}" for k in range(T)]
                valores = [ordenes[i]] + [-1] * T  # coeficientes de las variables de arriba
                prob.linear_constraints.add(
                    lin_expr=[[indices, valores]],
                    senses=['E'],  # L es <=, G es >=, E es ==
                    rhs=[0],
                    names=[f"restriccion1_{i+1}_{j+1}_{h+1}"] # no se me ocurrió otro nombre 
                )
                    
    # Cada orden de trabajo puede ser asignada a lo sumo a un turno
    
    # Un mismo trabajador no puede estar asignado a dos ordenes en un mismo turno
    
    # Cada trabajador tiene que tener a lo sumo un día en el que no trabaje
    
    # Ningún trabajador puede estar asignado a una tarea en los 5 turnos de un mismo día
    
    # Hay pares de órdenes que no pueden ser satisfechas consecutivamente el mismo día (por ej si están alejadas geográficamente)
    
    # Hay pares de órdenes que deben ser resueltas consecutivamente el mismo día
    
    # La diferencia entre el trabajador con más órdenes (x) y el con menos (y) tiene que ser menor o igual a 8 (x-y<=8)
    
    # El esquema de remuneraciones debe ponerse como restricciones
    
    # Las siguientes son las restricciones deseables, sólo las haremos una vez tengamos el resto del modelo y veamos que funciona
        # Conflictos entre trabajadores que hacen que prefieran no ser asignados a la misma orden
        # Pares de órdenes que son repetitivas por lo que se prefiere que no sean asignadas al mismo trabajador

def armar_lp(prob, instancia):

    # Agregar las variables
    agregar_variables(prob, instancia)
   
    # Agregar las restricciones 
    agregar_restricciones(prob, instancia)

    # Setear el sentido del problema
    prob.objective.set_sense(prob.objective.sense.....)

    # Escribir el lp a archivo
    prob.write('asignacionCuadrillas.lp')

def resolver_lp(prob):
    
    # Definir los parametros del solver
    prob.parameters....
       
    # Resolver el lp
    prob.solve()

#def mostrar_solucion(prob,instancia):
    # Obtener informacion de la solucion a traves de 'solution'
    
    # Tomar el estado de la resolucion
    status = prob.solution.get_status_string(status_code = prob.solution.get_status())
    
    # Tomar el valor del funcional
    valor_obj = prob.solution.get_objective_value()
    
    print('Funcion objetivo: ',valor_obj,'(' + str(status) + ')')
    
    # Tomar los valores de las variables
    x  = prob.solution.get_values()
    # Mostrar las variables con valor positivo (mayor que una tolerancia)
    .....

def main():
    
    # Lectura de datos desde el archivo de entrada
    instancia = cargar_instancia()
    
    # Definicion del problema de Cplex
    prob = cplex.Cplex()
    
    # Definicion del modelo
    armar_lp(prob,instancia)

    # Resolucion del modelo
    resolver_lp(prob)

    # Obtencion de la solucion
    mostrar_solucion(prob,instancia)

if __name__ == '__main__':
    main()
