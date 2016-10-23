# -*- coding: utf-8 -*-

from math import pow, fabs

from conf import Conf


class AnalyticalModel:
    def __init__(self, user_input):
        self.num_ws = user_input.num_ws
        self.__t_processing_ws = user_input.t_processing_ws
        self.__t_formation_req = user_input.t_formation_req
        self.__num_processors_list = user_input.num_processors_list
        self.__t_process_on_processor_list = user_input.tpr_list
        self.num_stages = len(user_input.tpr_list)

        self.k1 = user_input.k1
        self.k2 = user_input.k2
        self.delta = user_input.delta

        self.lambda_f1 = self.__lambda_f1()
        self.start_lambda = self.lambda_f1
        self.end_lambda = None

    def __lambda_f1(self):
        values = []
        for i in range(len(self.__num_processors_list)):
            values.append(self.__num_processors_list[i] / self.__t_process_on_processor_list[i])
        return self.k1 * min(values) * (self.num_ws - 1) / self.num_ws

    def t_stay_on_processor(self, i):
        """
        Среднее время пребывания на i-ой стадии
        """
        value = self.lambda_f1 * self.__t_process_on_processor_list[i] / self.__num_processors_list[i]
        return self.__t_process_on_processor_list[i] / (1 - pow(value, self.__num_processors_list[i]))

    def num_requests_i(self, i):
        """
        Среднее количество заявок на i-ой стадии
        """
        return self.t_stay_on_processor(i) * self.__lambda()

    def t_cycle(self):
        sum_tpr = 0
        for i in range(len(self.__t_process_on_processor_list)):
            sum_tpr += self.t_stay_on_processor(i)
        return self.__t_processing_ws + self.__t_formation_req + sum_tpr

    def t_reaction(self):
        return self.t_cycle() - self.__t_formation_req

    def t_reaction_i(self, i):
        """
        Среднее время реакции на i-ой стадии
        :return:
        """
        # todo
        pass

    def lambda_f(self):
        self.end_lambda = (self.num_ws - 1) / self.t_cycle()
        return self.end_lambda

    def load_ws(self):
        return (self.__t_processing_ws + self.__t_formation_req) / self.t_cycle()

    def load_user(self):
        return self.__t_formation_req / self.t_cycle()

    def __lambda(self):
        return self.num_ws / self.t_cycle()

    def load_processor(self, i):
        """
        Загрузка i-го сервера
        """
        return self.__lambda() * self.__t_process_on_processor_list[i] / self.__num_processors_list[i]

    def modeling(self):
        """
        При моделировании просчитывает все выходные параметры
        :return: количество итераций
        """
        iteration = 0
        current_delta = self.delta + 1
        while current_delta > self.delta and iteration < Conf.max_iterations:
            lambda_f = self.lambda_f()
            diff = self.lambda_f1 - lambda_f
            current_delta = fabs(diff) / lambda_f
            self.lambda_f1 -= diff / self.k2
            iteration += 1
        if iteration == Conf.max_iterations:
            print('Reached the maximum number of iterations=' + str(iteration))
        return iteration
