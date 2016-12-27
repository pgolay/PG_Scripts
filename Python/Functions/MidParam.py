def SrfMidParam(srf):
    domU = srf.Domain(0)
    domV = srf.Domain(1)
    return [domU.T0 + ((domU.T1-domU.T0)/2) , domV.T0 + ((domV.T1-domV.T0)/2)]
    
def CrvMidParam(crv):
    dom = crv.Domain
    return dom.T0 + ((dom.T1-dom.T0)/2) 