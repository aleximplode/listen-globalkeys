import keybinder
import utils
from plugins.generic import GenericPlugin
from player import Player
from widget.preference import HelperConfigureDialog
from config import config

def toggle_window():
    win = utils.get_main_window()

    if win.get_property('visible'):
        win.tray.cacher()
    else:
        win.tray.montrer()


class GlobalKeys(GenericPlugin):

    PLUGIN_NAME = "Global Key Bindings"
    PLUGIN_DESC = "Plugin to set global key bindings"
    PLUGIN_VERSION = "0.2"
    PLUGIN_AUTHOR = "Alexander Godlewski <alex@implode.ca>"
    PLUGIN_WEBSITE = ""
    
    func = {
        "globalkey_previous": Player.previous,
        "globalkey_pause": Player.pause,
        "globalkey_play": Player.playpause,
        "globalkey_stop": Player.stop,
        "globalkey_next": Player.next,
        "globalkey_rewind": Player.rewind,
        "globalkey_forward": Player.forward,
        "globalkey_toggle_window": toggle_window
        }
    
    def __init__(self):
        GenericPlugin.__init__(self)
        
        self.autoconnect(config, "config-changed", self.__on_config_changed)

        for (field, _) in self.func.items():
            key = config.get("plugins", field, "")
            if key:
                self.__bind(key, field)
                
            config.set("plugins", "%s_last" % field, key)
     
    def __handle_callback(self, text, callback):
    	self.logdebug(text)
    	callback()
    	
    def __bind(self, key, field):
        try:
            self.__try_unbind(key)
        except:
            pass
            
        keybinder.bind(key, lambda(text): self.__handle_callback(text, self.func[field]), "Global binding for %s pressed(%s)" % (field, key))
        self.logdebug("Bound %s" % key)

    def __try_unbind(self, key):
        try:
            self.logdebug("Unbinding %s" % key)
            keybinder.unbind(key)
            self.logdebug("Unbound %s" % key)
        except:
            self.logdebug("Did not unbind %s" % key)

    def delete_thyself(self):
        for field, _ in self.func.items():  
            key = config.get("plugins", field, "")
            if key:
                self.__try_unbind(key)
            
        GenericPlugin.delete_thyself(self)
        
    @staticmethod   
    def on_configure():
        GlobalKeysDialog()
        
    def __on_config_changed(self, dispatcher, section, option, value):
        if section == "plugins" and option.find("globalkey_") == 0 and option.find("_last") == -1:
            self.__try_unbind(config.get(section, option + "_last", value))
            
            if value:            
                self.__bind(config.get(section, option, value), option)
                
            config.set(section, option + "_last", value)
        
class GlobalKeysDialog(HelperConfigureDialog):
    def __init__(self):
        HelperConfigureDialog.__init__(self, GlobalKeys.PLUGIN_NAME)
        
        #Options will come out in a "random" order
        #It looks bad but will look better in a treeview one day
        for (key, _) in GlobalKeys.func.items():
            label = key.replace("globalkey_", "", 1).replace("_", " ").title()
            self.add(self.make_lentry(label, "plugins", key, ""))

        self.show_all()

