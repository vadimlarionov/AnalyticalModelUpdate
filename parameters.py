# -*- coding: utf-8 -*-


class Param:
    def __init__(self, row, text, values=None):
        if values is None:
            values = []
        self.row = row
        self.text = text
        self.values = values

    def __repr__(self):
        return 'Param: {' + 'row: {}, text: {}, values: {}'.format(self.row, self.text, self.values) + '}'


def check_params(params):
    current_row = 0
    for key in params.keys():
        if key != current_row:
            msg = 'actual=' + str(key) + ' , expected=' + str(current_row)
            raise ValueError(msg)
        current_row += 1


def add_attribute(obj, attribute_name, param_text, values=None):
    param = Param(obj.count_attributes, param_text, values)
    obj.count_attributes += 1
    setattr(obj, attribute_name, param)
    obj[param.row] = param


class InputParams(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.count_attributes = 0

        add_attribute(self, 'num_ws', 'Количество рабочих станций', [10, 10, 10, 10, 10])

        add_attribute(self, 't_processing_ws', 'Среднее время дообработки запроса на РС', [0, 0, 0, 0, 50])
        add_attribute(self, 't_formation_req', 'Среднее время формирования запроса на РС', [100, 200, 100, 100, 50])

        add_attribute(self, 'num_processors', 'Количество процессоров на i-ой стадии обработки', [1, 1, 1, 1, 1])
        add_attribute(self, 't_process_on_processor', 'Среднее время обработки запроса на процессоре',
                      [10, 10, 10, 10, 10])
        add_attribute(self, 'num_disks', 'Количество дисков', [1, 1, 2, 1, 2])
        sorted(self)
        check_params(self)


class OutputParams(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.count_attributes = 0

        add_attribute(self, 'load_ws', 'Загрузка рабочей станции')
        add_attribute(self, 'load_user', 'Загрузка пользователя')
        add_attribute(self, 'avg_ws', 'Среднее количество работающих РС')
        add_attribute(self, 'load_channel', 'Загрузка канала')
        add_attribute(self, 'load_processor', 'Загрузка процессора')
        add_attribute(self, 'load_disk', 'Загрузка i-го диска')
        add_attribute(self, 't_cycle', 'Среднее время цикла системы')
        add_attribute(self, 't_reaction', 'Среднее время реакции системы')
        add_attribute(self, 'start_lambda', 'Начальная интенсивность фонового потока')
        add_attribute(self, 'end_lambda', 'Конечная интенсивность фонового потока')
        add_attribute(self, 'num_iterations', 'Количество итераций')

        sorted(self)
        check_params(self)

    def __add_attribute(self, attribute_name, param_text):
        param = Param(self.count_attributes, param_text)
        self.count_attributes += 1
        setattr(self, attribute_name, param)
        self[param.row] = param
