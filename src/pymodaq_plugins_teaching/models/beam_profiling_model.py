import numpy as np

from pymodaq.extensions.data_mixer.model import DataMixerModel, np  # np will be used in method eval of the formula

from pymodaq_utils.math_utils import gauss1D, my_moment

from pymodaq_data.data import DataToExport, DataWithAxes, DataCalculated, DataDim
from pymodaq_gui.parameter import Parameter

from pymodaq.extensions.data_mixer.parser import (
    extract_data_names, split_formulae, replace_names_in_formula)
import laserbeamsize as lbs
from pymodaq_data.data import Q_


# def gaussian_fit(x, amp, x0, dx, offset):
#     dx = np.abs(dx)
#     return amp * gauss1D(x, x0, dx) + offset


class DataMixerBeamProfiler(DataMixerModel):
    params = DataMixerModel.params+ [
        # {'title': 'Get Data:', 'name': 'get_data', 'type': 'bool_push', 'value': False,
        #  'label': 'Get Data'},
        # {'title': 'Data2D:', 'name': 'data2D', 'type': 'itemselect',
        #  'value': dict(all_items=[], selected=[])},
        {'title': 'Plot x & y:', 'name': 'xy_opt', 'type': 'bool',
         'value': True},
        {'title': 'Plot d_major & d_minor:', 'name': 'd_opt', 'type': 'bool_push',
         'value': True},
        {'title': 'Plot theta:', 'name': 'theta_opt', 'type': 'led',
         'value': True},
    ]
    #
    # def ini_model(self):
    #     self.show_data_list()
    #
    # def show_data_list(self):
    #     dte = self.modules_manager.get_det_data_list()
    #     data_list1D = dte.get_full_names('data2D')
    #     self.settings.child('data2D').setValue(dict(all_items=data_list2D, selected=[]))
    #
    # def update_settings(self, param: Parameter):
    #     if param.name() == 'get_data':
    #         self.show_data_list()

    def process_dte(self, dte: DataToExport):
        dte_processed = DataToExport('computed')
        # if len(self.settings['data2D']['selected']) != 0:
        dwa = dte.get_data_from_name('BSCamera').data[0]
        # dwa_fit = dwa.fit(gaussian_fit, self.get_guess(dwa), data_index=0)
        # dwa.append(dwa_fit)
        # dte_processed.append(dwa)
        x, y, d_major, d_minor, phi = lbs.beam_size(dwa)
        phi_q = Q_(phi, units='rad')
        dx = d_major
        dy = d_minor
        if self.settings.child('d_opt').value():
            data0D = DataCalculated(name='Extension', data=[np.atleast_1d(dx), np.atleast_1d(dy)],
                                    labels=['d_major', 'd_minor'], units='pixels')
            dte_processed.append(data0D)

        if self.settings['xy_opt']:
            data0D = DataCalculated(name='Position', data=[np.atleast_1d(x), np.atleast_1d(y)],
                                    labels=['x', 'y'], units='pixels')
            dte_processed.append(data0D)

        if self.settings.child('theta_opt').value():
            data0D = DataCalculated(name='Angle', data=[np.atleast_1d(phi_q.m_as('degree'))],
                                    labels=['theta'], units='degree')
            dte_processed.append(data0D)

            # dte_processed.append(
            #     DataCalculated('Coeffs',
            #                    data=[np.atleast_1d(coeff) for coeff in dwa_fit.fit_coeffs[0]],
            #                    labels=['amp', 'x0', 'dx', 'offset']))

        return dte_processed

    # @staticmethod
    # def get_guess(dwa):
    #     offset = np.min(dwa).value()
    #     dwa.create_missing_axes()
    #     moments = my_moment(dwa.axes[0].get_data(), dwa.data[0])
    #     amp = (np.max(dwa) - np.min(dwa)).value()
    #     x0 = float(moments[0])
    #     dx = float(moments[1])
    #
    #     return amp, x0, dx, offset


