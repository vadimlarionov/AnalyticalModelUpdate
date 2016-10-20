# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QMessageBox, QApplication

from analytical_model import AnalyticalModel
from conf import Conf
from parameters import InputParams, OutputParams
from ui_analyticalmodel import Ui_AnalyticalModel
from utils import Utils


class AnalyticalModelView(QDialog, Ui_AnalyticalModel):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.number_variants = Conf.default_variants
        self.input_params = InputParams()
        self.output_params = OutputParams()

        self.init_input_table()
        self.addVariantButton.clicked.connect(self.add_variant)
        self.deleteVariantButton.clicked.connect(self.delete_variant)
        self.calculateButton.clicked.connect(self.modeling)
        self.calculateButton.setDefault(True)
        self.modeling()

    def init_input_table(self):
        self.inputTableWidget.setColumnCount(1)
        self.inputTableWidget.setHorizontalHeaderItem(0, QTableWidgetItem(' '))
        for x in range(self.number_variants):
            self.add_variant()

        for row, param in self.input_params.items():
            self.inputTableWidget.insertRow(row)
            self.inputTableWidget.setItem(row, 0, QTableWidgetItem(param.text))
            column = 1
            for value in param.values:
                item = QTableWidgetItem(str(value))
                item.setFlags(QtCore.Qt.ItemIsEditable)
                self.inputTableWidget.setItem(row, column, QTableWidgetItem(str(value)))
                column += 1
        self.inputTableWidget.setColumnWidth(0, Conf.param_header_width)

    def add_variant(self):
        column = self.inputTableWidget.columnCount()
        if column <= Conf.max_variants:
            self.inputTableWidget.insertColumn(column)
            self.inputTableWidget.setHorizontalHeaderItem(column, QTableWidgetItem('В' + str(column)))
            self.number_variants = column

    def delete_variant(self):
        column = self.inputTableWidget.columnCount()
        if column > Conf.min_variants + 1:
            self.inputTableWidget.removeColumn(column - 1)
            self.number_variants = column - 2  # 1 - это название параметра

    def get_input_data(self, param, variant):
        try:
            return float(self.inputTableWidget.item(param.row, variant).text())
        except ValueError as e:
            print('Value error: ' + str(e))
            self.create_error_msg().show()
        except AttributeError as e:
            print('Attribute error: ' + str(e))

    def delete_output_table(self):
        self.outputTableWidget.clear()
        self.outputTableWidget.setColumnCount(0)
        self.outputTableWidget.setRowCount(0)

    def create_output_table(self):
        self.delete_output_table()
        self.outputTableWidget.setColumnCount(self.number_variants + 1)
        self.outputTableWidget.setHorizontalHeaderItem(0, QTableWidgetItem(' '))
        for x in range(1, self.number_variants + 1):
            self.outputTableWidget.setHorizontalHeaderItem(x, QTableWidgetItem('В' + str(x)))

        for row, param in self.output_params.items():
            self.outputTableWidget.insertRow(row)
            self.outputTableWidget.setItem(row, 0, QTableWidgetItem(param.text))
        self.outputTableWidget.setColumnWidth(0, Conf.param_header_width)

    def create_model(self, variant):
        params = self.input_params
        num_ws = self.get_input_data(params.num_ws, variant)
        t_processing_ws = self.get_input_data(params.t_processing_ws, variant)
        t_formation_req = self.get_input_data(params.t_formation_req, variant)
        t_transfer_forward = self.get_input_data(params.t_transfer_forward, variant)
        t_transfer_back = self.get_input_data(params.t_transfer_back, variant)
        num_processors = self.get_input_data(params.num_processors, variant)
        t_process_on_processor = self.get_input_data(params.t_process_on_processor, variant)
        num_disks = self.get_input_data(params.num_disks, variant)
        t_process_on_disk = self.get_input_data(params.t_process_on_disk, variant)
        p_access_to_disk = self.get_input_data(params.p_access_to_disk, variant)
        return AnalyticalModel(num_ws, t_processing_ws, t_formation_req, t_transfer_forward, t_transfer_back,
                               num_processors, t_process_on_processor, num_disks, t_process_on_disk, p_access_to_disk)

    def create_error_msg(self):
        msg = QMessageBox(self)
        msg.setText('<font size=6>Проверьте входные данные</font>')
        msg.setInformativeText('<font size=5>Все вводимые параметры должны быть числовыми. '
                               'Используйте точку для разделения целой и дробной частей числа</font>')
        msg.setWindowTitle('Внимание')
        return msg

    def modeling(self):
        return

        Conf.k1 = Utils.get_float(self.k1LineEdit.text(), Conf.k1)
        Conf.k2 = Utils.get_float(self.k2LineEdit.text(), Conf.k2)
        Conf.delta = Utils.get_float(self.deltaLineEdit.text(), Conf.delta)

        self.create_output_table()
        params = self.output_params
        for variant in range(1, self.number_variants + 1):
            try:
                model = self.create_model(variant)
                num_iterations = model.modeling()
                self.add_output_item(params.load_ws, variant, model.load_ws())
                self.add_output_item(params.load_user, variant, model.load_user())
                self.add_output_item(params.avg_ws, variant, model.load_ws() * model.num_ws)
                self.add_output_item(params.load_channel, variant, model.load_channel())
                self.add_output_item(params.load_processor, variant, model.load_processor())
                self.add_output_item(params.load_disk, variant, model.load_disk())
                self.add_output_item(params.t_cycle, variant, model.t_cycle())
                self.add_output_item(params.t_reaction, variant, model.t_reaction())
                self.add_output_item(params.start_lambda, variant, model.start_lambda)
                self.add_output_item(params.end_lambda, variant, model.end_lambda)
                self.add_output_item(params.num_iterations, variant, num_iterations)
            except TypeError as e:
                print('Type error: ' + str(e))

    def add_output_item(self, output_param, variant, value):
        self.outputTableWidget.setItem(output_param.row, variant, QTableWidgetItem(Utils.to_str(value)))
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AnalyticalModelView()
    window.setWindowFlags(window.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint |
                          QtCore.Qt.WindowMaximizeButtonHint)
    window.show()
    sys.exit(app.exec_())
