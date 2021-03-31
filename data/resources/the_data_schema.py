the_schema = {
    'type': 'object',
    'properties': {
        'rank': {'type': 'number'},
        'sent': {
            'type': 'object',
            'patternProperties': {
                '^[a-z]+$': {
                    'additional': {'type': 'array'},
                    'times': {'type': 'number'}
            }
        }
    }
}}