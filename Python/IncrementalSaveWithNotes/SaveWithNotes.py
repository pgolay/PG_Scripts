import scriptcontext as sc
import rhinoscriptsyntax as rs
import datetime

def IncrementalSaveWithNotes():
    
    notes = sc.doc.Notes
    t = datetime.datetime.today()
    y = str(t.year)
    m = str(t.month)
    d = str(t.day)
    h = str(t.hour)
    mi = str(t.minute)
    strT = m + "/"+ d +"/" + y + " " + h +":" + mi
    newN = rs.StringBox ("Type some stuff")
    if newN is not None:
        notes = notes + "\n \n"   + strT + "\n " + newN
        sc.doc.Notes = notes
    print (notes)
    rs.Command ("_Save")
    pass
    
if __name__ == "__main__":
    IncrementalSaveWithNotes()