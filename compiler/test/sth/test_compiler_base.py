from helper import assert_compiled_output


def test_hello_world():
    assert_compiled_output(
"""
def main(args: List[str]) -> int :
    return 0
""",
"", 0)
