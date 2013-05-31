import math
import random
import copy
import union_find as uf
import itertools
from collections import deque
import pp

class ProblemInstance:
    def __str__(self):
        return """Name: %s
Type : %s
Comment: %s
Nodes: %s
Dimension: %s
Capacity: %s
Edge weight: %s
Node demand: %s
Node coordinate type: %s
""" % (self.name,
    self.type,
    self.comment,
    self.node_coord,
    self.dimension,
    self.capacity,
    self.node_distances,
    self.node_demand,
    self.ewt)

    def prepare(self):
        if self.ewt == "EUC_2D":
            def metric((x, y), (a, b)):
                return math.sqrt((x - a) ** 2 + (y - b) ** 2)
        else:
            def metric(a, b):
                return 0
        self.node_distances = [ [ metric(self.node_coord[i], self.node_coord[j])  for i in range(self.dimension) ] for j in range(self.dimension) ]
        return self

    def  __init__(self):
        self.name = ""
        self.type = ""
        self.comment = ""
        self.dimension = 0
        self.capacity = 0
        self.nct = "NO_COORDS"
        self.ewt = ""
        self.ewf = ""
        self.edf = ""
        self.ddt = "NO_DISPLAY"

        self.node_coord = {}
        self.node_distances = {}
        self.node_demand = {}


class Solution:
    def  __init__(self, p):
        self.problem = p.name
        self.capacity = p.capacity
        self.paths = [uf.Path(p.node_demand[i], i) for i in xrange(p.dimension)]
        self.used_savings = deque()
        self.solution = sum([2 * p.node_distances[0][i] for i in range(1, p.dimension)])
        
    def feasibleSaving(self, saving):
        (_, i, j, _) = saving
        return uf.Joinable(self.capacity, self.paths[i], self.paths[j])
        
    def processSaving(self, saving):
        (k, i, j, s) = saving
        x = self.paths[i]
        y = self.paths[j]
        if uf.Joinable(self.capacity, x, y):
            uf.Union(x, y)
            self.used_savings.append(k)
            self.solution -= s
            

def randomSampling(solution, savings, current_best):
    p = random.uniform(0.05, 0.2)
    for s in savings:
        if random.random() < p:
            if solution.feasibleSaving(s):
                solution.processSaving(s) 
    return solution 
    
                
def saving(p, i, j):
    c = p.node_distances
    return c[0][i] + c[0][j] - c[i][j]

def buildSavingsList(p):
    savings = sorted([(i, j, saving(p, i, j)) for i in xrange(1, p.dimension) for j in xrange(i, p.dimension) if i != j], key=lambda tup: tup[2], reverse=True)
    return [(i,) + savings[i] for i in xrange(len(savings))]

def remote_job(chunk_size, solution, deque_savings, best):
    local_best_cost = best
    local_best_path = None
    
    local_solution = copy.deepcopy(solution)
    probe = randomSampling(local_solution, deque_savings, local_best_cost)
    local_sum = probe.solution
    
    for _ in xrange(1, chunk_size):
        local_solution = copy.deepcopy(solution)
        probe = randomSampling(local_solution, deque_savings, local_best_cost)
        local_sum += probe.solution
        if probe.solution < local_best_cost:
            local_best_cost = probe.solution
            local_best_path = probe.used_savings
    return (local_best_cost, local_best_path, local_sum)


def MonteCarloSimulation(problem, ncpus,nprobes,servers):
    ppservers = tuple(servers)
    job_server = pp.Server(ppservers=ppservers)
    
    sol = Solution(problem)
    best_cost = sol.solution
    best_path = sol.used_savings
                    
    savings = buildSavingsList(problem)
    deq_savings = deque(savings)
    if ncpus == None or ncpus < 1:
        ncpus = job_server.get_ncpus()
    chunk_size = nprobes / ncpus
    print "There are %d cpus available." % ncpus 
    for _ in xrange(len(savings) - 10):
        saving = deq_savings.popleft()
        if sol.feasibleSaving(saving):  
            
            unprocessed = sol
            no = 0 
            jobs = [job_server.submit(remote_job, (chunk_size, unprocessed, deq_savings, best_cost), (randomSampling,), ("random", "copy", "itertools")) for _ in xrange(ncpus)]
            results = [job() for job in jobs]
            for (lbest_cost, lbest_path, lsum) in results:
                if lbest_cost < best_cost:
                    best_cost = lbest_cost
                    best_path = lbest_path
                no += lsum
                 
            processed = copy.deepcopy(sol)
            processed.processSaving(saving)
            yes = 0       
            jobs = [job_server.submit(remote_job, (chunk_size, processed, deq_savings, best_cost), (randomSampling,), ("random", "copy", "itertools")) for _ in xrange(ncpus)]  
            results = [job() for job in jobs]
            for (lbest_cost, lbest_path, lsum) in results:
                if lbest_cost < best_cost:
                    best_cost = lbest_cost
                    best_path = lbest_path
                yes += lsum
                
            if yes < no:
                sol = processed
    
    l = savings[len(savings) - 10:]
    subsets = list(itertools.chain(*[itertools.combinations(l, ni) for ni in xrange(1, len(l) + 1)]))
    for subset in subsets:
        solution_copy = copy.deepcopy(sol)
        for s in subset:
            if solution_copy.feasibleSaving(s):
                solution_copy.processSaving(s)
        if solution_copy.solution < best_cost:
            best_cost = solution_copy.solution
            best_path = solution_copy.used_savings
    paths = [[i] for i in xrange(problem.dimension)]
    for (i, j) in [savings[n][1:3] for n in best_path]:
        if paths[i][0] == i and paths[j][0] == j:
            newpath = paths[i][::-1] + paths[j]
        elif paths[i][0] == i and paths[j][-1] == j:
            newpath = paths[j] + paths[i]
        elif paths[i][-1] == i and paths[j][0] == j:
            newpath = paths[i] + paths[j]
        elif paths[i][-1] == i and paths[j][-1] == j:
            newpath = paths[i] + paths[j][::-1] 
        for k in newpath:
                paths[k] = newpath
        
    job_server.print_stats()
    return best_cost, [k for k, _ in itertools.groupby(sorted(paths[1:]))]

