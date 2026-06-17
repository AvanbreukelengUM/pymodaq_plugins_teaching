import numpy as np
from pymodaq_data import DataCalculated

from pymodaq_utils.utils import ThreadCommand
from pymodaq_data.data import DataToExport, Axis
from pymodaq_gui.parameter import Parameter

from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.data import DataFromPlugins
import laserbeamsize as lbs


from pymodaq_plugins_mock.daq_viewer_plugins.plugins_2D.daq_2Dviewer_Mock import DAQ_2DViewer_Mock
from pymodaq_plugins_mockexamples.daq_viewer_plugins.plugins_2D.daq_2Dviewer_BSCamera import DAQ_2DViewer_BSCamera

class DAQ_2DViewer_BeamProfiler(DAQ_2DViewer_BSCamera):
    def grab_data(self, Naverage=1, **kwargs):
        data = self.average_data(Naverage)
        data_array_2D = data.get_data_from_name('BSCamera').data[0] # 0 because it is the first element of the list(data_array,data_array)
#         calculation
        x, y, d_major, d_minor, phi = lbs.beam_size(data_array_2D)
        dx = d_major
        dy = d_minor
        # data0D = DataToExport('Profiler',
        #                                   data=[DataCalculated(name='Extension', data=[np.atleast_1d(dx),np.atleast_1d(dy)],
        #                                                         dim='Data0D', labels=['dx','dy'])])
        data0D = DataCalculated(name='Extension', data=[np.atleast_1d(dx),np.atleast_1d(dy)],
                                                        labels=['d_major','d_minor'])
        data0D_pos = DataCalculated(name='Position', data=[np.atleast_1d(x),np.atleast_1d(y)],
                                                                labels=['x','y'])
        # super().grab_data(Naverage=Naverage, **kwargs)
        # self.dte_signal.emit(DataToExport('Profiler',
        #                                   data=[DataFromPlugins(name='Profile', data=data2D,
        #                                                         dim='Data2D', labels=['Intensity']),
        #                                         #
        #                                         # DataFromPlugins(name='Extension', data=data0D,
        #                                         #                 dim='Data0D', labels=['dx','dy']),
        #                                         ]))
        data.append(data0D)
        data.append(data0D_pos)
        self.dte_signal.emit(data)

if __name__ == '__main__':
    main(__file__)
