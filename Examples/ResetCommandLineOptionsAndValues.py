import Rhino
import scriptcontext as sc

def get_inputs():
        
        # set some defaults
        X = True
        Y = True
        Z = True
        
        XSpace = 1
        YSpace = 1
        ZSpace = 1
        
        #retrieve the previous booleans if any
        if sc.sticky.has_key("Bools"):
            X = sc.sticky["XBool"]
        if sc.sticky.has_key("YBool"):
            Y = sc.sticky["YBool"]
        if sc.sticky.has_key("ZBool"):
            Z = sc.sticky["ZBool"]
        
        #retrieve previously used values if any
        if sc.sticky.has_key("XSpace"):
            XSpace = sc.sticky["XSpace"]
        if sc.sticky.has_key("YSpace"):
            YSpace = sc.sticky["YSpace"]
        if sc.sticky.has_key("ZSpace"):
            ZSpace = sc.sticky["ZSpace"]
        
        #set up the GetObject
        go = Rhino.Input.Custom.GetObject()
        go.SetCommandPrompt("Select a thing")
        
        #don't define or add any options until you get inside the while True: loop.
        # this way they are reinitialized every time the loop is run
        # and you can set the values from scratch so the command line
        # looks correct
        
        while True:
            # clear the previous options- 
            go.ClearCommandOptions()
            
            
            #it does them all, so you need to rebuild all options every time -
            
            boolOptionX = Rhino.Input.Custom.OptionToggle(X, "No", "Yes")
            boolOptionY = Rhino.Input.Custom.OptionToggle(Y, "No", "Yes")
            boolOptionZ = Rhino.Input.Custom.OptionToggle(Z, "No", "Yes")
        
            
            dblOptionX = Rhino.Input.Custom.OptionDouble(XSpace)
            dblOptionY = Rhino.Input.Custom.OptionDouble(YSpace)
            dblOptionZ = Rhino.Input.Custom.OptionDouble(ZSpace)        
            
            go.AddOptionToggle("XSection", boolOptionX)
            go.AddOptionToggle("YSection", boolOptionY)
            go.AddOptionToggle("ZSection", boolOptionZ)
            
            x_opt = go.AddOptionDouble("XSpacing", dblOptionX)
            y_opt = go.AddOptionDouble("YSpacing", dblOptionY)
            z_opt = go.AddOptionDouble("ZSpacing", dblOptionZ)
            
            
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            #This option, when clicked, forces all of the 'Spacing values to be the same as 
            # x_opt.CurrentValue. In order for the command line options to reflect this the 
            # next loop, the options all need to be rebuilt again inside the while True: loop
            
            all_opt = go.AddOption("SetAllSpacingToX") 
            #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
            
            rc = go.Get()
            
            if go.CommandResult() != Rhino.Commands.Result.Success:
                return go.CommandResult()
               
            if rc==Rhino.Input.GetResult.Object:
                 objRef = go.Object(0)
                 
                 XSpace = dblOptionX.CurrentValue
                 YSpace = dblOptionY.CurrentValue
                 ZSpace = dblOptionZ.CurrentValue
                
                
                #set all the sticky values before exiting the getter-
                 sc.sticky["XBool"] = X
                 sc.sticky["YBool"] = Y
                 sc.sticky["ZBool"] = Z
                
                 sc.sticky["XSpace"] = XSpace
                 sc.sticky["YSpace"] = YSpace
                 sc.sticky["ZSpace"] = ZSpace
                
                 break
                
            elif rc==Rhino.Input.GetResult.Option:
                XSpace = dblOptionX.CurrentValue
                YSpace = dblOptionY.CurrentValue
                ZSpace = dblOptionZ.CurrentValue
                X = boolOptionX.CurrentValue
                Y = boolOptionY.CurrentValue
                Z = boolOptionZ.CurrentValue
                
                if go.OptionIndex()==all_opt:
                    #reset the Y and Z values to match X
                    YSpace = XSpace
                    ZSpace = XSpace
                    
                    #reset the bools as well so they
                    #will be correct the next time the loop runs
                    X = boolOptionX.CurrentValue
                    Y = boolOptionY.CurrentValue
                    Z = boolOptionZ.CurrentValue
                    
                continue
           
        return objRef, X, Y, Z, XSpace, YSpace, ZSpace
        
x = get_inputs()