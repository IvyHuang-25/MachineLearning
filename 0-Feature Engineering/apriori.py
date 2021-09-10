'''
    1、发现频繁项集
'''
# 生成单一元素的项集
def create_C1():
    C1 = set()
    for transaction in dataSet:
        for item in transaction:
            C1.add(frozenset([item])) # 每条交易记录中的单个商品
    return C1 # {frozenset({'l1'}), frozenset({'l2'}), frozenset({'l3'}), frozenset({'l4'}), frozenset({'l5'})}

# 频繁项集组合
def create_Ck(Lk, k):
    """

    :param Lk: 包含了k-1个元素的频繁项集
    :param k:
    :return: Ck: 包含了k个元素的频繁项集
    """
    Ck = set()
    len_Lk = len(Lk)
    list_Lk = list(Lk)
    for i in range(len_Lk):
        for j in range(1, len_Lk):
            L1 = list(list_Lk[i])
            L2 = list(list_Lk[j])
            L1.sort()
            L2.sort()
            # 前k-2项相同时，将两个集合合并
            if L1[0:k-2] == L2[0:k-2]:
                Ck_item = list_Lk[i] | list_Lk[j]
                if is_apriori(Ck_item, Lk):
                    Ck.add(Ck_item)
    return Ck

# 判断是否满足Apriori原理
def is_apriori(Ck_item, Lk):
    """

    :param Ck: 包含了k个元素的可能频繁项集
    :param Lk: 包含了k-1个元素的频繁项集
    :return: bool, 是否满足Apriori原理
    """
    for item in Ck_item:
        sub_Ck = Ck_item - frozenset([item])
        if sub_Ck not in Lk:
            return False
    return True

def generate_Lk_by_Ck(Ck, minSupport=0.5):
    Lk = set()
    item_count = {}

    for t in dataSet:
        for item in Ck:
            if item.issubset(t):
                if item not in item_count:
                    item_count[item] = 1
                else:
                    item_count[item] += 1
    # 计算支持度
    for item in item_count:
        support = item_count[item] / float(len(dataSet))
        if support >= minSupport:
            Lk.add(item)
            supportData[item] = support

    return Lk

def generate_L(minSupport):
    C1 = create_C1()
    L1 = generate_Lk_by_Ck(C1, minSupport)

    L = []
    Lksub1 = L1.copy()
    L.append(Lksub1)
    for lk in Lksub1:
        freq_itemsets.append((lk, supportData[lk]))
    i = 2

    while True:
        Ci = create_Ck(Lksub1, i)
        Li = generate_Lk_by_Ck(Ci, minSupport)
        Lksub1 = Li.copy()
        if len(Lksub1) == 0:
            break
        L.append(Lksub1)
        for lk in Lksub1:
            freq_itemsets.append((lk, supportData[lk]))
        i += 1

    return L, freq_itemsets


'''
    2、找出关联规则
'''
def generate_rules(L, minSupport):
    big_rule_list = []
    sub_set_list = []
    for i in range(0, len(L)):
        for freq_set in L[i]:
            for sub_set in sub_set_list:
                if sub_set.issubset(freq_set):
                    support = supportData[freq_set] / supportData[freq_set - sub_set]
                    big_rule = (freq_set - sub_set, sub_set, support)
                    if support >= minSupport and big_rule not in big_rule_list:
                        big_rule_list.append(big_rule)
            sub_set_list.append(freq_set)
    return big_rule_list



supportData = {}
freq_itemsets = []
dataSet = [['l1', 'l2', 'l5'],
         ['l2', 'l4'],
         ['l2', 'l3'],
         ['l1', 'l2', 'l4'],
         ['l1', 'l3'],
         ['l2', 'l3'],
         ['l1', 'l3'],
         ['l1', 'l2', 'l3', 'l5'],
         ['l1', 'l2', 'l3']]

if __name__ == "__main__":
    L, _ = generate_L(minSupport=0.2)
    big_rule_list = generate_rules(L, minSupport=0.7)

    for Lk in L:
        print("="*50)
        print("frequent " + str(len(list(Lk)[0])) + "-itemsets\t\tsupport")
        print("="*50)
        for freq_set in Lk:
            print(freq_set, supportData[freq_set])

    print()
    print("Big Rules")
    for item in big_rule_list:
        print(item[0], " => ", item[1], " conf: ", item[2])
