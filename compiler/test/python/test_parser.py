def assert_parser(input, ret):
    from sth.parser import parse_string

    ret = [] 

    module = parse_string(input)

    assert module.sthcode == input


def test_helloworld():
    assert_parser(
"""def main(args):
    "[str] -> cint"
    print("Hello World!")
    return 0
""", 0)
