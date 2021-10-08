'''

'''

"""
    1、定义FP树
"""
class treeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue # 节点名字
        self.count = numOccur # 节点计数值
        self.nodeLink = None # 用于链接相似的元素项
        self.parent = parentNode # 需要被更新
        self.children = {} # 子节点

    def inc(self, numOccur):
        # 对count变量增加给定值
        self.count += numOccur

    def disp(self, ind=1):
        # 将树以文本形式展示
        print(' ' * ind, self.name, ' ', self.count)
        for child in self.children.values():
            child.disp(ind + 1)

"""
    2、FP树构建
"""
def createTree(initSet, minSup=1):
    # 创建FP树
    headerTable = {}

    '''第一次扫描数据集'''
    # 1、计算item出现的频数
    for trans in initSet:
        for item in trans:
            headerTable[item] = headerTable.get(item, 0) + initSet[trans]

    # 2、设置最小支持度
    headerTable = {k:v for k, v in headerTable.items() if v >= minSup}
    freqItemSet = set(headerTable.keys()) # {'l1', 'l2', 'l3', 'l4', 'l5'}

    # 如果没有元素项满足要求，则退出
    if len(freqItemSet) == 0:
        return None, None

    for k in headerTable:
        headerTable[k] = [headerTable[k], None] # 初始化headerTable

    '''第二次扫描数据集'''
    # 创建树
    retTree = treeNode('Null Set', 1, None)

    for tranSet, count in initSet.items():
        localD = {}
        for item in tranSet:
            if item in freqItemSet:
                localD[item] = headerTable[item][0] # {'l3': 6, 'l2': 7, 'l1': 6}

        # 3、按降序重新排列
        if len(localD) > 0:
            orderedItems = [v[0] for v in sorted(localD.items(), key=lambda  p: p[1], reverse=True)] # ['l2', 'l3', 'l1']
            updateTree(orderedItems, retTree, headerTable, count)

    return retTree, headerTable

def updateTree(items, inTree, headerTable, count):
    # 检查第一个元素项是否作为子节点存在
    if items[0] in inTree.children:
        # 存在，更新计数
        inTree.children[items[0]].inc(count)
    else:
        # 不存在，创建一个新的treeNode
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        if headerTable[items[0]][1] == None:
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])

    # 不断迭代调用自身，每次调用都会删掉列表中的第一个元素
    if len(items) > 1:
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)

def updateHeader(nodeToTest, targetNode):
    # 更新头指针表，确保节点链接指向树中该元素项的每一个实例
    while nodeToTest.nodeLink != None:
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode


"""
    3、抽取条件模式基
"""
# 迭代上溯整棵树
def ascendTree(leafNode, prefixPath):
    if leafNode.parent != None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)

def findPrefixPath(basePat, treeNode):
    condPats = {}
    while treeNode != None:
        prefixPath = []
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1:
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        treeNode = treeNode.nodeLink
    return condPats

"""
    4、递归寻找频繁项集
"""
def mineTree(inTree, headerTable, minSup, preFix, freqItemList):
    # 排序头指针表：升序
    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p: p[1][0])] # ['l5', 'l4', 'l1', 'l3', 'l2']

    # 从头指针的底端开始
    for basePat in bigL:
        newFreqSet = preFix.copy()
        newFreqSet.add(basePat)
        print('finalFrequent Item: ', newFreqSet)
        freqItemList.append(newFreqSet)
        condPattBases = findPrefixPath(basePat, headerTable[basePat][1])
        print('condPattBases :', basePat, condPattBases)

        # 从条件模式基创建条件FP树
        myCondTree, myHead = createTree(condPattBases, minSup)
        # print('head from conditional tree: ', myHead)

        # 挖掘条件FP树
        if myHead != None:
            print('conditional tree for: ', newFreqSet)
            myCondTree.disp(1)
            mineTree(myCondTree, myHead, minSup, newFreqSet, freqItemList)


"""
    5、数据集
"""
def loadSimpDat():
    simpDat = [
        ['I1', 'I2', 'I5'],
        ['I2', 'I4'],
        ['I2', 'I3'],
        ['I1', 'I2', 'I4'],
        ['I1', 'I3'],
        ['I2', 'I3'],
        ['I1', 'I3'],
        ['I1', 'I2', 'I3', 'I5'],
        ['I1', 'I2', 'I3']
    ]
    return simpDat

def createInitSet(dataSet):
    retDict = {}
    for trans in dataSet:
        # 若有相同的trans，则+1；否则，则为1
        retDict[frozenset(trans)] = retDict.get(frozenset(trans), 0) + 1
    return retDict


if __name__ == '__main__':
    minSup = 2
    simpDat = loadSimpDat()
    initSet = createInitSet(simpDat)
    myFPtree, myHeaderTab = createTree(initSet, minSup)
    myFPtree.disp()
    myFreqList = []
    mineTree(myFPtree, myHeaderTab, minSup, set([]), myFreqList)
            
