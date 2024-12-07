"""
Brandon Stiven Jimenez Romero
Cod: 2371717-2724
Sistemas Operativos
Tecnologia en Desarollo de Software
Universidad del Valle
"""
# Clase que define un Proceso con varios atributos
class Process:
    def __init__(self, label, burst_time, arrival_time, queue, priority):
        # Identificadores y tiempos asociados al proceso
        self.label = label
        self.burst_time = burst_time  # Tiempo total que el proceso necesita para ejecutarse
        self.remaining_time = burst_time  # Tiempo restante para ejecutar el proceso
        self.arrival_time = arrival_time  # Momento en que el proceso llega al sistema
        self.queue = queue  # Cola a la que pertenece el proceso (basado en prioridad)
        self.priority = priority  # Prioridad del proceso dentro de su cola (5 es la mayor prioridad)
        self.wait_time = 0  # Tiempo que el proceso ha esperado en las colas
        self.turnaround_time = 0  # Tiempo total en el sistema (desde que llega hasta que termina)
        self.completion_time = 0  # Momento en que el proceso finaliza su ejecución
        self.response_time = -1  # Tiempo de respuesta, se calcula la primera vez que el proceso se ejecuta

class MLQScheduler:
    def __init__(self, scheme=1):
        # Inicializamos tres colas de procesos (no cuatro)
        self.queues = {1: [], 2: [], 3: []}
        self.time = 0  # El tiempo global, que simula el reloj del CPU

        # Esquemas de planificación: controlamos el quantum y la política de la cola final
        if scheme == 1:  # RR(1), RR(3), RR(4), SJF
            self.quantums = {1: 1, 2: 3, 3: 4}
            self.last_queue_policy = "SJF"
        elif scheme == 2:  # RR(2), RR(3), RR(4), STCF
            self.quantums = {1: 2, 2: 3, 3: 4}
            self.last_queue_policy = "STCF"
        elif scheme == 3:  # RR(3), RR(5), RR(6), RR(20)
            self.quantums = {1: 3, 2: 5, 3: 6}
            self.last_queue_policy = "RR"

    # Método para agregar un proceso a la cola correspondiente
    def add_process(self, process):
        self.queues[process.queue].append(process)

    # Método para realizar la planificación Round Robin (RR)
    def schedule_rr(self, queue, quantum):
        process_order = []  # Lista para almacenar el orden de ejecución de los procesos
        queue_list = self.queues[queue]  # Cola específica (por número de cola)

        while queue_list:
            process = queue_list.pop(0)  # Sacamos el primer proceso de la cola

            # Si el proceso llega después del tiempo actual, avanzamos el reloj
            if process.arrival_time > self.time:
                self.time = process.arrival_time

            # Establecer tiempo de respuesta la primera vez que el proceso es ejecutado
            if process.response_time == -1:
                process.response_time = self.time - process.arrival_time

            # Si el proceso puede completarse dentro del quantum
            if process.remaining_time <= quantum:
                self.time += process.remaining_time
                process.completion_time = self.time
                process.turnaround_time = process.completion_time - process.arrival_time
                process.wait_time = process.turnaround_time - process.burst_time
                process.remaining_time = 0
            else:
                # Si no, procesamos por el quantum y lo reincorporamos a la cola
                process.wait_time += quantum
                process.remaining_time -= quantum
                self.time += quantum
                queue_list.append(process)

            process_order.append(process.label)

        return process_order

    # Método para planificar con el algoritmo SJF (Shortest Job First)
    def schedule_sjf(self):
        process_order = []
        queue_list = sorted(self.queues[3], key=lambda p: (p.remaining_time, p.arrival_time))

        while queue_list:
            process = queue_list.pop(0)

            if process.arrival_time > self.time:
                self.time = process.arrival_time

            if process.response_time == -1:
                process.response_time = self.time - process.arrival_time

            # Ejecutar el proceso completamente
            self.time += process.remaining_time
            process.completion_time = self.time
            process.turnaround_time = process.completion_time - process.arrival_time
            process.wait_time = process.turnaround_time - process.burst_time
            process.remaining_time = 0
            process_order.append(process.label)

        return process_order

    # Método para planificar con el algoritmo STCF (Shortest Time to Completion First)
    def schedule_stcf(self):
        process_order = []
        queue_list = sorted(self.queues[3], key=lambda p: (p.remaining_time, p.arrival_time))

        while queue_list:
            process = queue_list.pop(0)

            if process.arrival_time > self.time:
                self.time = process.arrival_time

            if process.response_time == -1:
                process.response_time = self.time - process.arrival_time

            self.time += 1  # Se ejecuta un ciclo de CPU
            process.remaining_time -= 1

            if process.remaining_time > 0:
                queue_list.append(process)
            else:
                process.completion_time = self.time
                process.turnaround_time = process.completion_time - process.arrival_time
                process.wait_time = process.turnaround_time - process.burst_time

            process_order.append(process.label)
            queue_list.sort(key=lambda p: (p.remaining_time, p.arrival_time))

        return process_order

    # Método principal para coordinar las ejecuciones de las colas
    def schedule(self):
        rr1_order = self.schedule_rr(1, self.quantums[1])  # Cola 1 con RR(1)
        rr2_order = self.schedule_rr(2, self.quantums[2])  # Cola 2 con RR(3)
        rr3_order = self.schedule_rr(3, self.quantums[3])  # Cola 3 con RR(4)

        # Procesamos la cola final con la política configurada
        if self.last_queue_policy == "SJF":
            last_queue_order = self.schedule_sjf()  # SJF para la cola 3
        elif self.last_queue_policy == "STCF":
            last_queue_order = self.schedule_stcf()  # STCF para la cola 3
        else:
            last_queue_order = self.schedule_rr(3, self.quantums[3])  # RR para la cola 3

        return rr1_order + rr2_order + rr3_order + last_queue_order

# Función para leer los procesos desde un archivo
def read_processes_from_file(filename):
    processes = []
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('#'):
                continue
            parts = line.strip().split(';')
            label, burst_time, arrival_time, queue, priority = parts
            processes.append(Process(label, int(burst_time), int(arrival_time), int(queue), int(priority)))
    return processes

# Función para escribir los resultados en un archivo
def write_output_to_file(processes, filename):
    with open(filename, 'w') as file:
        file.write("# etiqueta; BT; AT; Q; Pr; WT; CT; RT; TAT\n")
        for process in processes:
            file.write(f"{process.label}; {process.burst_time}; {process.arrival_time}; {process.queue}; "
                       f"{process.priority}; {process.wait_time}; {process.completion_time}; "
                       f"{process.response_time}; {process.turnaround_time}\n")

        # Calcular promedios
        avg_wt = sum(p.wait_time for p in processes) / len(processes)
        avg_ct = sum(p.completion_time for p in processes) / len(processes)
        avg_rt = sum(p.response_time for p in processes) / len(processes)
        avg_tat = sum(p.turnaround_time for p in processes) / len(processes)
        file.write(f"\nWT={avg_wt}; CT={avg_ct}; RT={avg_rt}; TAT={avg_tat};\n")

# Función principal para ejecutar el programa
def main():
    input_files = ['mlfq001.txt', 'mlfq002.txt', 'mlfq003.txt']
    for input_file in input_files:
        scheduler = MLQScheduler(scheme=1)  # Cambiar esquema si es necesario
        try:
            processes = read_processes_from_file(input_file)
        except FileNotFoundError:
            print(f"Archivo no encontrado: {input_file}")
            continue

        for process in processes:
            scheduler.add_process(process)

        execution_order = scheduler.schedule()
        output_file = f'output_{input_file.split(".")[0]}.txt'
        write_output_to_file(processes, output_file)
        print(f"Archivo generado: {output_file}")
        print(f"Orden de ejecución: {execution_order}")

# Ejecutar el programa
if __name__ == "__main__":
    main()