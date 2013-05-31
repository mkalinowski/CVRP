
def Union(x, y):
    xRoot = Find(x)
    yRoot = Find(y)
    
    joined_demand = xRoot.demand + yRoot.demand
    
    if x.isFirst() and y.isFirst():
        joined_first = xRoot.last 
        joined_last = yRoot.last
    elif x.isFirst() and y.isLast():
        joined_first = yRoot.first 
        joined_last = xRoot.last
    elif x.isLast() and y.isFirst():
        joined_first = xRoot.first 
        joined_last = yRoot.last
    elif x.isLast() and y.isLast():
        joined_first = xRoot.first 
        joined_last = yRoot.first
            
    if xRoot.rank > yRoot.rank:
        yRoot.parent = xRoot
    elif xRoot.rank < yRoot.rank:
        xRoot.parent = yRoot
    elif xRoot != yRoot:  
        yRoot.parent = xRoot
        xRoot.rank = xRoot.rank + 1
        
    xNewRoot = Find(xRoot)
    xNewRoot.first = joined_first
    xNewRoot.last = joined_last
    xNewRoot.demand = joined_demand

def Find(x):
    if x.parent == x:
        return x
    else:
        x.parent = Find(x.parent)
        return x.parent

def Joinable(capacity, x, y):
    xRoot = Find(x)
    yRoot = Find(y)
    return (xRoot != yRoot) and ((xRoot.demand + yRoot.demand) <= capacity) and x.isEnd() and y.isEnd()

class Path:
    def __init__(self, demand, val):
        self.val = val
        self.first = val
        self.last = val
        self.parent = self
        self.rank = 0
        self.demand = demand
    
    def isEnd(self):
        root = Find(self)
        return (self.val == root.first) or (self.val == root.last)
    
    def isFirst(self):
        root = Find(self)
        return self.val == root.first
    
    def isLast(self):
        root = Find(self)
        return self.val == root.last

    

