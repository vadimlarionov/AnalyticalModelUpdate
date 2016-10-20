# -*- coding: utf-8 -*-


class Utils:
    precision = 5

    @staticmethod
    def set_precision(text):
        try:
            value = int(text)
            if 0 < value <= 24:
                Utils.precision = value
        except ValueError as e:
            print("set_precision exception", e)
            pass

    @staticmethod
    def get_float(text, default):
        try:
            return float(text)
        except ValueError:
            return default

    @staticmethod
    def to_str(obj):
        if isinstance(obj, str):
            return obj
        return str(round(obj, Utils.precision))
