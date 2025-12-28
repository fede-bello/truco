from models.card import Card


def test_card_initialization():
    card = Card(1, "espadas")
    assert card.number == 1
    assert card.suit == "espadas"
    assert str(card) == "1 of espadas"
    assert repr(card) == "1 of espadas"


def test_card_hashing():
    card1 = Card(1, "espadas")
    card2 = Card(1, "espadas")
    card3 = Card(1, "basto")
    assert hash(card1) == hash(card2)
    assert hash(card1) != hash(card3)


def test_is_mata():
    assert Card(1, "espadas")._is_mata() is True
    assert Card(1, "basto")._is_mata() is True
    assert Card(7, "espadas")._is_mata() is True
    assert Card(7, "oro")._is_mata() is True
    assert Card(1, "oro")._is_mata() is False
    assert Card(3, "espadas")._is_mata() is False


def test_is_pieza():
    muestra = Card(10, "oro")
    # Piezas are 2, 4, 5, 11, 10 of muestra suit
    assert Card(2, "oro")._is_pieza(muestra) is True
    assert Card(4, "oro")._is_pieza(muestra) is True
    assert Card(5, "oro")._is_pieza(muestra) is True
    assert Card(11, "oro")._is_pieza(muestra) is True
    assert Card(10, "oro")._is_pieza(muestra) is True

    assert Card(2, "espadas")._is_pieza(muestra) is False
    assert Card(3, "oro")._is_pieza(muestra) is False


def test_is_pieza_rey_replacement():
    # If muestra is a pieza (e.g. 2 of ORO), then 12 of ORO becomes a pieza
    muestra = Card(2, "oro")
    assert Card(12, "oro")._is_pieza(muestra) is True
    assert Card(2, "oro")._is_pieza(muestra) is True


def test_get_card_value_normal():
    muestra = Card(10, "copa")
    # Order: 4, 5, 6, 7, 10, 11, 12, 1, 2, 3
    assert Card(4, "oro").get_card_value(muestra) == 0
    assert Card(3, "oro").get_card_value(muestra) == 9


def test_get_card_value_matas():
    muestra = Card(10, "copa")
    # Matas: 7 ORO (10), 7 ESP (11), 1 BAS (12), 1 ESP (13)
    assert Card(7, "oro").get_card_value(muestra) == 10
    assert Card(7, "espadas").get_card_value(muestra) == 11
    assert Card(1, "basto").get_card_value(muestra) == 12
    assert Card(1, "espadas").get_card_value(muestra) == 13


def test_get_card_value_piezas():
    muestra = Card(10, "oro")
    # Piezas values: 10 (14), 11 (15), 5 (16), 4 (17), 2 (18)
    assert Card(10, "oro").get_card_value(muestra) == 14
    assert Card(11, "oro").get_card_value(muestra) == 15
    assert Card(5, "oro").get_card_value(muestra) == 16
    assert Card(4, "oro").get_card_value(muestra) == 17
    assert Card(2, "oro").get_card_value(muestra) == 18


def test_is_greater_than():
    muestra = Card(10, "oro")
    c_2_oro = Card(2, "oro")  # Pieza (18)
    c_1_esp = Card(1, "espadas")  # Mata (13)
    c_3_esp = Card(3, "espadas")  # Normal (9)

    assert c_2_oro.is_greater_than(c_1_esp, muestra) is True
    assert c_1_esp.is_greater_than(c_3_esp, muestra) is True
    assert c_3_esp.is_greater_than(c_2_oro, muestra) is False
