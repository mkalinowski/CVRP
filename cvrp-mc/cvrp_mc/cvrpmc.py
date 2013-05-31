#! /usr/bin/python

import tsplib
import cvrp
import time
import argparse
    


def main(args):
    
    problem = tsplib.readProblem(args.infile)
    solution = cvrp.MonteCarloSimulation(problem, args.ncpus,args.nprobes, args.servers)
    tsplib.writeSolution(solution, filename = args.outfile)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Computes optimal solution for a given CVRP problem using Monte-Carlo methods based on Clarke & Wright\'s Savings heuristic.')
    parser.add_argument("infile",
            help="File with a problem specification in the TSPLIB format.")
    parser.add_argument("-o", metavar="<file>", dest="outfile",
            help="Place the output into <file>")
    parser.add_argument("-j --jobs", metavar="N", dest="ncpus", type=int, 
            help="Computation will be split into N jobs. Default is the number of cpu cores available on the local computer.")
    parser.add_argument("-p --probes", metavar="N", dest="nprobes", type=int, default=100,
            help="Number of probes used at each step of the computation.")
    parser.add_argument("-s --servers", metavar="S", dest="servers", nargs="+", default = [],
            help="IP addresses of additional servers used for computations.")

    args = parser.parse_args()

    start_time = time.time()
    main(args)
    print "\nTime elapsed: ", time.time() - start_time, "s"
