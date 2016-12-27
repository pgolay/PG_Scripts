import rhinoscriptsyntax as rs
import Rhino
import scriptcontext



def get_inputs():
    
    KEYOLDSEGS = "OldSegs"
    KEYOLDTOL = "OldTol"
    KEYOLDRAD = "OldRad"
    KEYOLDCAP = "OldCap"
    
    def stickysetting(name, value_if_missing):
        if scriptcontext.sticky.has_key(name): return scriptcontext.sticky[name]
        return value_if_missing
        
    dblTol = stickysetting(KEYOLDTOL, scriptcontext.doc.ModelAbsoluteTolerance)
    dblRad = stickysetting(KEYOLDRAD, 1.0)
    listIndex = stickysetting(KEYOLDCAP, 2)
    intSegs = stickysetting(KEYOLDSEGS, 6)
    
    go = Rhino.Input.Custom.GetObject()
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Surface|Rhino.DocObjects.ObjectType.PolysrfFilter
    #go.EnablePressEnterWhenDonePrompt(False)

    go.SetCommandPrompt("Set Pipe options.")
    
    
    # set up the options
    segOption = Rhino.Input.Custom.OptionInteger(intSegs, 3, 128)
    tolOption = Rhino.Input.Custom.OptionDouble(dblTol)
    radOption = Rhino.Input.Custom.OptionDouble(dblRad)
    

    
    listValues = "None", "Flat", "Round"
    
    go.AddOptionDouble("Radius", radOption)
    go.AddOptionInteger("SegmentsAround", segOption)
    go.AddOptionDouble("CurveTolerance", tolOption)
    
    boolOption = Rhino.Input.Custom.OptionToggle(True, "Off", "On")
    go.AddOptionToggle("Boolean", boolOption)
    
    listIndex = 2
    capList = go.AddOptionList("Cap", listValues, listIndex)
    while True:
        # perform the get operation. This will prompt the user to
        # input a point, but also allow for command line options
        # defined above
        get_rc = go.Get()
        if go.CommandResult()!=Rhino.Commands.Result.Success:
            return go.CommandResult()

        elif get_rc==Rhino.Input.GetResult.Object:
            if go.OptionIndex()==capList:
              listIndex = go.Option().CurrentListOptionIndex
            continue
        break
        
 
    scriptcontext.sticky[KEYOLDSEGS] = segOption.CurrentValue
    scriptcontext.sticky[KEYOLDTOL] = tolOption.CurrentValue
    scriptcontext.sticky[KEYOLDCAP] = listIndex
    scriptcontext.sticky[KEYOLDRAD] = radOption.CurrentValue
        
        
    return  radOption.CurrentValue, segOption.CurrentValue, listIndex, tolOption.CurrentValue # Rhino.Commands.Result.Success

get_inputs()