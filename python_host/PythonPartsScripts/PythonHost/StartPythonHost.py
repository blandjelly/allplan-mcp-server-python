from __future__ import annotations
import sys
import os
import clr
from pathlib import Path

from typing import List

import NemAll_Python_IFW_Input as AllplanIFW

from .PythonHostHandler import RequestHandler
from .transport import BridgeServer
from BuildingElement import BuildingElement
from BuildingElementComposite import BuildingElementComposite
from BuildingElementControlProperties import BuildingElementControlProperties
from BuildingElementPaletteService import BuildingElementPaletteService
from StringTableService import StringTableService
from TypeCollections.ModificationElementList import ModificationElementList

from System import Object, Func, TimeSpan
from System.Windows import Application
from System.Windows.Threading import DispatcherTimer

os.environ["LIBRARY_ROOTS"] = ";".join(sys.path)


print("Load StartPythonHost.py")

def check_allplan_version(_build_ele: BuildingElement,
                          _version  : str):
    """ Check the current Allplan version

    Args:
        _build_ele: the building element.
        _version:   the current Allplan version

    Returns:
        True/False if version is supported by this script
    """

    return True

def invoke_in_ui_thread(func):
    """ Executes provided function on UI thread

    Args:
        func: Function to execute

    Returns:
        The same object that func returns
    """

    return Application.Current.Dispatcher.Invoke(Func[Object](func))


# entry point

def create_interactor(coord_input             : AllplanIFW.CoordinateInput,
                      pyp_path                : str,
                      global_str_table_service: StringTableService,
                      build_ele_list          : List[BuildingElement],
                      build_ele_composite     : BuildingElementComposite,
                      control_props_list      : List[BuildingElementControlProperties],
                      modification_ele_list   : ModificationElementList) -> PythonHostInteractor:
    """ Create the interactor

    Args:
        coord_input:              API object for the coordinate input, element selection, ... in the Allplan view
        pyp_path:                 path of the pyp file
        global_str_table_service: global string table service
        build_ele_list:           list with the building elements
        build_ele_composite:      building element composite with the building element constraints
        control_props_list:       control properties list
        modification_ele_list:    list with the UUIDs of the modified elements

    Returns:
          Created interactor object
    """

    return PythonHostInteractor(coord_input,
                                pyp_path,
                                global_str_table_service,
                                build_ele_list,
                                build_ele_composite,
                                control_props_list,
                                modification_ele_list)


class PythonHostInteractor():
    """ Definition of class PythonHostInteractor
    """

    def __init__(self,
                 coord_input             : AllplanIFW.CoordinateInput,
                 pyp_path                : str,
                 global_str_table_service: StringTableService,
                 build_ele_list          : List[BuildingElement],
                 build_ele_composite     : BuildingElementComposite,
                 control_props_list      : List[BuildingElementControlProperties],
                 modification_ele_list   : ModificationElementList):
        """ Create the interactor

        Args:
            coord_input:              API object for the coordinate input, element selection, ... in the Allplan view
            pyp_path:                 path of the pyp file
            global_str_table_service: global string table service
            build_ele_list:           list with the building elements
            build_ele_composite:      building element composite with the building element constraints
            control_props_list:       control properties list
            modification_ele_list:    UUIDs of the existing elements in the modification mode

        Returns:
            Created interactor object
        """

        self.coord_input = coord_input
        self.build_ele_list = build_ele_list
        self.build_ele_composite = build_ele_composite
        self.control_props_list = control_props_list

        # show the palette
        self.palette_service = BuildingElementPaletteService(self.build_ele_list,
                                                             self.build_ele_composite,
                                                             None,
                                                             self.control_props_list,
                                                             "StartPythonHost.pyp")

        build_ele = self.build_ele_list[0]
        self.palette_service.show_palette(build_ele.script_name)

        # start http server
        address = "127.0.0.1"
        port = 5679
        try:
            log_path = Path(__file__).resolve().parents[2] / ".allplan-mcp" / "logs" / "bridge.log"
            self.server = BridgeServer((address, port), RequestHandler(self.coord_input), invoke_in_ui_thread, log_path=log_path)
            self.server.start()
        except Exception:
            self.palette_service.close_palette()
            raise

        print("Python Host is started")

        # this timer pushes python thread to process requests if user minimized main window
        self.timer = DispatcherTimer()
        self.timer.Interval = TimeSpan.FromMilliseconds(50)
        self.timer.Tick += self.push_python_thread
        self.timer.Start()

    @staticmethod
    def push_python_thread(sender, args):
        # do nothing
        return

    def on_cancel_function(self) -> bool:
        """ Handles the cancel function event (e.g. by ESC, ...)

        Returns:
            True/False for success.
        """

        self.server.stop()
        self.palette_service.close_palette()
        self.timer.Stop()
        self.timer.Tick -= self.push_python_thread
        print("Python Host is stopped")

        return True

    def process_mouse_msg(self, mouse_msg, pnt, msg_info) -> bool:
        return True

    def on_preview_draw(self):
        return

    def on_mouse_leave(self):
        return
