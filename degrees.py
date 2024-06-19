import csv
import sys
import copy

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


# # All the ids of actors
# actor_ids = []

# movie_ids = set()

# array_of_frontiers = []

# added = []


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass
# # This needs to contain movie and actor tuple
# def populate_actor_ids(people):
#     for person in people:
#         for movie in people[person]["movies"]:
#             actor_ids.append((movie, person))
#     return

# def populate_movie_ids(people):
#     for person in people:
#         for movie in people[person]["movies"]:
#             movie_ids.add(movie)

def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "small"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    # WIll be cheaper to create this once and then pop it as I go and just check if empty
    # populate_actor_ids(people)
    # populate_movie_ids(people)
    
    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    
    source_id = person_id_for_name(source)
    target_id = person_id_for_name(target)
    visited = set()

    initial_state = Node(source_id, None, None)
    sf = StackFrontier()
    sf.add(initial_state)

    while not sf.empty():
        node = sf.remove()

        if node.state == target_id:
            path = extract_path(node)

        for movie, actor in neighbors_for_person(node.state):
            if actor not in visited and not sf.contains_state(target_id):
                visited.add(actor)
                node = Node(actor, node, movie)
                sf.add(node)

    return path

def extract_path(node):
    path = []
    while node.parent is not None:
        path.append((node.state, node.action))
        node = node.parent
    path.reverse()
    return path

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()


# def frontier_recursion(object, target_id, not_visited=actor_ids, already_checked=added, iterations = x):
#     """
#     Recursively explores the frontier until a connection to the target is found.
#     Each recursion maintains its state of people checked.
#     """
#     copy_of_the_object = copy.deepcopy(object)
#     not_visited = copy.deepcopy(not_visited)
#     # for node in copy_of_the_object.frontier:
#     #     # print(node.current)
#     #     # print(node.state)
        
#     for node in copy_of_the_object.frontier:
#         # print("Current - ")
#         # print(node.current)
#         if node.current not in already_checked and iterations > 0:
#             # print(node.state)
#             for state in node.state:
#                 print("Checking - ")
#                 print(state)
#                 already_checked.append(node.current)
#                 if state[1] == target_id:
#                     print("New iteration")
#                     print("Found - ")
#                     print(state)
#                     # copy_of_the_objects.state, contains already some values, I need only current
#                     array_of_frontiers.append([copy_of_the_object, state])
#                     iterations -= 1
#                     break
#     # Currently it overwrites the array_of_frontiers, so only the last one is left                
#     for state in node.state:
#         if not_visited != []:
#             if state in not_visited:
#                 next_node = Node(neighbors_for_person(state[1]), node.current, (state[0], state[1]), None)
#                 not_visited.remove(state)
#                 copy_of_the_object.add(next_node)
#                 frontier_recursion(copy_of_the_object, target_id, not_visited, already_checked)
#         else:
#             return "Finished"
            
# def path_extraction(array_of_frontiers):
#     """
#     Extracts the paths from the list of frontiers
#     """
#     paths = []
#     for object in array_of_frontiers:
#         print("new object in array")
#         temp_path = []
#         for i, node in enumerate(object[0].frontier):
#             print("New node in frontier")
#             if i > 0:
#                 print(node.state)
#                 temp_path.append((node.current))
          
#         temp_path.append(object[1])
#         paths.append([temp_path])
#     paths.sort(key=len)
#     return paths
