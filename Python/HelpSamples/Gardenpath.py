import rhinoscriptsyntax as rs
import math #Use this to get sine and cosine.
import Rhino.RhinoMath as rm #rhinoscriptsyntax.ToRadians() is missing

def test():
    
    Sin = math.sin
    Cos = math.cos
    	# Acquire information for the garden path

    sp = rs.GetPoint("Start point of path centerline")
    if sp is None: return
    
    ep = rs.GetPoint("End point of path centerline", sp)
    if ep is None: return
    
    hwidth = rs.GetDistance(sp, 1,  second_pt_msg = "Half width of path")
    if hwidth is None: return
    
    trad = rs.GetDistance(sp, 1.0, second_pt_msg = "Radius of tiles")
    if trad is None: return
    
    tspac = rs .GetDistance(sp, 1.0, second_pt_msg = "Distance between tiles")
    if tspac is None: return
    
    	# Calculate angles
    
    temp = rs.Angle(sp, ep)
    
    pangle = temp[0]
    
    plength = rs.Distance(sp, ep)
    
    width = hwidth * 2
    
    angp90 = pangle + 90.0
    
    angm90 = pangle - 90.0
    
    
	# To increase speed, disable redrawing

    rs.EnableRedraw (False)
    
	# Draw the outline of the path
    #make an empty list
    pline = []
    
    #add points to the list
    pline.append(rs.Polar(sp, angm90, hwidth))
    
    pline.append(rs.Polar(pline[0], pangle, plength))
    
    pline.append(rs.Polar(pline[1], angp90, width))
    
    pline.append(rs.Polar(pline[2], pangle + 180.0, plength))
    
    #add the first point back on to the end of the list to close the pline
    pline.append (pline[0])
    
    #create the polyline from the lst of points.
    rs.AddPolyline (pline)
    
    

    # Draw the rows of tiles
    
    #define a plane
    plane = rs.WorldXYPlane()
    
    pdist = trad + tspac
    
    off = 0.0
    
    while (pdist <= plength - trad):
    
        #Place one row of tiles given distance along path
        
        # and possibly offset it
        
        pfirst = rs.Polar(sp, pangle, pdist)
        
        pctile = rs.Polar(pfirst, angp90, off)
        
        pltile = pctile
        
        while (rs.Distance(pfirst, pltile) < hwidth - trad):
        
            plane = rs.MovePlane(plane, pltile)
            
            rs.AddCircle (plane, trad)
            
            pltile = rs.Polar(pltile, angp90, tspac + trad + trad)
        
        
        pltile = rs.Polar(pctile, angm90, tspac + trad + trad)
        
        while (rs.Distance(pfirst, pltile) < hwidth - trad):
        
            plane = rs.MovePlane(plane, pltile)
            
            rs.AddCircle (plane, trad)
            
            pltile = rs.Polar(pltile, angm90, tspac + trad + trad)

        pdist = pdist + ((tspac + trad + trad) * Sin(rm.ToRadians(60))) #Missing rs.ToRadians()
        
        if off == 0.0:
        
            off = (tspac + trad + trad) * Cos(rm.ToRadians(60))
        
        else:
        
            off = 0.0
    
   

	

    
if __name__ == "__main__":
    
    test()







