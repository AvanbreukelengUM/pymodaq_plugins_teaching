from pymodaq.extensions.data_mixer.model import DataMixerModel, np  # np will be used in method eval of the formula

from pymodaq_utils.math_utils import gauss1D, my_moment

from pymodaq_data.data import DataToExport, DataWithAxes, DataCalculated, DataDim
from pymodaq_gui.parameter import Parameter

from pymodaq.extensions.data_mixer.parser import (
    extract_data_names, split_formulae, replace_names_in_formula)

import laserbeamsize as lbs
from pymodaq_data.data import Q_


class DataMixerBeamProfiler(DataMixerModel):
    params = DataMixerModel.params+ [
        {'title': 'Plot x & y:', 'name': 'xy_opt', 'type': 'bool',
         'value': True},
        {'title': 'Plot d_major & d_minor:', 'name': 'd_opt', 'type': 'bool_push',
         'value': True},
        {'title': 'Plot theta:', 'name': 'theta_opt', 'type': 'led',
         'value': True},
    ]

    def process_dte(self, dte: DataToExport):
        dte_processed = DataToExport('computed')
        dwa = dte.get_data_from_name('BSCamera').data[0]
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

        return dte_processed

