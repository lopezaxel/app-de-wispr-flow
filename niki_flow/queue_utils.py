import queue


def drain_queue(q):
    """Ejecuta todas las acciones pendientes en una queue.Queue sin bloquear.

    Usado para despachar callbacks encolados desde hilos de fondo hacia el
    hilo de Tkinter dentro de un ciclo de `root.after(...)`.
    """
    try:
        while True:
            action = q.get_nowait()
            action()
    except queue.Empty:
        pass
