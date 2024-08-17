from utils import time_expression_to_seconds

def test_single_unit_pytest():
    # test regular cases
    assert time_expression_to_seconds('1m') == 60
    assert time_expression_to_seconds('1h') == 60 * 60
    assert time_expression_to_seconds('1d') == 24 * 60 * 60
    assert time_expression_to_seconds('1d1m') == 24 * 60 * 60 + 60
    assert time_expression_to_seconds('1d1h1m') == 24 * 60 * 60 + 60 * 60 + 60

    # test reverse order
    assert time_expression_to_seconds('1m1h1d') == 24 * 60 * 60 + 60 * 60 + 60

    # test invalid cases
    assert time_expression_to_seconds('stelios') == 0
    assert time_expression_to_seconds('1') == 0
    assert time_expression_to_seconds('m') == 0