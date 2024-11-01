from werkzeug.datastructures import ImmutableMultiDict


class Form:

    def __init__(self, data: ImmutableMultiDict):
        parsed_dict = {key: data.getlist(key) for key in data.keys()}
        self.points = parsed_dict['start_city'] + parsed_dict.get('stops', []) + parsed_dict['finish_city']

    def __str__(self):
        print(f'points: {self.points}')
