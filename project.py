"""
This program is intended for use at the conclusion of the beta test of an examination form.
It assumes that an exam intended to have TARGET_LENGTH items was beta tested with a larger number of items.
The program recommends a list of items to remove from the form to achieve the target length.
It seeks to maximize one parameter, alpha.
It applies the following constraint: the test blueprint specifies minimum and maximum item counts
 for each content domain of the test; it avoids violating those rules.
Results are printed to the console.
"""

RESPONSE_STRING = 'alt_response_string.csv'
# RESPONSE_STRING is assumed to be a csv file with three entries per line:
#   candidate_ID
#   item_ID
#   response
# The combination candidate_ID and item_ID is assumed to be unique

BLUEPRINT = 'alt_blueprint.csv'
# BLUEPRINT is assumed to be a csv file with three values per row:
#   domain
#   min
#   max

KEYS = 'alt_keys.csv'
# KEYS is assumed to be a csv file with  two values per row:
#   item_ID
#   key (credited response)

DOMAINS = 'alt_domains.csv'
# DOMAINS is assumed to be a csv file with  two values per row:
#   item_ID
#   domain

TARGET_LENGTH = 75
# how many items should be in the ultimate form

#import itertools
import csv
import statistics

def main():
    #create a dictionary with the test blueprint
    d_blueprint = get_blueprint()
    #create a dictionary with the test keys
    d_keys = get_keys()
    #create a dictionary with the test domains
    d_domains = get_domains()
    #evaluate each response, returning a grid of 0s, 1s, and blanks for skipped items
    grid = evaluate_responses(d_keys)
    #find the optimal subset of items
    find_optimal_subset(grid, d_domains, d_blueprint)


def find_optimal_subset(grid, d_domains, d_blueprint):
    """
    gateway: generate a combination of TARGET_LENGTH items and measure alpha
    store combo and alpha as reference
    iterate through every possible combination of TARGET_LENGTH items,
    comparing alpha for that set with reference
    if alpha is higher, replace reference
    Oops!
    it turns out that the number of 75-item subsets of 100 items is astronomical.
    #combos = list(itertools.combinations(item_IDs, 98))
    new idea: take one item out at a time
    """
    # extract item_IDs from grid
    item_IDs = extract_item_IDs(grid)

    # initialize the list the program ultimately returns
    removed = []

    # recursively (if that's thw word) run reductio until we reach the target length
    while len(item_IDs) > TARGET_LENGTH:
        now_pop = reductio(grid, d_domains, item_IDs, d_blueprint)
        print("Optimal item to remove:", now_pop)
        removed.append(now_pop)
        item_IDs.remove(now_pop)
        print("New  number of items:", len(item_IDs))
        print("New alpha:", get_alpha(grid, item_IDs))
        print('')
    print("The program has concluded. Remove the following items:")
    print(removed)
    print('')
    alpha = get_alpha(grid, item_IDs)
    print("Alpha for the revised form is", round(alpha, 5))

def reductio(grid, d_domains, item_list, d_blueprint):
    # generates two lists to shorten and compare
    list = item_list.copy()    # keep item_list intact for iterations below
    alpha1 = 0                  # reference alpha
    removed = [0,0]             # reference item, experimental item
    removed[0] = list.pop(0)   # start off with [0]
    alpha1 = get_alpha(grid, list)     # get reference alpha
    for i in range(1, len(item_list)):
        list = item_list.copy()
        #check to see if removing this item would violate constraints
        if check_rules(list[i], list, d_blueprint, d_domains):
            removed[1] = list.pop(i)       # experimental item i
            alpha2 = get_alpha(grid, list) # experimental alpha i
            if alpha2 > alpha1:
                alpha1 = alpha2             # replace reference alpha if appropriate
                removed[0] = removed[1]     # replace reference item if appropriate
    return removed[0]

def get_alpha(grid, items):
    """
    here's a formula for alpha: (k/(k-1))*(1-(covpq/varx))
    where k is the number of items
    covpq is the sum of the products of the p-values and (1-p-values) of the items
    varx is the variance of the candidate scores
    """
    k = len(items)
    covpq = get_covpq(items, grid)
    varx = get_varx(items, grid)
    return (k/(k-1))*(1-(covpq/varx))

def get_covpq(items, grid):
    """
    For each item, we count (1) how many candidates scored 1 (ones)
    (2) how many candidates scored at all (i.e., not None) (ones_and_zeros)
    calculate pq, which is ones x (ones_and_zeros = ones) / ones_and_zeros squared
    """
    sum = 0      # the figure to be returned. Each loop will add its pq
    for item in items:
        # initialize more variables
        ones = 0
        ones_and_zeros = 0
        for cand in grid:
            result = grid[cand][item]
            if result != None:
                ones += result
                ones_and_zeros += 1
        pq = ones*(ones_and_zeros-ones)/(ones_and_zeros**2)
        sum += pq
    return sum

def get_varx(items, grid):
    """
    For each candidate, calculates score and adds to the list scores
    Then returns variance of scores
    """
    scores = []
    for cand in grid:
        score = 0
        for item in items:
            result = grid[cand][item]
            if result != None:
                score += result
        scores.append(score)
    return statistics.variance(scores)


def extract_item_IDs(grid):
    # returns a list of item_IDs from grid
    # since care has been taken to have a comprehensive list per candidate,
    # itcan  rely on the first entry in grid
    candidate_IDs = list(grid.keys())
    item_IDs = list(grid[candidate_IDs[0]].keys())
    return item_IDs

def extract_candidate_IDs(grid):
    # returns a list of candidate_IDs from grid
    return list(grid.keys())


def get_blueprint():
    """
    This function returns a dictionary with domain names as keys
    Each key returns a dictionary with two keys, min and max, with a value for each
    [If the BLUEPRINT file is missing a value, the function returns an error.][I wish.]
    It relies on the csv file specified in BLUEPRINT, which is assumed to have three values per row:
    domain
    min
    max
    """
    with open(BLUEPRINT, newline='', encoding='utf-8-sig') as f:
        next(f)
        d = {}
        reader = csv.reader(f)
        for line in reader:
            d[line[0]] = {} #create a dictionary for each domain name
            d[line[0]]['min'] = int(line[1]) #add min
            d[line[0]]['max'] = int(line[2]) #add max
        return d

def get_keys():
    """
    This function returns a dictionary with item names as keys and 'keys' as values
    It relies on the csv file specified in KEYS, which is assumed to have two values per row:
    item_ID (unique)
    key
    """
    with open(KEYS, newline='', encoding='utf-8-sig') as f:
        next(f)
        d = {}
        reader = csv.reader(f)
        for line in reader:
            d[line[0]] = line[1]
        return d

def get_domains():
    """
    This function returns a dictionary with item names as keys and 'domains' as values
    It relies on the csv file specified in DOMAINS, which is assumed to have two values per row:
    item_ID (unique)
    domain
    """
    with open(DOMAINS, newline='', encoding='utf-8-sig') as f:
        next(f)
        d = {}
        reader = csv.reader(f)
        for line in reader:
            d[line[0]] = line[1]
        return d

def evaluate_responses(d_keys):
    """
    This function creates a dictionary with candidateIDs as keys
    Each value is a dictionary with itemIDs as keys
    Each itemID for each candidate is given a 1 or 0 if the candidate responded to the item
    If the response matched the key, the value is 1; else, it's 0
    """
    # collect candidate and item lists
    cand_and_item = get_cand_and_item()

    # Make data dictionary
    grid = make_data_base(cand_and_item, d_keys)

    return grid


def make_data_base(cand_and_item, d_keys):
    """
    This function parses the file specified in RESPONSE_STRING, which is assumed to have three entries per line:
    candidate_ID
    item_ID
    response
    The combination candidate_ID and item_ID is assumed to be unique
    It requires cand_and_item, a list of two lists, the candidate_IDs and item_IDs
    and d_keys, a dictionary with item_IDs as keys and the credited response (key) for each item as values
    It returns grid, a dictionary with candidate_IDs as keys and dictionaries as values;
    these dictionaries have item_IDs as keys and 1, 0, or None as values
    """

    candidate_IDs = cand_and_item[0]
    item_IDs = cand_and_item[1]
    with open(RESPONSE_STRING, newline='', encoding='utf-8-sig') as f:
        next(f)
        d = {}
        for i in range(len(candidate_IDs)):
            d[candidate_IDs[i]] = {}
            for j in range(len(item_IDs)):
                d[candidate_IDs[i]][item_IDs[j]] = None
                #create blank in case candidate skipped item
        reader = csv.reader(f)
        for line in reader:
            cand = line[0]
            item = line[1]
            resp = line[2]
            point = check_key(item, resp, d_keys)
            d[cand][item] = point
    return d

def check_key(item, resp, d_keys):
    """
    This function looks up the credited response (key) for item in d_keys and compares it to
    the candidate response, resp, returning 1 if there's a match and 0 if there isn't.
    """
    key = d_keys[item]
    if not resp:
        return None
    if resp == key:
        return 1
    return 0


def get_cand_and_item():
    """
    This function parses the file specified in RESPONSE_STRING, which is assumed to have three entries per line:
    candidate_ID
    item_ID
    response
    The combination candidate_ID and item_ID is assumed to be unique
    It returns a list of two lists, the candidate_IDs and item_IDs
    """
    with open(RESPONSE_STRING, newline='', encoding='utf-8-sig') as f:
        next(f)
        candidate_IDs = []
        item_IDs = []
        reader = csv.reader(f)
        for line in reader:
            # make a list of candidates
            if line[0] not in candidate_IDs:
                candidate_IDs.append(line[0])
            # make a list of itemIDs
            if line[1] not in item_IDs:
                item_IDs.append(line[1])
    return [candidate_IDs, item_IDs]

def check_rules(item, item_list, d_blueprint, d_domains):
    """
    This function checks to see if the removal of an item would violate the blueprint rules
    item is the item being evaluated.
    item_list is the current list of items, with strings as item names
    d_blueprint is a dictionary with domain names as keys; each value is a dictionary with keys 'min' and 'max'
    d_domains is a dictionary with items as keys and their domains as values
    The function returns False is removing the item would lead to a violation of constraints
    """
    # make a dictionary with domains as keys and item counts as values
    d = {}
    for i in item_list:
        domain = d_domains[i]
        if domain not in d:
            d[domain] = 1
        else:
            d[domain] += 1

    #test 1: will removing this item bring domain item count below the minimum?
    #specify domain of item in quo
    item_domain = d_domains[item]
    if d[item_domain] - 1 < d_blueprint[item_domain]['min']:
        return False

    #test 2: will removing this item make it impossible to bring other domains' item counts below max?
    for domain in d:
        if domain != item_domain:
            #on the left: how many items are left to remove
            #on the right: how many items over max we are in this domain
            #effectively, at a certain point it'll only allow removal of items in domains that are running over
            #there may be potential for error here if two domains are equally over max???
            if (len(item_list)-TARGET_LENGTH) < (d[domain] - d_blueprint[domain]['max']):
                return  False

    #You didn't fail. Yay!
    return True

if __name__ == '__main__':
    main()
