'''
Created on Jul 31, 2015

@author: Ross
'''
from traits.api import provides, Callable
from traitsui.api import Controller, View, Item, CheckListEditor
from envisage.api import Plugin, contributes_to
from pyface.api import ImageResource

from cytoflowgui.op_plugins import OpHandlerMixin, IOperationPlugin, OP_PLUGIN_EXT
from cytoflow import MixtureModelOp

class MixtureModelHandler(Controller, OpHandlerMixin):
    """
    classdocs
    """
    
    def default_traits_view(self):
        return View(Item('object.name'),
                    Item('object.channels',
                         editor = CheckListEditor(name='handler.previous_channels',
                                                  cols = 2),
                         style = 'custom'),
                    Item('object.numPopulations',
                         label = 'Number of Populations',
                         style = 'readonly'),
                    Item('object.transform',
                         label = 'Data Transformation',
                         style = 'readonly'))
    
@provides(IOperationPlugin)
class HLogPlugin(Plugin):
    """
    class docs
    """
    
    id = 'edu.mit.synbio.cytoflowgui.op_plugins.mixtureModel'
    operation_id = 'edu.mit.synbio.cytoflow.operations.mixtureModel'
    
    short_name = "Mixture Model"
    menu_group = "Clustering"
     
    def get_operation(self):
        ret = MixtureModelOp()
        ret.add_trait("handler_factory", Callable)
        ret.handler_factory = MixtureModelHandler
        return ret
    
    def get_default_view(self, op):
        return None
    
    def get_icon(self):
        return ImageResource('GMM')
    
    @contributes_to(OP_PLUGIN_EXT)
    def get_plugin(self):
        return self
    

    
        