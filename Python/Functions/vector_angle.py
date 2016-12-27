def vector_angle(vec1, vec2, blnRadians):
    DP = (vec1[0] * vec2[0]) + (vec1[1] * vec2[1]) +  (vec1[2] * vec2[2])
    if DP  > .999999:
        VectorAngle = 0
    elif DP < -.999999:
        VectorAngle = math.pi()
    else:
        VectorAngle = math.acos(DP)
        
    if blnRadians == False:
        return Rhino.RhinoMath.ToDegrees(VectorAngle)
    else:
        return VectorAngle