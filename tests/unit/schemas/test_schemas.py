from schemas.actions import ActionCode, card_index_from_code


def test_action_code_values():
    assert ActionCode.PLAY_CARD_0 == 0
    assert ActionCode.PLAY_CARD_1 == 1
    assert ActionCode.PLAY_CARD_2 == 2
    assert ActionCode.OFFER_TRUCO == 3
    assert ActionCode.ACCEPT_TRUCO == 4
    assert ActionCode.REJECT_TRUCO == 5


def test_card_index_from_code():
    assert card_index_from_code(ActionCode.PLAY_CARD_0) == 0
    assert card_index_from_code(ActionCode.PLAY_CARD_1) == 1
    assert card_index_from_code(ActionCode.PLAY_CARD_2) == 2
    assert card_index_from_code(ActionCode.OFFER_TRUCO) is None
    assert card_index_from_code(ActionCode.ACCEPT_TRUCO) is None
