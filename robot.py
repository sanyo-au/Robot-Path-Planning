import pyvisgraph as vg
import pygame
import sys
import inputbox
from pygame.locals import *
from pyvisgraph.visible_vertices import visible_vertices
from pyvisgraph.graph import Graph, Edge
from itertools import izip
import time

#Node class to store all the points and their path cost and heuristic value
class Node:
    def __init__(self, x , y):
        self.parent = None
        self.x = x
        self.y = y
        self.heuristic = 0
        self.pathcost = 0

#function to find the children of the given node, returns a list of all the children of a particular node
def add_children(node, listofEdges, listofNodes):
    listofChildren = []
    for i in listofEdges:
        #check the first point of the edge
            if i.p1.x == node.x and i.p1.y == node.y:
                for j in listofNodes:
                        if i.p2.x == j.x and i.p2.y == j.y:
                            listofChildren.append(j)
        #check the second point of the edge
            if i.p2.x == node.x and i.p2.y == node.y:
                for j in listofNodes:
                    if i.p1.x == j.x and i.p1.y == j.y:
                        listofChildren.append(j)
    return listofChildren


#function to calculate the heuristic
def euclidean(node1, node2):
    #straight line distance between to points
    distance = ((((node1.x - node2.x) ** 2) + ((node1.x - node2.x) ** 2)) ** (0.5))
    return distance


#implememntation of the A star algorithm
def aStar(listofNodes, listofEdges, start_x, start_y, end_x , end_y):

    open1 = set()
    closed = set()
    for i in listofNodes:
        if i.x == start_x and i.y == start_y :
            current = i
            open1.add(i)

    while open1:

        current = min(open1, key=lambda o: o.pathcost + o.heuristic)
        if current.x == end_x and current.y == end_y:
            shortest_path = []
            while current.parent :
                shortest_path.append([current.x,current.y])
                current = current.parent
            shortest_path.append([current.x,current.y])
            return shortest_path

        open1.remove(current)
        closed.add(current)

        l = add_children(current, listofEdges, listofNodes)
        for i in l:
                if i in closed:
                    continue
                if i in open1:
                    new = current.pathcost + euclidean(current, i)
                    if new < i.pathcost:
                        i.pathcost = new
                        i.parent = current

                else:
                    i.pathcost = current.pathcost + euclidean(current, i)

                    for j in listofNodes:
                        if j.x == end_x and j.y == end_y:
                            i.heuristic = euclidean(i, j)
                    i.parent = current
                    open1.add(i)


#builds a graph by appending the starting and ending vertices to the visibility graph
def build_graph(graph, origin, destination):

    origin_exists = origin in graph.visgraph
    dest_exists = destination in graph.visgraph
    if origin_exists and dest_exists:
        return graph.visgraph
    orgn = None if origin_exists else origin
    dest = None if dest_exists else destination
    if not origin_exists:
        for v in visible_vertices(origin, graph.graph, destination = dest):
            graph.visgraph.add_edge(Edge(origin, v))
    if not dest_exists:
        for v in visible_vertices(destination, graph.graph, origin = orgn):
            graph.visgraph.add_edge(Edge(destination, v))
    return graph.visgraph


#get the input file from the user
def get_input_file(filename):
    with open(filename, 'r') as f:
        my_list = [line.strip().split(',') for line in f]
    my_list = [[int(column) for column in row] for row in my_list]
    return my_list


def main():
    start_x = start_y = 0
    end_x = end_y = 0
    #initialize the display
    pygame.init()
    noOfMouseClick = 0
    SURFACE = pygame.display.set_mode((900, 600))
    SURFACE.fill((255, 255, 255))






    pygame.display.set_caption("Robot Path Planning")
    #ask for input from user in the GUI itself
    answer = inputbox.ask(SURFACE, "Name of the file: ")
    my_list = get_input_file(answer)
    polys = []
    poly2 = []
    SURFACE.fill((255, 255, 255))
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP:
                for i in my_list:
                    zipped = zip(i[::2], i[1::2])
                    poly2.append(zipped)
                    pygame.draw.polygon(SURFACE, (0, 0, 0), zipped, 1)
                    poly1 = []
                    for j, k in zipped:
                        poly1.append(vg.Point(j, k))
                    polys.append(poly1)

            #the first click takes the point as the start point
            elif event.type == MOUSEBUTTONDOWN and event.button == 1 and noOfMouseClick == 0:
                start_x, start_y = event.pos
                pygame.draw.circle(SURFACE, (0,0,0), [start_x, start_y], 5)

                robot_char = pygame.Rect(start_x, start_y, 20, 30)
                robot = pygame.image.load("Cartoon_Robot.png")
                robot = pygame.transform.scale(robot, (50,50))
                SURFACE.blit(robot, robot_char)

                noOfMouseClick = 1
            #the second click is the place where the robot's path ends
            elif event.type == MOUSEBUTTONDOWN and event.button == 1 and noOfMouseClick == 1:
                end_x, end_y = event.pos
                pygame.draw.circle(SURFACE, (0, 0, 0), [end_x, end_y], 5)
                noOfMouseClick = 2
            #on the third click the visibility graph is drawn
            elif event.type == MOUSEBUTTONDOWN and event.button == 1 and noOfMouseClick == 2:
                noOfMouseClick = 3
                g = vg.VisGraph()
                g.build(polys)
                gra = build_graph(g, vg.Point(start_x, start_y), vg.Point(end_x, end_y))
                listofEdges = list(gra.get_edges())
                for i in listofEdges:
                    pygame.draw.line(SURFACE, (255, 0, 0), [i.p1.x, i.p1.y], [i.p2.x, i.p2.y], 2)

                pygame.draw.circle(SURFACE, (0, 0, 0), [start_x, start_y], 5)
                pygame.draw.circle(SURFACE, (0, 0, 0), [end_x, end_y], 5)
                for i in poly2:
                    pygame.draw.polygon(SURFACE, (0, 0, 0), i)
            #on the fourth click, the shortest path is calculated and drawn
            elif event.type == MOUSEBUTTONDOWN and event.button == 1 and noOfMouseClick == 3:
                noOfMouseClick = 4
                poly2.append([(start_x, start_y)])
                poly2.append([(end_x, end_y)])
                listofNodes = []
                for i in poly2:
                    for j, k in i:
                        listofNodes.append(Node(j,k))

                shortest_path = aStar(listofNodes, listofEdges, start_x, start_y, end_x, end_y)
                for i in listofNodes:
                    if i.x == end_x and i.y == end_y:
                        shortest_distance = i.heuristic + i.pathcost
                for i, j in shortest_path:
                    robot_char.x = i
                    robot_char.y = j
                    SURFACE.blit(robot, robot_char)
                print "Start point is :"
                print start_x ,start_y
                print "Goal point is :"
                print end_x,end_y
                print "Shortest path is :"
                print shortest_path
                print "Shortest Distance is:"
                print shortest_distance

                for i in range(len(shortest_path) - 1):
                    pygame.draw.line(SURFACE, (0, 255, 0), shortest_path[i], shortest_path[i+1], 5)

                pygame.draw.circle(SURFACE, (0, 0, 0), [start_x, start_y], 5)
                pygame.draw.circle(SURFACE, (0, 0, 0), [end_x, end_y], 5)

            pygame.display.update()

if __name__ == "__main__":
    main()
