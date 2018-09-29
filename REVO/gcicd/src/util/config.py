from util.parser import parse_json

def parse_config(config={}):
    try:
        parsed_config = parse_json(config)
        assert parsed_config
        return parsed_config
    except AssertionError:
        return {}
