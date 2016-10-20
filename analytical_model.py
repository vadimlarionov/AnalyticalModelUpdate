# -*- coding: utf-8 -*-

from math import pow, fabs

from conf import Conf


class AnalyticalModel:
    def __init__(self, num_ws, t_processing_ws, t_formation_req, num_processors, t_process_on_processor):
        self.num_ws = num_ws
        self.__t_processing_ws = t_processing_ws
        self.__t_formation_req = t_formation_req
        self.__num_processors = num_processors
        self.__t_process_on_processor = t_process_on_processor

        self.lambda_f1 = self.__lambda_f1()
        self.start_lambda = self.lambda_f1
        self.end_lambda = None

    def __lambda_f1(self):
        values = []
        for i in range(len(self.__num_processors)):
            values.append(self.__num_processors[i] / self.__t_process_on_processor[i])
        return Conf.k1 * min(values) * (self.num_ws - 1) / self.num_ws

    def t_stay_on_processor(self):
        value = self.lambda_f1 * self.__t_process_on_processor / self.__num_processors
        return self.__t_process_on_processor / (1 - pow(value, self.__num_processors))

    def t_cycle(self):
        return self.__t_processing_ws + self.__t_formation_req + self.t_stay_on_processor()

    def t_reaction(self):
        return self.t_cycle() - self.__t_formation_req

    def lambda_f(self):
        self.end_lambda = (self.num_ws - 1) / self.t_cycle()
        return self.end_lambda

    def load_ws(self):
        return (self.__t_processing_ws + self.__t_formation_req) / self.t_cycle()

    def load_user(self):
        return self.__t_formation_req / self.t_cycle()

    def __lambda(self):
        return self.num_ws / self.t_cycle()

    def load_processor(self):
        return self.__lambda() * self.__t_process_on_processor / self.__num_processors

    def modeling(self):
        iteration = 0
        current_delta = Conf.delta + 1
        while current_delta > Conf.delta and iteration < Conf.max_iterations:
            lambda_f = self.lambda_f()
            diff = self.lambda_f1 - lambda_f
            current_delta = fabs(diff) / lambda_f
            self.lambda_f1 -= diff / Conf.k2
            iteration += 1
        if iteration == Conf.max_iterations:
            print('Reached the maximum number of iterations=' + str(iteration))
        return iteration
