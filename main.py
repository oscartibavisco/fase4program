from modelo.cliente import Cliente
from modelo.servicio import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from gestores.gestor_sistema import GestorSistemaFJ
from excepciones.errores import ErrorSistemaFJ


def correr_simulacion_base(app: GestorSistemaFJ) -> None:
    # Ejecuta más de 10 operaciones válidas e inválidas para validar estabilidad y logs.
    app.logger.info("--- Inicio simulación base Software FJ ---")

    app.correr_op(1, "Cliente válido CLI-01", lambda: app.agregar_cliente(Cliente("CLI-01", "Laura Gómez", "laura@fj.co")))
    app.correr_op(2, "Cliente inválido CLI-02", lambda: app.agregar_cliente(Cliente("CLI-02", "Carlos Ruiz", "sin-correo")))
    app.correr_op(3, "Cliente faltante (None)", lambda: app.agregar_cliente(None))
    app.correr_op(4, "Cliente válido CLI-03", lambda: app.agregar_cliente(Cliente("CLI-03", "Andrés Pardo", "andres@fj.co")))

    def cargar_servicios() -> str:
        app.agregar_servicio(ReservaSala("SALA-1", "Sala Reuniones", 80000, capacidad=10))
        app.agregar_servicio(AlquilerEquipo("EQ-1", "Portátil Pro", 25000, stock=5))
        app.agregar_servicio(AsesoriaEspecializada("ASE-1", "Soporte Cloud", 120000, seniority="Senior"))
        return "Servicios registrados"

    app.correr_op(5, "Crear servicios", cargar_servicios)
    app.correr_op(6, "Servicio tarifa negativa", lambda: app.agregar_servicio(ReservaSala("SALA-BAD", "Sala Error", -10000, capacidad=6)))

    def crear_y_confirmar_res1() -> str:
        app.crear_reserva("RES-1", "CLI-01", "SALA-1", 3, descuento=10.0, asistentes=7)
        return app.buscar_reserva("RES-1").confirmar()

    app.correr_op(7, "Crear y confirmar RES-1", crear_y_confirmar_res1)
    app.correr_op(8, "Procesar RES-1", lambda: app.buscar_reserva("RES-1").procesar())
    app.correr_op(9, "Exceso capacidad en sala", lambda: app.crear_reserva("RES-2", "CLI-03", "SALA-1", 2, asistentes=20))
    app.correr_op(10, "Alquiler equipo RES-3", lambda: app.crear_reserva("RES-3", "CLI-03", "EQ-1", 4, cantidad=2))

    def desactivar_y_fallar() -> str:
        servicio = app.buscar_servicio("ASE-1")
        servicio.disponible = False
        return app.crear_reserva("RES-4", "CLI-01", "ASE-1", 2)

    app.correr_op(11, "Servicio no disponible", desactivar_y_fallar)
    app.correr_op(12, "Cancelar RES-1 ya procesada", lambda: app.buscar_reserva("RES-1").cancelar("Intento tardío"))

    def cancelar_y_cotizar() -> str:
        msg = app.buscar_reserva("RES-3").cancelar("Reprogramación")
        cotizacion = app.buscar_reserva("RES-3").servicio.calcular_costo(2, cantidad=1, ajuste_tarifa="10%")
        return f"{msg} | Cotización 2h con +10% tarifa: ${cotizacion:,.2f}"

    app.correr_op(13, "Cancelar RES-3 y cotizar con ajuste", cancelar_y_cotizar)
    app.logger.info("--- Fin simulación Software FJ ---")


def menu_interactivo(app: GestorSistemaFJ) -> None:
    contador_op = 14
    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Registrar cliente (ID, nombre y correo)")
        print("2. Crear reserva (IDs servicios: SALA-1, EQ-1, ASE-1 | ID reserva, ID cliente, ID servicio, horas)")
        print("3. Confirmar / Cancelar / Procesar reserva")
        print("4. Ver clientes, servicios y reservas en memoria")
        print("5. Salir")

        opcion = input("Elige una opción (1-5): ").strip()

        if opcion == "1":
            id_cli = input("ID cliente: ").strip()
            nom_cli = input("Nombre cliente: ").strip()
            cor_cli = input("Correo cliente: ").strip()
            app.correr_op(
                contador_op,
                "Registro interactivo de cliente",
                lambda: app.agregar_cliente(Cliente(id_cli, nom_cli, cor_cli)),
            )
            contador_op += 1
        elif opcion == "2":
            id_res = input("ID reserva: ").strip()
            id_cli = input("ID cliente: ").strip()
            id_srv = input("ID servicio: ").strip()
            txt_horas = input("Horas: ").strip()

            def registrar_reserva() -> str:
                try:
                    horas = int(txt_horas)
                except ValueError as exc:
                    raise ErrorSistemaFJ("Las horas deben ser un número entero.") from exc
                return app.crear_reserva(id_res, id_cli, id_srv, horas)

            app.correr_op(contador_op, "Creación interactiva de reserva", registrar_reserva)
            contador_op += 1
        elif opcion == "3":
            id_res = input("ID reserva: ").strip()
            accion = input("Acción (confirmar / cancelar / procesar): ").strip().lower()

            def ejecutar_accion() -> str:
                reserva = app.buscar_reserva(id_res)
                if accion == "confirmar":
                    return reserva.confirmar()
                if accion == "cancelar":
                    motivo = input("Motivo de cancelación: ").strip()
                    return reserva.cancelar(motivo or "Cancelada por usuario")
                if accion == "procesar":
                    return reserva.procesar()
                raise ErrorSistemaFJ("Acción no válida (usa confirmar, cancelar o procesar).")

            app.correr_op(contador_op, f"Acción {accion} en reserva", ejecutar_accion)
            contador_op += 1
        elif opcion == "4":
            app.listar_resumen()
        elif opcion == "5":
            print("Saliendo del sistema Software FJ...")
            break
        else:
            print("Opción no válida. Elige entre 1 y 5.")


if __name__ == "__main__":
    sistema = GestorSistemaFJ()
    correr_simulacion_base(sistema)
    menu_interactivo(sistema)