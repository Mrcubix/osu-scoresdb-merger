import osudb

def Merge_scores(base, update):
    scDB_Base = osudb.parse_score(base)
    scDB_Update = osudb.parse_score(update)
    for map_u in scDB_Update[2]:
        for idx, map_b in enumerate(scDB_Base[2]):
            if map_u[0] in map_b:
                for scores_u in map_u[2]:
                    if not scores_u in map_b[2]:
                        scDB_Base[2][idx][2].append(scores_u)
                        scDB_Base[2][idx][1] += 1
                        print("Added: "+str(scores_u)+" Type: Scores")
    listmap = []
    [listmap.append(map_b[0]) for map_b in scDB_Base[2]]
    for map_u in scDB_Update[2]:
        if not map_u[0] in listmap:
            scDB_Base[2].append(map_u)
            scDB_Base[1] += 1
            print("Added: "+str(map_u[0])+" Type: Maps")
    return scDB_Base

