import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs
import System.Drawing.Text

def get_font():
    
    fams = System.Drawing.Text.InstalledFontCollection().Families
    lcSysFonts = [f.Name.lower() for f in fams]
    sysFonts = [f.Name for f in fams]
    
    while True:
        crntFont = sc.doc.Fonts[sc.doc.Fonts.CurrentIndex].FaceName
        sFont = crntFont
        if sc.sticky.has_key("NumbererCrntFont"):
            crntFont = sc.sticky["NumbererCrntFont"]
        
        gs = Rhino.Input.Custom.GetString()
        gs.SetCommandPrompt("Set current font.")
        gs.SetDefaultString(crntFont)
        opList = gs.AddOption("List")
        
        result = gs.Get()
        
        if gs.CommandResult()!= Rhino.Commands.Result.Success:
            return
            
        x = gs.OptionIndex()
        
        if gs.OptionIndex() == opList:
            sFont = rs.ListBox(sysFonts, "Set Nunberer font face.", "Numberer Font", crntFont)
            if not sFont: break
        
        else:sFont = gs.StringResult().Trim()
        
        if sFont.lower() in lcSysFonts:
            idx = sc.doc.Fonts.FindOrCreate(sysFonts[lcSysFonts.index(sFont.lower())], False, False)
            sc.sticky["NumbererCrntFont"] = sc.doc.Fonts[idx].FaceName
            break
        else:
            print sFont + " is not a valid font name."
            continue
    

def Numberer():
    
    crntNum = 0
    if sc.sticky.has_key("MyNum"):
        crntNum = sc.sticky["MyNum"]
        
    prefix = None
    if sc.sticky.has_key("NumPrefix"):
        prefix = sc.sticky["NumPrefix"]
        
    suffix = None
    if sc.sticky.has_key ("NumSuffix"):
        suffix = sc.sticky["NumSuffix"]
       
    outputStyle = 1
    if sc.sticky.has_key("NumOutputStyle"):
        outputStyle = sc.sticky["NumOutputStyle"]
        
    justCodes = 1, 2, 4, 65536, 131072, 262144
    
    count = 0
    numList = []
    while True:
        gp = Rhino.Input.Custom.GetPoint()
        opReset = gp.AddOption("Reset")
        StyleList = "Text","Dots"
        textList = "Size", "Font", "Style", "Justification"
        #OpList = gp.AddOptionList("Output", StyleList, outputStyle)
        opToggleStyle = Rhino.Input.Custom.OptionToggle(outputStyle,  "Text", "Dots")
        gp.AddOptionToggle("Output", opToggleStyle)
        
        opPref = gp.AddOption("Prefix")
        opSuf = gp.AddOption("Suffix")
        textIdx = 0
        opText = gp.AddOption("TextSettings")
        
        if count > 0 : opUndo = gp.AddOption("Undo")
        
        gp.SetCommandPrompt("Set number location or type a number. Current number = " + str(crntNum))
        gp.AcceptNumber(True, True)
        result = gp.Get()
        if gp.CommandResult()!= Rhino.Commands.Result.Success:
            return
        if result == Rhino.Input.GetResult.Number:
            crntNum = int(gp.Number())
            continue
        if result == Rhino.Input.GetResult.Option:
            if gp.OptionIndex() == opText:
                while True:
                    
                    #//////////////////////////////////////////
                    #Text Option defaults:
                    crntTextSize = 1
                    if sc.sticky.has_key("CurrentNumbererTextSize"):
                        crntTextSize = sc.sticky["CurrentNumbererTextSize"]
                        
                    textStyleIdx = 0
                    if sc.sticky.has_key("NumbererTextStyleIdx"):
                        textStyleIdx = sc.sticky["NumbererTextStyleIdx"]
                        
#                    textFont= "Arial"
#                    if sc.sticky.has_key("NumbererTextFont"):
#                        textFont = sc.sticky["NumbererTextFont"]
                    crntFont = sc.doc.Fonts[sc.doc.Fonts.CurrentIndex].FaceName
                    if sc.sticky.has_key("NumbererCrntFont"):
                        crntFont = sc.sticky["NumbererCrntFont"]
                        
                    textJust = 0
                    if sc.sticky.has_key("NumbererTextJust"):
                        textJust = sc.sticky["NumbererTextJust"]
                    
                    #//////////////////////////////////////////
                    
                    
                    #Set up an option getter:
                    #//////////////////////////////////////////
                    go = Rhino.Input.Custom.GetOption()
                    
                    go.SetCommandPrompt("Set text options")
                    opFont = go.AddOption("Font")
                    opDblHeight = Rhino.Input.Custom.OptionDouble(crntTextSize)
                    go.AddOptionDouble("Height",opDblHeight)
                    
                    textStyleList = "Normal", "Bold", "Italic", "BoldItalic"
                    opStyleList = go.AddOptionList("Style", textStyleList, textStyleIdx)
                    
                    justList = "Left", "CenterH", "Right", "Bottom","CenterV","Top"
                    opJustList = go.AddOptionList("Justification", justList, textJust)
                    
                    
                    #//////////////////////////////////////////

                    #//////////////////////////////////////////
                    go.Get()
                    
                    sc.sticky["CurrentNumbererTextSize"] = opDblHeight.CurrentValue
                    
                    if go.CommandResult()!=Rhino.Commands.Result.Success:
                        break
                        
                    if go.OptionIndex() == opFont: 
                        get_font()
                         
                        
                    if go.OptionIndex()==opJustList:
                        sc.sticky["NumbererTextJust"] = go.Option().CurrentListOptionIndex
                        
                    if go.OptionIndex()==opStyleList:
                        sc.sticky["NumbererTextStyleIdx"] = go.Option().CurrentListOptionIndex
                        
                    #//////////////////////////////////////////

                    
                    
            if count >0:
                if gp.OptionIndex() == opUndo:
                    rs.DeleteObject(numList.pop())
                    count = count-1
                    crntNum = crntNum-1
                    continue
                    
            outputStyle = opToggleStyle.CurrentValue
            sc.sticky["NumOutputStyle"] = outputStyle
            
            if gp.OptionIndex()== opReset:
                gi= Rhino.Input.Custom.GetInteger()
                gi.AcceptNumber(True, True)
                gi.SetDefaultInteger(1)
                gi.SetCommandPrompt("Start numbering at ") 
                numResult = gi.Get()
                if gi.CommandResult() != Rhino.Commands.Result.Success:
                    return gi.CommandResult()
                num = int(gi.Number())
                if num:
                    crntNum = num
                    sc.sticky["MyNum"]= num
                    continue
                crntNum = 1
                sc.sticky["MyNum"] = 1
                continue
                
            elif gp.OptionIndex()== opPref:
                prefix = rs.StringBox("Enter \"none\" for no prefix.", default_value = prefix, title = "Numberer Prefix")
                if prefix is None:
                    prefix = sc.sticky["NumPrefix"]
                else:
                     if isinstance(prefix, str):
                        sc.sticky["NumPrefix"] = prefix
                continue
                        
            elif gp.OptionIndex()== opSuf:
                suffix = rs.StringBox( "Enter \"none\" for no suffix.", default_value = suffix, title = "Numberer Suffix")
                if suffix is None:
                    sc.sticky["NumSuffix"] = suffix
                else:
                    if isinstance(suffix, str):
                        sc.sticky["NumSuffix"] = suffix
                continue
        else:
            pt = gp.Point()
            if pt:
                if sc.sticky.has_key("NumPrefix"):
                    prefix = sc.sticky["NumPrefix"]
                if not prefix: prefix = ""
                
                if sc.sticky.has_key("NumSuffix"):
                    suffix = sc.sticky["NumSuffix"]
                if not suffix: suffix = ""
                
                
                if outputStyle:
                    numList.append(rs.AddTextDot(prefix + str(crntNum) + suffix, pt))
                else:
                    crntTextSize = 1
                    if sc.sticky.has_key("CurrentNumbererTextSize"):
                        crntTextSize = sc.sticky["CurrentNumbererTextSize"]
                        
                    textStyleIdx = 0
                    if sc.sticky.has_key("NumbererTextStyleIdx"):
                        textStyleIdx = sc.sticky["NumbererTextStyleIdx"]
                        
                    textJust = 1
                    if sc.sticky.has_key("NumbererTextJust"):
                        textJust = justCodes[sc.sticky["NumbererTextJust"]]
                    
                    crntFont = sc.doc.Fonts[sc.doc.Fonts.CurrentIndex].FaceName
                    if sc.sticky.has_key("NumbererCrntFont"):
                        crntFont = sc.sticky["NumbererCrntFont"]
                        
                    numList.append(rs.AddText(prefix + str(crntNum) + suffix, pt, crntTextSize, crntFont, textStyleIdx, textJust))
                crntNum = crntNum+1
                count = count + 1
                sc.sticky["MyNum"] = crntNum
            
            else: return
    
Numberer()