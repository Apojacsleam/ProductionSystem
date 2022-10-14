from networkx import MultiDiGraph, all_neighbors
from Database import Query, Get_Name


def Get_Konwledge_Network():
    Graph = MultiDiGraph()
    NodeFeature = list(Query('''SELECT FeatureNo FROM Feature''')['FeatureNo'])
    NodeIndividual = list(Query('''SELECT IndividualNo FROM Individual''')['IndividualNo'])
    Graph.add_nodes_from(NodeFeature)
    Graph.add_nodes_from(NodeIndividual)
    RuleData = Query('''SELECT * FROM Rule''')
    for i in range(len(RuleData)):
        Condition_list = RuleData['Condition'][i].split('&')
        for Condition in Condition_list:
            Graph.add_edges_from([(Condition, RuleData['Result'][i], {'Rule': RuleData['RuleNo'][i]})])
    return Graph


def Get_All_PointNode(Node, KnowledgeNetwork):
    Resultset = set()
    Nowset = set()
    Nowset.add(Node)
    while len(Nowset):
        NowList = list(Nowset)
        Nowset.clear()
        for node in NowList:
            Nowneighbor = list(KnowledgeNetwork.neighbors(node))
            for neighbor in Nowneighbor:
                Nowset.add(neighbor)
        Resultset = Resultset | Nowset
    Returnset = set()
    Pointset = set()
    Pointset.add(Node)
    for result in Resultset:
        if result[0] == 'I':
            Returnset.add(result)
        else:
            Pointset.add(result)
    return (Returnset, Pointset)


def Inference(ConditionList, KnowledgeNetwork):
    Result, Point = Get_All_PointNode(ConditionList[0], KnowledgeNetwork)
    for i in range(1, len(ConditionList)):
        ResultSet, PointSet = Get_All_PointNode(ConditionList[i], KnowledgeNetwork)
        Result = Result & ResultSet
        Point = Point | PointSet
    return (Result, Point)


def Inference_Result(ConditionList, KonwledgeNetwork):
    if len(ConditionList) == 0:
        return ['请向综合数据库中添加事实！']
    else:
        Result, Point = Inference(ConditionList, KonwledgeNetwork)
        Result = list(Result)
        Result.sort()
        ResultList = [Get_Name('Individual', x) for x in Result]
        strList = ['-----开始推理-----', '本次采用正向推理方法', '推理中...', '-----推理结束-----']
        if len(ResultList) == 0:
            strList.append('您所提供的事实与规则矛盾，不能推理出任一有效结果，请重新设置综合数据库！')
        elif len(ResultList) == 1:
            Neighbors = list(all_neighbors(KonwledgeNetwork, Result[0]))
            MissingCondition = []
            for neighbor in Neighbors:
                if neighbor not in Point:
                    MissingCondition.append(Get_Name('Feature', neighbor))
            if len(MissingCondition) == 0:
                strList.append('根据您所提供的事实，可以推理出唯一有效结果！')
                strList.append('您所推理的结果为：' + ResultList[0])
            else:
                strList.append('根据您所提供的事实，可以推理出一种可能结果！')
                strList.append('可能的结果为：' + ResultList[0])
                strList.append('但仍缺少条件：' + '、'.join(MissingCondition))
                strList.append('请向综合数据库中添加条件或新添加规则！')
        else:
            strList.append('根据您所提供的事实，可以推理出多种可能结果！')
            strList.append('可能的结果有：' + '、'.join(ResultList))
            minNeighbor = len(list(all_neighbors(KonwledgeNetwork, Result[0])))
            Best = ResultList[0]
            for i in range(1, len(Result)):
                Neighbornum = len(list(all_neighbors(KonwledgeNetwork, Result[i])))
                if Neighbornum < minNeighbor:
                    minNeighbor = Neighbornum
                    Best = ResultList[i]
            strList.append('其中，最可能的结果是：' + Best)
        return strList