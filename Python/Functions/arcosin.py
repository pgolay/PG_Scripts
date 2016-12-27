def arcos(dblAng,blnRad):
    if blnRad == True:
        return Atn(-dblAng / Sqr(-dblAng * dblAng + 1)) + 2 * Atn(1)
    else:
        return Rhino.RhinoMath.ToDegrees( Atn(-dblAng / Sqr(-dblAng * dblAng + 1)) + 2 )
        
        
def VectorAngle(vec1,vec2):
    vec1 = rs.VectorUnitize(vec1)
    vec2 = rs.VectorUnitize(vec2)
    DP =  Vec1(0) * Vec2(0) + Vec1(1) * Vec2(1) +  Vec1(2) * Vec2(2)
    
    if DP  > .999999:
        VectorAngle = 0
    elif DP < -.999999:   
        VectorAngle = rs.ToDegrees(Rhino.Pi())
    else:
        VectorAngle = arcos(DP, False)