import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import RhinoPython.Host as __host

def escape_test( throw_exception=True, reset=False ):
    "Tests to see if the user has pressed the escape key"
    rc = __host.EscapePressed(reset)
    if rc and throw_exception:
        raise Exception('escape key pressed')
    return rc

def get_things():
    divs = 12
    if sc.sticky.has_key("OldDivs"):
        divs = sc.sticky["OldDivs"]
     
    go= Rhino.Input.Custom.GetObject()
    go.EnablePreSelect(False, False)
    gi = Rhino.Input.Custom.GetInteger()
    #intOp = Rhino.Input.Custom.OptionInteger(divs)
    #gi.AcceptNumber(True, True)
    gi.SetCommandPrompt("Divisions.<"+str(divs)+">")
    #gi.AddOptionInteger("Integer",intOp)
    

    X = go.Get()
    if go.CommandResult() != Rhino.Commands.Result.Success:
        return Rhino.Commands.Result

    if X == Rhino.Input.GetResult.Object:
        obj = go.Object(0)
       
    Y = gi.Get()
    if gi.CommandResult() != Rhino.Commands.Result.Success:
        h = gi.CommandResult()
        return Rhino.Commands.Result 
        
    if Y == Rhino.Input.GetResult.Number:
        divs = gi.Number()
        sc.sticky["OldDivs"] = divs
        return [obj, divs]
    else:
        divs = intOp.CurrentValue
        sc.sticky["OldDivs"] = divs
        return [obj, divs]
        
    
def test():
    objList = []
    divList = []
    
    while True:
        test = get_things()
        if type(test) != list:
            break
        else:
            objList.append(test[0])
            divList.append(test[1])

    X = 2
test()