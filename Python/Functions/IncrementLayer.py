import rhinoscriptsyntax as rs


def increment_name(name):
    if not rs.IsLayer(name):
        return name
    else:
        for num in range(999):
         test = name+("{:0>3d}".format(num))
         if not rs.IsLayer(test): return test
     
def test():
    
 name = increment_name("ping")
 rs.AddLayer(name)

test()
