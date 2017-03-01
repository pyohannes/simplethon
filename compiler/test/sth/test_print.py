from helper import assert_compiled_output


def test_hello_world():
    assert_compiled_output(
"""
def main(args) [str] -> int :
    print("Hello World")
      
    return 0
""",
"""Hello World
""", 0)
