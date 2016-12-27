import Rhino
import System

def DisplayPolygonToolbarGroup():
    
    # Get toolbar collections (files)
    tb_files = Rhino.RhinoApp.ToolbarFiles
    
    # See if 'Default' toolbar file is loaded
    tb = tb_files.FindByName('Default', True)
    
    if not tb:
        # Get path to user profile
        path = System.Environment.GetFolderPath(System.Environment.SpecialFolder.ApplicationData)
        # Try loading 'Default" toolbar file
        tb = tb_files.Open(path + '\McNeel\Rhinoceros\5.0\UI\Default.rui')
    
    if not tb:
        # Something wrong...
        RhinoApp.WriteLine('Unable to open Default.rui')
        return
    
    # Find the 'Polygon' toolbar group
    grp = tb.GetGroup('Polygon');
    if grp:
        # Show toolbar group
        grp.Visible = True
        
        # Pause for user input
        str = ''
        rc, str = Rhino.Input.RhinoGet.GetString('Press <Enter> to continue', True, str)
        
        # Hide toolbar group
        grp.Visible = False


if __name__ == "__main__":
    DisplayPolygonToolbarGroup()