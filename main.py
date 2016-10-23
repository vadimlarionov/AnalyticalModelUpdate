# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QMessageBox, QApplication
from PyQt5.QtGui import QFont

from analytical_model import AnalyticalModel
from conf import Conf
from parameters import InputParams, OutputParams
from ui_analyticalmodel import Ui_AnalyticalModel
from utils import Utils


class UserInput:
    def __init__(self, n, to, tp, c, tpr, k1, k2, delta):
        """
        :param n: Число рабочих станций сети
        :param to: Среднее t дообработки на РС
        :param tp: Среднее t формирования запроса на РС
        :param c: Список числа процессоров на каждой стадии последовательной обработки
        :param tpr: Список из средних значений времени обработки запроса на ЦП сервера
        """
        self.num_ws = int(n)
        self.t_processing_ws = float(to)
        self.t_formation_req = float(tp)
        self.num_processors_list = [int(x) for x in c]
        self.tpr_list = [float(x) for x in tpr]
        self.k1 = float(k1)
        self.k2 = float(k2)
        self.delta = float(delta)

        if any([self.num_ws < 0, self.t_processing_ws < 0, self.t_formation_req < 0, len(c) != len(tpr),
                *[x <= 0 for x in self.tpr_list], *[x <= 0 for x in self.num_processors_list], self.k1 < 0,
                self.k2 < 0, self.delta < 0]):
            raise ValueError


class AnalyticalModelView(QDialog, Ui_AnalyticalModel):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.number_stages = Conf.default_stages
        self.user_input = None

        self.input_params = InputParams()
        self.output_params = OutputParams()

        self.init_input_table()

        self.addVariantButton.clicked.connect(self.add_variant)
        self.deleteVariantButton.clicked.connect(self.delete_variant)
        self.calculateButton.clicked.connect(self.on_start_modeling)
        self.calculateButton.setDefault(True)
        self.on_start_modeling()

    def init_input_table(self):
        self.inputTableWidget.setColumnCount(1)
        self.inputTableWidget.setHorizontalHeaderItem(0, QTableWidgetItem(' '))
        for x in range(self.number_stages):
            self.add_variant()

        # font = QFont('Serif', 9)
        for row, param in self.input_params.items():
            self.inputTableWidget.insertRow(row)
            name_item = QTableWidgetItem(param.text)
            # name_item.setFont(font)
            self.inputTableWidget.setItem(row, 0, name_item)
            column = 1
            for value in param.values:
                item = QTableWidgetItem(str(value))
                # item.setFont(font)
                self.inputTableWidget.setItem(row, column, item)
                column += 1
        self.inputTableWidget.setColumnWidth(0, Conf.param_header_width)

    def add_variant(self):
        column = self.inputTableWidget.columnCount()
        if column <= Conf.max_variants:
            self.inputTableWidget.insertColumn(column)
            self.inputTableWidget.setHorizontalHeaderItem(column, QTableWidgetItem('Стадия ' + str(column)))
            self.number_stages = column

    def delete_variant(self):
        column = self.inputTableWidget.columnCount()
        if column > Conf.min_variants + 1:
            self.inputTableWidget.removeColumn(column - 1)
            self.number_stages = column - 2  # 1 - это название параметра

    # def get_input_data(self, param, variant):
    #     try:
    #         return float(self.inputTableWidget.item(param.row, variant).text())
    #     except ValueError as e:
    #         print('Value error: ' + str(e))
    #         self.create_error_msg().show()
    #     except AttributeError as e:
    #         print('Attribute error: ' + str(e))

    def get_input_list(self, row):
        data = []
        columns = self.inputTableWidget.columnCount()
        for column in range(1, columns):
            data.append(self.inputTableWidget.item(row, column).text())
        return data

    def delete_output_table(self):
        self.outputTableWidget.clear()
        self.outputTableWidget.setColumnCount(0)
        self.outputTableWidget.setRowCount(0)

    def create_output_table(self):
        self.delete_output_table()
        self.outputTableWidget.setColumnCount(self.number_stages + 1)
        self.outputTableWidget.setHorizontalHeaderItem(0, QTableWidgetItem(' '))
        for x in range(1, self.number_stages + 1):
            self.outputTableWidget.setHorizontalHeaderItem(x, QTableWidgetItem('В' + str(x)))

        for row, param in self.output_params.items():
            self.outputTableWidget.insertRow(row)
            self.outputTableWidget.setItem(row, 0, QTableWidgetItem(param.text))
        self.outputTableWidget.setColumnWidth(0, Conf.param_header_width)
        # self.outputTableWidget.resizeRowsToContents()

    def create_error_msg(self):
        msg = QMessageBox(self)
        msg.setText('<font size=6>Проверьте входные данные</font>')
        msg.setInformativeText(
            '<font size=5>Все вводимые параметры должны быть числовыми, некоторые - строго положительные. '
            'Используйте точку для разделения целой и дробной частей числа</font>')
        msg.setWindowTitle('Внимание')
        return msg

    def on_start_modeling(self):
        try:
            c = self.get_input_list(self.input_params.num_processors.row)
            tpr = self.get_input_list(self.input_params.t_process_on_processor.row)
            self.user_input = UserInput(self.nLineEdit.text(), self.toLineEdit.text(), self.tpLineEdit.text(), c, tpr,
                                        self.k1LineEdit.text(), self.k2LineEdit.text(), self.deltaLineEdit.text())
        except ValueError:
            self.create_error_msg().show()
            self.user_input = None
            return
        self.modeling()
        self.user_input = None

    def modeling(self):
        self.create_output_table()

        params = self.output_params
        model = AnalyticalModel(self.user_input)

        num_iterations = model.modeling()

        self.add_output_item(params.load_ws, 1, model.load_ws())
        self.add_output_item(params.load_user, 1, model.load_user())
        self.add_output_item(params.avg_ws, 1, model.load_ws() * model.num_ws)
        for i in range(model.num_stages):
            self.add_output_item(params.load_processor_i, i + 1, model.load_processor(i))
            self.add_output_item(params.t_stay_on_processor_i, i + 1, model.t_stay_on_processor(i))
            self.add_output_item(params.num_requests_i, i + 1, model.num_requests_i(i))
        self.add_output_item(params.t_cycle, 1, model.t_cycle())
        self.add_output_item(params.t_reaction, 1, model.t_reaction())
        self.add_output_item(params.start_lambda, 1, model.start_lambda)
        self.add_output_item(params.end_lambda, 1, model.end_lambda)
        self.add_output_item(params.num_iterations, 1, num_iterations)

        # for variant in range(1, self.number_variants + 1):
        #     try:
        #         model = self.create_model(variant)
        #         num_iterations = model.modeling()
        #         # self.add_output_item(params.load_ws, variant, model.load_ws())
        #         # self.add_output_item(params.load_user, variant, model.load_user())
        #         # self.add_output_item(params.avg_ws, variant, model.load_ws() * model.num_ws)
        #         # self.add_output_item(params.load_processor, variant, model.load_processor())
        #         # self.add_output_item(params.t_cycle, variant, model.t_cycle())
        #         # self.add_output_item(params.t_reaction, variant, model.t_reaction())
        #         # self.add_output_item(params.start_lambda, variant, model.start_lambda)
        #         # self.add_output_item(params.end_lambda, variant, model.end_lambda)
        #         self.add_output_item(params.num_iterations, variant, num_iterations)
        #     except TypeError as e:
        #         print('Type error: ' + str(e))

    def add_output_item(self, output_param, column, value):
        self.outputTableWidget.setItem(output_param.row, column, QTableWidgetItem(Utils.to_str(value)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AnalyticalModelView()
    window.setWindowFlags(window.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint |
                          QtCore.Qt.WindowMaximizeButtonHint)
    window.show()
    sys.exit(app.exec_())
