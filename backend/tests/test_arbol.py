import pytest
from servicios.arbol_orden import calcular_precio_nodo

@pytest.mark.parametrize(
        "precio_base,cantidad, esperado",
        [
            (1000,1,1000),
            (1000,3,3000),
            (2500,0,0),
        ]
)
def test_platillo_simple(precio_base,cantidad,esperado):
    nodo= {
        "PrecioBaseHistorico": precio_base,
        "Cantidad": cantidad,
        "Modificadores": [],
        "Contiene": []
    }
    assert calcular_precio_nodo(nodo) == esperado

def test_platillo_con_modificadores_cantidad_tres():
    nodo={
        "PrecioBaseHistorico": 2500,
        "Cantidad": 3,
        "Modificadores": [
            {"PrecioExtraHistorico": 800,"Cantidad": 1},
            {"PrecioExtraHistorico": 1000,"Cantidad": 1}
        ],
        "Contiene": []
    }
    assert calcular_precio_nodo(nodo) == 12900

def test_platillo_con_un_hijo():
    nodo={
        "PrecioBaseHistorico": 2500,
        "Cantidad": 3,
        "Modificadores":[],
        "Contiene": [
            {
                "PrecioBaseHistorico": 1000,
                "Cantidad": 2,
                "Modificadores":[],
                "Contiene": []
            }
        ]
    }
    assert calcular_precio_nodo(nodo) == 13500

def test_platillo_con_un_hijo_con_modificador():
    nodo={
        "PrecioBaseHistorico": 2500,
        "Cantidad": 3,
        "Modificadores":[],
        "Contiene": [
            {
                "PrecioBaseHistorico": 1000,
                "Cantidad": 2,
                "Modificadores":[
                    {"PrecioExtraHistorico": 800,"Cantidad": 1}
                ],
                "Contiene": []
            }
        ]
    }
    assert calcular_precio_nodo(nodo) == 18300

def test_arbol_tres_niveles_con_modificadores():
    nodo = {
        "PrecioBaseHistorico": 2500,
                "Cantidad": 3,
                "Modificadores": [
                    {"PrecioExtraHistorico": 800,"Cantidad": 1},
                    {"PrecioExtraHistorico": 1000,"Cantidad": 1}
                ],
                "Contiene": [
                    {
                        "PrecioBaseHistorico": 1000,
                                        "Cantidad": 4,
                                        "Modificadores":[{"PrecioExtraHistorico":1000,"Cantidad":1}],
                                        "Contiene": [
                                            {
                                                "PrecioBaseHistorico": 1500,
                                                                "Cantidad": 2,
                                                                "Modificadores":[
                                                                    {"PrecioExtraHistorico": 1800,"Cantidad": 1},
                                                                    {"PrecioExtraHistorico": 1500,"Cantidad": 1}
                                                                ],
                                                                "Contiene": []
                                            }
                                        ]
                    }
                ]
            }
    assert calcular_precio_nodo(nodo) == 152100