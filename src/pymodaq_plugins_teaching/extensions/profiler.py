from pymodaq_data import DataToExport, DataCalculated
from pymodaq_gui.plotting.data_viewers import Viewer0D
from qtpy import QtWidgets

from pymodaq_gui import utils as gutils
from pymodaq_utils.config import Config, ConfigError
from pymodaq_utils.logger import set_logger, get_module_name
from pymodaq_gui.utils.shared_ui import MenuToolbarNames

from pymodaq.extensions.utils import CustomExt
import laserbeamsize as lbs

import numpy as np

# todo: replace here *pymodaq_plugins_something* by your plugin package name
from pymodaq_plugins_teaching.utils import Config as PluginConfig

logger = set_logger(get_module_name(__file__))

main_config = Config()
plugin_config = PluginConfig()

# todo: modify this as you wish
EXTENSION_NAME = 'BeamProfiler'  # the name that will be displayed in the extension list in the
# dashboard
CLASS_NAME = 'CustomExtensionBeamProfiler'  # this should be the name of your class defined below



class CustomExtensionBeamProfiler(CustomExt):

    params = [
        {'title': 'BeamSizeOptions', 'name': 'options', 'type': 'group',
         'children': [
             {'title': 'XY', 'name': 'plot_xy', 'type': 'bool', 'value': True},
             {'title': 'DXDY', 'name': 'plot_dxdy', 'type': 'bool_push', 'value': True},
             {'title': 'Phi', 'name': 'plot_phi', 'type': 'led', 'value': True}, ]}
    ]

    def __init__(self, parent: gutils.DockArea, dashboard):
        super().__init__(parent, dashboard)

        # info: in an extension, if you want to interact with ControlModules you have to use the
        # object: self.modules_manager which is a ModulesManager instance from the dashboard
        self.daq_viewer = None
        self.setup_ui()


    def setup_docks_and_widgets(self):
        """Mandatory method to be subclassed to setup the docks layout

        Examples
        --------
        >>>self.docks['ADock'] = gutils.Dock('ADock name')
        >>>self.dockarea.addDock(self.docks['ADock'])
        >>>self.docks['AnotherDock'] = gutils.Dock('AnotherDock name')
        >>>self.dockarea.addDock(self.docks['AnotherDock'''], 'bottom', self.docks['ADock'])

        See Also
        --------
        pyqtgraph.dockarea.Dock
        """
        self.docks['Settings'] = gutils.Dock('Settings')
        self.docks['Viewer'] = gutils.Dock('Viewer')

        self.dockarea.addDock(self.docks['Settings'])
        self.dockarea.addDock(self.docks['Viewer'])

        self.docks['Settings'].addWidget(self.settings_tree)

        viewer_widget = QtWidgets.QWidget()
        self.viewer = Viewer0D(viewer_widget, 'Viewer')

        self.docks['Viewer'].addWidget(viewer_widget)


    def setup_actions(self):
        """Method where to create actions to be subclassed. Mandatory

        Examples
        --------
        >>> self.add_action('quit', 'Quit', 'close2', "Quit program")
        >>> self.add_action('grab', 'Grab', 'camera', "Grab from camera", checkable=True)
        >>> self.add_action('load', 'Load', 'Open', "Load target file (.h5, .png, .jpg) or data from camera"
            , checkable=False)
        >>> self.add_action('save', 'Save', 'SaveAs', "Save current data", checkable=False)

        See Also
        --------
        ActionManager.add_action
        """
        self.add_action('snap', 'Snap', 'looks_one',
                        tip='Snap current data', checkable=False,
                        toolbar=self.toolbar,
                        auto_toolbar=True)

    def connect_things(self):
        """Connect actions and/or other widgets signal to methods"""
        self.connect_action('snap', self.snap)

    def snap(self):
        if self.daq_viewer is None:
            self.daq_viewer = self.modules_manager.get_mod_from_name('Camera')
            self.daq_viewer.grab_done_signal.connect(self.plot)
        self.daq_viewer.snap()

    def plot(self, dte: DataToExport):
        dte_processed = DataToExport('computed')
        data_array_2D = dte.get_data_from_name('BSCamera')[0]
        # calculation
        x, y, d_major, d_minor, phi = lbs.beam_size(data_array_2D)

        dwa = DataCalculated('BeamSizeXY',
                       data=[np.atleast_1d(x),
                             np.atleast_1d(y), ],
                       labels=['X', 'Y'], )

        self.viewer.show_data(dwa)

    def setup_menus_and_toolbars(self, menubar: QtWidgets.QMenuBar = None):
        """Non mandatory method to be subclassed in order to create a menubar

        create menu for actions contained into the self._actions, for instance:

        Examples
        --------
        >>>file_menu = menubar.addMenu('File')
        >>>self.affect_to('load', file_menu)
        >>>self.affect_to('save', file_menu)

        >>>file_menu.addSeparator()
        >>>self.affect_to('quit', file_menu)

        See Also
        --------
        pymodaq.utils.managers.action_manager.ActionManager
        """
        # todo create and populate menu using actions defined above in self.setup_actions
        pass

    def value_changed(self, param):
        """ Actions to perform when one of the param's value in self.settings is changed from the
        user interface

        For instance:
        if param.name() == 'do_something':
            if param.value():
                print('Do something')
                self.settings.child('main_settings', 'something_done').setValue(False)

        Parameters
        ----------
        param: (Parameter) the parameter whose value just changed
        """
        pass


def main():
    import sys
    from pymodaq_gui.qt_utils import mkQApp
    from pymodaq.dashboard import create_load_dashboard
    from pymodaq.utils.gui_utils.loader_utils import create_extension

    app = mkQApp('Something')

    win, dashboard = create_load_dashboard()
    win.mainwindow.setVisible(False)

    win_ext, data_mixer = create_extension(dashboard, CustomExtensionBeamProfiler)
    win_ext.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
