import pytest
from pydantic import ValidationError
from schemas.orden import Ticket, Pedido, OrdenRespuesta, centavos_a_pesos, Orden

def test_ticket_rechaza_nombre_platillo_vacio():
    with pytest.raises(ValidationError) as excinfo:
        Ticket(Cantidad = 1, NombrePlatillo="")

    errores = excinfo.value.errors()
    assert len(errores) == 1
    assert errores[0]["loc"] == ("NombrePlatillo",)
    assert errores[0]["type"] == "string_too_short"

def test_pedido_rechaza_campo_obsoleto():
    with pytest.raises(ValidationError) as excinfo:
       Pedido(
           Platillo= 1,
           Cantidad= 1,
           Nota = "Pasa en 15 min"
           )

    errores = excinfo.value.errors()
    assert len(errores) == 1
    assert errores[0]["loc"] == ("Nota",)
    assert errores[0]["type"] == "extra_forbidden"

@pytest.mark.parametrize(
        "centavos, esperado",
        [
            (2500, "25.00"),
            (1005, "10.05"),
            (5, "0.05"),
            (99, "0.99"),
            (0, "0.00"),
        ]
)
def test_centavos_a_pesos(centavos,esperado):
    assert centavos_a_pesos(centavos) == esperado

def test_orden_respuesta_serializa_total_a_texto_json():
    respuesta=OrdenRespuesta(
        Message="Orden creada",
        OrdenID = 1,
        Total = 12200)
    
    assert respuesta.model_dump()["Total"] == 12200
    assert respuesta.model_dump(mode="json")["Total"] == "122.00"

@pytest.mark.parametrize("total_invalido", [0,-100])
def test_orden_respuesta_rechaza_total_cero_o_negativo(total_invalido):
    with pytest.raises(ValidationError) as excinfo:
        OrdenRespuesta(
            Message="Orden creada",
            OrdenID=1,
            Total = total_invalido
            )

    errores = excinfo.value.errors()
    assert len(errores) == 1
    assert errores[0]["loc"] == ("Total",)
    assert errores[0]["type"] == "greater_than"

def test_orden_rechaza_platillos_vacios():
    with pytest.raises(ValidationError) as excinfo:
        Orden(NombreCliente= "Bob", Platillos=[])

    errores = excinfo.value.errors()
    assert len(errores) == 1
    assert errores[0]["loc"] == ("Platillos",)
    assert errores[0]["type"] == "too_short"

@pytest.mark.parametrize("cantidad", [0,-1])
def test_pedido_rechaza_cantidad_menor_que_uno(cantidad):
    with pytest.raises(ValidationError) as excinfo:
        Pedido(Platillo=1,Cantidad=cantidad)

    errores = excinfo.value.errors()
    assert len(errores) == 1
    assert errores[0]["loc"] == ("Cantidad",)
    assert errores[0]["type"] == "greater_than_equal"

def test_pedido_hijo_rechaza_cantidad_invalida():
    with pytest.raises(ValidationError) as excinfo:
        Pedido(
            Platillo=1,
            Cantidad=1,
            Contiene=[
                {"Platillo": 2, "Cantidad": 0 }
            ]
        )

    errores = excinfo.value.errors()
    assert len(errores) == 1
    assert errores[0]["loc"] == ("Contiene", 0, "Cantidad")
    assert errores[0]["type"] == "greater_than_equal"

@pytest.mark.parametrize(
    "centavos, esperado",
    [
        (-5, "-0.05"),
        (-105, "-1.05"),
    ]
)
def test_centavos_a_pesos_negativos(centavos,esperado):
    assert centavos_a_pesos(centavos) == esperado