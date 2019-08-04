import numpy as np
import pandas as pd
import itertools
import operator

import time




pd.set_option('display.max_columns', None)

def preprocess(data, headerfile):
    headers = []

    with open(headerfile) as myFile:

        for line in myFile:

            header = line.split(',')
            headers.append(header[0])


    #print(headers)

    df = pd.read_csv(data, sep = ',', names = headers)

    transactions = []


    for header in headers:
        df[header] = np.where(df[header] >= 1, header, df[header])


    for rows in df.values:
        row_s = []
        for item in rows:
            if item != '0':
                row_s.append(item)
        transactions.append(row_s)

    transactions.sort()
    transactions_sets = set()

    for sublist in transactions:
        for item in sublist:
            transactions_sets.add(frozenset([item]))



    return transactions_sets, transactions



#
def scan_Data(set_dataset, f_data, s_level):

    #returns list with items that meet the support theshold

    support_count = {}
    for item in set_dataset:

        for candidate in f_data:

            if candidate.issubset(item):

                if not candidate in support_count:
                    support_count[candidate] = 1

                else:

                    support_count[candidate] += 1

    total_items = float(len(set_dataset))

    qualified = []
    support_vals = {}

    #support calculation

    for val in support_count:

        support_val = support_count[val]/total_items

        if support_val >= s_level:

            qualified.append(val)

        support_vals[val] = support_val


    return qualified, support_vals


#creation of candidate item sets
def setGen(freq_items, k):

    itemsets = []
    total_length = len(freq_items)

    for i in range(total_length):

        for j in range(i+1, total_length):

            list_1 = list(freq_items[i])[:k-2]
            list_2 = list(freq_items[j])[:k-2]

            list_1.sort()
            list_2.sort()

            if list_1 == list_2: #if first k-2 elements are equal

                itemsets.append(freq_items[i] | freq_items[j]) #set union

    return itemsets

#generate rules
def ruleGen(freq_items, supportData, c_level):

    rules = []
    rules2 = []

    #Sets with 2+ items
    for i in range(1, len(freq_items)):

        for set in freq_items[i]:

            X = [frozenset([item]) for item in set]
            if (i > 1):

                rulesConseq(set, X, supportData, rules, c_level, rules2)

            else:

                confidence_lift(set, X, supportData, rules, c_level,  rules2)

    return rules, rules2



#generates more rules from dataset by using the frequent set of items and a list of potential candidates
#for the right side of rule
def rulesConseq(items, rightCandidate, supportData, rules, c_level, rules2):

    n_item = len(rightCandidate[0])

    if (len(items) > (n_item + 1)):

        new_can = setGen(rightCandidate, n_item + 1)  #new candidates

        new_can_confidence = confidence_lift(items, new_can, supportData, rules, c_level, rules2)

        if (len(new_can_confidence) > 1):

            rulesConseq(items, new_can_confidence, supportData, rules, c_level, rules2)

#calculates confidence and lift values for each rule, only appends those that meet the threshhold
def confidence_lift(items, rightCandidate, supportData, rules, c_level, rules2):

    min_confidence = []  #holds list of rules that have minimum confidence at least
    lift_val = [] #holds all the lift value

    for item in rightCandidate:

        conf = supportData[items] / supportData[items-item]
        lift = supportData[items] / (supportData[items] * supportData[item])

        if conf >= c_level and lift >= 1: #rules with min confidence and positive correlation

            rules.append(str(items - item) + '-->' + str(item) + ' conf: ' + str(conf) + ' lift: ' + str(lift))
            rules2.append(items)

            min_confidence.append(item)
            lift_val.append(item)

    return min_confidence



data = 'small_basket.dat'
headerfile = 'products'

support_thresh = [0.2, 0.3, 0.5, 0.2, 0.3, 0.5, 0.3, 0.4, 0.3, 0.2, 0.1]
confid_thresh = [0.5, 0.5, 0.5, 0.8, 0.8, 0.8, 0.6, 0.5, 0.7, 0.7, 0.7]


f_data, dataset = preprocess(data, headerfile)

set_dataset = list(map(set, dataset))


for i in range(len(support_thresh)):

    start = time.time()

    item_set, supportData = scan_Data(set_dataset, f_data, support_thresh[i])

    freq_items = [item_set]
    k = 2

    while (len(freq_items[k-2]) > 0):

        can_set = setGen(freq_items[k - 2], k)
        items_2, support_2 = scan_Data(set_dataset, can_set, support_thresh[i])
        supportData.update(support_2)
        freq_items.append(items_2)

        k += 1

    rules, rules2 = ruleGen(freq_items, supportData, confid_thresh[i])

    end = time.time()
    print("Time: " + str(end - start))
    print("Support:", support_thresh[i])
    print("Confidence:", confid_thresh[i])

    k_items = 0
    for item in freq_items:
        k_items += 1
        print("K:", k_items, "items", len(item))

    x = 0
    num_rules = 0
    for item in rules2:
        if x < len(item):
            x = len(item)

    for item in rules2:
        if x == len(item):
            num_rules += 1

    print("Largest K:", k_items - 1)
    print("Number of rules in largest K:", num_rules)

    print("Listed rules:")

    for i in range(len(rules)):
        print(rules[i])

    print("")



