# Trabajo Práctico PLE - Asignación de cuadrillas

En el presente trabajo práctico se aborda un problema de asignación óptima de cuadrillas de trabajadores a órdenes de servicio. Para su solución se propone un modelo matemático de Programación Lineal Entera (PLE) implementado para ser usado en CPLEX, buscando maximizar las ganancias de la empresa al asignar los trabajadores. Más allá de que el modelo funcione correctamente, el objetivo de este trabajo fue poder testear diferentes parámetros de CPLEX y ver cómo estos podían afectar a la eficiencia del modelo, además de implementar restricciones deseables y medir el impacto que tenían estas en la función objetivo. Los resultados muestran que el ajuste de parámetros varía dependiendo del tipo de instancia y que las restricciones deseables pueden ser implementadas de distintas formas dependiendo de cómo se quiere medir la violación de una de estas restricciones. En conclusión, CPLEX parece adaptarse bastante bien a distintos contextos y necesidades operativas, pero hace falta un conocimiento detallado del problema para elegir bien el camino a tomar.  

- [Modelo con restricciones deseables](modelo-sin-deseables.py)  
- [Modelo con restricciones deseables](modelo-con-deseables.py)

- [Informe del proyecto](tp-PLE-Fernandez-Ruz.pdf)
