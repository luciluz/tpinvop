import sys
#importamos el modulo cplex
import cplex
from recordclass import recordclass

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
        self.dias = 6
        self.turnos = 5
        self.costo_por_conflicto = 0        #Aca definimos los costos por conflicto y repeticion
        self.costo_por_repeticion = 0       #Definimos los valores como negativos (como queremos que aparezcan en FO)
        
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
    
    T = instancia.cantidad_trabajadores
    N = instancia.cantidad_ordenes
    dias = instancia.dias
    turnos = instancia.turnos
    costo_por_conflicto = instancia.costo_por_conflicto
    costo_por_repeticion = instancia.costo_por_repeticion
    
    # Llenar coef\_funcion\_objetivo
    #coeficientes_funcion_objetivo = .... # no sé bien que es esto

    # Poner nombre a las variables
    coeficientes_funcion_objetivo = []
    nombres = []
    lb = []
    ub = []
    types = []
    
    
    # Variables A_ijhk
    for i in range(N):          
        for j in range(dias):       # 1 si la orden i se realiza el día j en el turno h por el trabajador k
            for h in range(turnos): # 0 c.c.
                for k in range(T):
                    coeficientes_funcion_objetivo.append(0) 
                    nombres.append(f"A_{i}_{j}_{h}_{k}")
                    lb.append(0)
                    ub.append(1)
                    types.append("B")  # esto le dice que la variable es binaria
    
    # Variables X_ijh:
    for i in range(N):          
        for j in range(dias):       # 1 si la orden i se realiza el dia j en el turno h
            for h in range(turnos): # 0 c.c.
                coeficientes_funcion_objetivo.append(0)
                nombres.append(f"x_{i}_{j}_{h}")
                lb.append(0)
                ub.append(1)
                types.append("B")
    
    # Variables w_jhk:
    for j in range(dias):       
        for h in range(turnos):     # 1 si el trabajador k trabaja en el día j en el turno h
            for k in range(T):      # 0 c.c.
                coeficientes_funcion_objetivo.append(0)  
                nombres.append(f"w_{j}_{h}_{k}")
                lb.append(0)
                ub.append(1)
                types.append("B")  
    
    # Variables y_ik                        
    for i in range(N):          
        for k in range(T):      
            coeficientes_funcion_objetivo.append(0)  
            nombres.append(f"y_{i}_{k}")
            lb.append(0)
            ub.append(1)
            types.append("B")  # abajo el binarismo
            
    # variables z_i
    for i in range(N):
        coeficientes_funcion_objetivo.append(instancia.ordenes[i].beneficio)
        nombres.append(f"z_{i}")
        lb.append(0)
        ub.append(1)
        types.append("B")        
        
    # variables d_hk
    for j in range(dias):
        for k in range(T):
            coeficientes_funcion_objetivo.append(0)  
            nombres.append(f"d_{j}_{k}")
            lb.append(0)
            ub.append(1)
            types.append("B")
            
    # # variables C_i_k_k*
    for i in range(N):
        for k1 in range(T):
            for k2 in range(T):
                coeficientes_funcion_objetivo.append(costo_por_conflicto)  
                nombres.append(f"C_{i}_{k1}_{k2}")
                lb.append(0)
                ub.append(1)
                types.append("B")
                
    # variables R_i_i*_k
    for i1 in range(N):
        for i2 in range(N):
            for k in range(T):
                coeficientes_funcion_objetivo.append(costo_por_repeticion)  
                nombres.append(f"R_{i1}_{i2}_{k}")
                lb.append(0)
                ub.append(1)
                types.append("B")
                
    # variables P_k
    for k in range(T):
        coeficientes_funcion_objetivo.append(-1)  
        nombres.append(f"P_{k}")
        lb.append(0)
        ub.append(40500)
        types.append("B")
        
    # variables p_k_num
    for k in range(T):
        for num in range(3): #las primeras tres van entre 0 y 5
            coeficientes_funcion_objetivo.append(0)  
            nombres.append(f"p_{k}_{num}")
            lb.append(0)
            ub.append(5)
            types.append("B")
        
        # La ultima va de 0 a 15.
        coeficientes_funcion_objetivo.append(0)  
        nombres.append(f"p_{k}_3") 
        lb.append(0)
        ub.append(15)
        types.append("B")
        
    # y variables f_k_num
    for k in range(T):   
        for num in range(3):
            coeficientes_funcion_objetivo.append(0)  
            nombres.append(f"f_{k}_{num}") 
            lb.append(0)
            ub.append(1)
            types.append("B")    
    
    coeficientes_funcion_objetivo = [float(c) for c in coeficientes_funcion_objetivo]
    # Agregar todas las variables
    prob.variables.add(obj=coeficientes_funcion_objetivo, lb = lb, ub = ub, types=types, names=nombres)


def agregar_restricciones(prob, instancia):        
    N = instancia.cantidad_ordenes
    T = instancia.cantidad_trabajadores
    dias = instancia.dias
    turnos = instancia.turnos
    
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
                        indices = [f"A_{i}_{j}_{h}_{k}", f"x_{i}_{j}_{h}", f"w_{j}_{h}_{k}", f"y_{i}_{k}"]
                        valores = [3, -1, -1, -1]  # coeficientes de las variables de arriba
                        prob.linear_constraints.add(
                            lin_expr=[[indices, valores]],
                            senses=['L'],  # L es <=, G es >=, E es ==
                            rhs=[0],
                            names=[f"coherencias A_{i}_{j}_{h}_{k} (1)"]
                        )
                        
                        # -A_ijhk + x_ijh + w_jhk + y_ik <= 2
                        indices = [f"A_{i}_{j}_{h}_{k}", f"x_{i}_{j}_{h}", f"w_{j}_{h}_{k}", f"y_{i}_{k}"]
                        valores = [-1, 1, 1, 1]  
                        prob.linear_constraints.add(
                            lin_expr=[[indices, valores]],
                            senses=['L'],
                            rhs=[2],
                            names=[f"coherencia A_{i}_{j}_{h}_{k} (2)"]
                        )
                        
    # que las variables z_i tengan coherencia con las x_ijh
    for i in range(N):
        indices = [f"z_{i}"] + [f"x_{i}_{j}_{h}" for j in range(dias) for h in range(turnos)]
        valores = [1] + [-1]*(dias*turnos)
        prob.linear_constraints.add(
                lin_expr=[[indices,valores]],
                senses=['E'],
                rhs=[0],
                names=[f"coherencia z_{i}"]
            )
        
    # que las variables d_jk tengan coherencia con las w_jhk
    for j in range(dias):
        for k in range(T):
            indices = [f"d_{j}_{k}"] + [f"w_{j}_{h}_{k}" for h in range(turnos)]
            valores = [1] + [-1]*turnos
            prob.linear_constraints.add(
                    lin_expr=[[indices,valores]],
                    senses=['G'],
                    rhs=[0],
                    names=[f"coherencia d_{j}_{k} (1)"]
                )
            
    for j in range(dias):
        for k in range(T):
            indices = [f"d_{j}_{k}"] + [f"w_{j}_{h}_{k}" for h in range(turnos)]
            valores = [5] + [-1]*turnos
            prob.linear_constraints.add(
                    lin_expr=[[indices,valores]],
                    senses=['L'],
                    rhs=[0],
                    names=[f"coherencia d_{j}_{k} (2)"]
                )
            
    # Si una orden se realiza, entonces debe tener exactamente t_i trabajadores asignados
    for i in range(N):
        for j in range(dias):
            for h in range(turnos):
                # t_i*x_ijh == Σ_k A_ijhk
                indices = [f"x_{i}_{j}_{h}"] + [f"A_{i}_{j}_{h}_{k}" for k in range(T)]
                valores = [int(instancia.ordenes[i].cant_trab)] + [-1] * T  # coeficientes de las variables de arriba
                prob.linear_constraints.add(
                    lin_expr=[[indices, valores]],
                    senses=['E'],  # L es <=, G es >=, E es ==
                    rhs=[0],
                    names=[f"Cumple trabajadores_{i}_{j}_{h}"] 
                )
                  
    # Cada orden de trabajo puede ser asignada a lo sumo a un turno
    for i in range(N):
        indices = [f"x_{i}_{j}_{h}" for j in range(dias) for h in range(turnos)]
        valores = [1]*(dias*turnos)
        prob.linear_constraints.add(
            lin_expr=[[indices, valores]],
            senses=['L'],
            rhs=[1],
            names=[f"Tiene Turno_{i}"] 
        )
    
    # Un mismo trabajador no puede estar asignado a dos ordenes en un mismo turno
    for i in range(N):
        indices = [f"A_{i}_{j}_{h}_{k}" for j in range(dias) for h in range(turnos) for k in range(T)]
        valores = [1]*(dias*turnos*T)
        prob.linear_constraints.add(
            lin_expr=[[indices, valores]],
            senses=['L'],
            rhs=[1],
            names=[f"TrabajadorNoSeDuplica_{i}"] 
        )
    
    
    # Cada trabajador tiene que tener a lo sumo un día en el que no trabaje
    for k in range(T):
        indices = [f"d_{j}_{k}" for j in range(dias)]
        valores = [1]*dias
        prob.linear_constraints.add(
            lin_expr=[[indices, valores]],
            senses=['L'],
            rhs=[5],
            names=[f"TrabajadorTieneFranco_{k}"] 
        )
    
    # Ningún trabajador puede estar asignado a una tarea en los 5 turnos de un mismo día
    for j in range(dias):
        for k in range(T):
            indices = [f"w_{j}_{h}_{k}" for h in range(turnos)]
            valores = [1]*turnos
            prob.linear_constraints.add(
                lin_expr=[[indices, valores]],
                senses=['L'],
                rhs=[4],
                names=[f"TrabajadorDescansaUnTurno_{j}_{k}"] 
            )
    
    # Hay pares de órdenes que no pueden ser satisfechas consecutivamente el mismo día (por ej si están alejadas geográficamente)
    for a, b in instancia.ordenes_conflictivas:
        for j in range(dias):
            for h in range(turnos-1):
                # para restringir que b esté después de a
                indices = [f"x_{b}_{j}_{h}", f"x_{a}_{j}_{h+1}"]
                valores = [1,1]
                prob.linear_constraints.add(
                    lin_expr=[[indices, valores]],
                    senses=['L'],
                    rhs=[1],
                    names=[f"OrdenesConflictivas_{a}_{b}_{j}_{h} (ida)"]
                )
                    
                    
                # para restringir que a esté después de b    
                indices = [f"x_{a}_{j}_{h}", f"x_{b}_{j}_{h+1}"]
                valores = [1, 1]
                prob.linear_constraints.add(
                    lin_expr=[[indices, valores]],
                    senses=['L'],
                    rhs=[1],
                    names=[f"OrdenesConflictiva_{b}_{a}_{j}_{h} (vuelta)"]
                )
        
    # Hay pares de órdenes que deben ser resueltas consecutivamente el mismo día
    for a, b in instancia.ordenes_correlativas:
        for j in range(dias):
            for h in range(turnos-1):
                # para restringir que b esté después de a    
                indices = [f"x_{a}_{j}_{h}", f"x_{b}_{j}_{h+1}"]
                valores = [1, -1]
                prob.linear_constraints.add(
                    lin_expr=[[indices, valores]],
                    senses=['L'],
                    rhs=[0],
                    names=[f"OrdenesCorrelativas_{a}_{b}_{j}_{h} (1)"]
                )

        
        # si se cumple b quiero que a también
        indices = [f"z_{a}", f"z_{b}"]
        valores = [1, -1]
        prob.linear_constraints.add(
            lin_expr=[[indices, valores]],
            senses=['G'],
            rhs=[0],
            names=[f"OrdenesCorrelativas_{a}_{b} (2)"]
        )
        
        # que tarea a nunca se pueda hacer el último turno de cualquier día
        indices = [f"x_{a}_{j}_{4}" for j in range(dias)]
        valores = [1]*dias
        prob.linear_constraints.add(
            lin_expr=[[indices, valores]],
            senses=['E'],
            rhs=[0],
            names=[f"OrdenesCorrelativas_{a}_{b} (2)"]
        )
    
    # La diferencia entre el trabajador con más órdenes (x) y el con menos (y) tiene que ser menor o igual a 8 (x-y<=8)
    for k1 in range(T):
        for k2 in range(T):
            if k1 != k2:
                indices = [f"y_{i}_{k1}" for i in range(N)] + [f"y_{i}_{k2}" for i in range(N)]
                valores = [1]*N + [-1]*N
                prob.linear_constraints.add(
                    lin_expr=[[indices, valores]],
                    senses=['L'],
                    rhs=[8],
                    names=[f"AsignacionParejaDeTareas_{k1}_{k2}"]
                )
    
    # El esquema de remuneraciones debe ponerse como restricciones
    
    #Se pagan todas las tareas completadas
    for k in range(T):
        indices = [f"p_{k}_{num}" for num in range (4)] + [f"y_{i}_{k}" for i in range(N)]
        valores = [1]*4 + [-1]*N 
        prob.linear_constraints.add(
            lin_expr=[[indices, valores]],
            senses=['E'],
            rhs=[0],
            names=[f"SePagaAlTrabajador_{k}"]
        )
        
    #P_k = 1000p_k0 + 1200p_k1 + 1400_p_k3 + 1500p_k4   
    for k in range(T):
        indices = [f"P_{k}"] + [f"p_{k}_{num}" for num in range (4)] 
        valores = [1, -1000, -1200, -1400, -1500]
        prob.linear_constraints.add(
            lin_expr=[[indices, valores]],
            senses=['E'],
            rhs=[0],
            names=[f"Pagos_{k}"]
        )
    
    #Agrego restricciones para la integralidad de p_k0  a p_k4
    for k in range(T):
        indices = [f"f_{k}_{0}", f"p_{k}_{1}"]   # 5f_k0 <= p_k0 
        valores = [5, -1]
        prob.linear_constraints.add(
            lin_expr=[[indices, valores]],
            senses=['L'],
            rhs=[0],
            names=[f"Pagos_{k} (2)"]
        )
        
        indices = [f"p_{k}_{0}"]                # p_k0 <= 5
        valores = [1]
        prob.linear_constraints.add(
            lin_expr=[[indices, valores]],
            senses=['L'],
            rhs=[5],
            names=[f"Pagos_{k} (3)"]
        )
        
        indices = [f"f_{k}_{1}", f"p_{k}_{1}"]  # 5f_k1 <= p_k1 
        valores = [5, -1]
        prob.linear_constraints.add(
            lin_expr=[[indices, valores]],
            senses=['L'],
            rhs=[0],
            names=[f"Pagos_{k} (4)"]
        )
        
        indices = [f"p_{k}_{1}", f"p_{k}_{0}"]   # p_k1 <= 5f_k0
        valores = [1, -5]
        prob.linear_constraints.add(
            lin_expr=[[indices, valores]],
            senses=['L'],
            rhs=[0],
            names=[f"Pagos_{k} (5)"]
        )
        
        indices = [f"f_{k}_{2}", f"p_{k}_{2}"]  # 5f_k2 <= p_k2 
        valores = [5, -1]
        prob.linear_constraints.add(
            lin_expr=[[indices, valores]],
            senses=['L'],
            rhs=[0],
            names=[f"Pagos_{k} (6)"]
        )
        
        indices = [f"p_{k}_{0}", f"p_{k}_{1}"]   # p_k2 <= 5f_k1
        valores = [1, -5]
        prob.linear_constraints.add(
            lin_expr=[[indices, valores]],
            senses=['L'],
            rhs=[0],
            names=[f"Pagos_{k} (7)"]
        )
        
        indices = [f"p_{k}_{3}"]                 # 0 <= p_k3 
        valores = [1]
        prob.linear_constraints.add(
            lin_expr=[[indices, valores]],
            senses=['G'],
            rhs=[0],
            names=[f"Pagos_{k} (8)"]
        )
        
        indices = [f"p_{k}_{0}", f"p_{k}_{2}"]   # p_k3 <= 15f_k2
        valores = [1, -15]
        prob.linear_constraints.add(
            lin_expr=[[indices, valores]],
            senses=['L'],
            rhs=[0],
            names=[f"Pagos_{k} (9)"]
        )
        
    # Las siguientes son las restricciones deseables, sólo las haremos una vez tengamos el resto del modelo y veamos que funciona
        # Conflictos entre trabajadores que hacen que prefieran no ser asignados a la misma orden
    # ACÁ SE ESTÁ INDEXANDO MAL. k1 y k2 son ordenes no podemos indexarlas como trabajadores
    
    for k1, k2 in instancia.conflictos_trabajadores:
        for i in range(N):
            indices = [f"y_{i}_{k1}", f"y_{i}_{k2}", f"C_{i}_{k1}_{k2}"] 
            valores = [1, 1, -1]
            prob.linear_constraints.add(
            lin_expr=[[indices, valores]],
            senses=['L'],
            rhs=[0],
            names=[f"ConflictosTrabajadores_{k1}_{k2}_{i}"]
                )
            
         # Pares de órdenes que son repetitivas por lo que se prefiere que no sean asignadas al mismo trabajador       
    for i1, i2 in instancia.ordenes_repetitivas:
        for k in range(T):
            indices = [f"y_{i1}_{k}", f"y_{i2}_{k}", f"R_{i1}_{i2}_{k}"] 
            valores = [1, 1, -1]
            prob.linear_constraints.add(
            lin_expr=[[indices, valores]],
            senses=['L'],
            rhs=[0],
            names=[f"OrdenesRepetitivas_{i1}_{i2}_{k}"]
                )

def armar_lp(prob, instancia):
    
    # Agregar las variables
    agregar_variables(prob, instancia)
   
    # Agregar las restricciones 
    agregar_restricciones(prob, instancia)

    # Setear el sentido del problema
    prob.objective.set_sense(prob.objective.sense.maximize)

    # Escribir el lp a archivo
    prob.write('asignacionCuadrillas.lp')

def resolver_lp(prob):
    
    # Definir los parametros del solver
       
    # Resolver el lp
    prob.solve()

def mostrar_solucion(prob,instancia):
    # Obtener informacion de la solucion a traves de 'solution'
    
    # Tomar el estado de la resolucion
    status = prob.solution.get_status_string(status_code = prob.solution.get_status())
    
    # Tomar el valor del funcional
    valor_obj = prob.solution.get_objective_value()
    
    print('Funcion objetivo: ',valor_obj,'(' + str(status) + ')')
    
    # Tomar los valores de las variables
    x  = prob.solution.get_values()
    # Mostrar las variables con valor positivo (mayor que una tolerancia)
    #.....

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
