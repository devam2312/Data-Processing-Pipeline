from neo4j import GraphDatabase

class Interface:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

    def bfs(self, start_node, last_node):
        # TODO: Implement this method
        with self._driver.session() as session:
            session.run("""CALL gds.graph.project('bfsGraph', 'Location', 'TRIP')""")
            bfsQuery = """
            MATCH (start:Location{name:$start_node}), (last:Location{name:$last_node})
            WITH id(start) AS source, id(last) AS targetNodes
            CALL gds.bfs.stream('bfsGraph', {
                sourceNode: source,
                targetNodes: targetNodes
                })
            YIELD path
            RETURN path
            """
            result = session.run(bfsQuery, start_node=start_node, last_node=last_node)
            session.run("CALL gds.graph.drop('bfsGraph')")
            return result.data()


    def pagerank(self, max_iterations, weight_property):
        # TODO: Implement this method
        q1 = f""" CALL gds.graph.project('pagerankGraph', 'Location', 'TRIP', {{relationshipProperties: '{weight_property}'}})"""
        q2 = f""" CALL gds.pageRank.stream('pagerankGraph', 
        {{maxIterations: {max_iterations}, dampingFactor: 0.85, relationshipWeightProperty: '{weight_property}'}})
        YIELD nodeId, score
        RETURN gds.util.asNode(nodeId).name as name, score
        ORDER BY score DESC"""

        with self._driver.session() as session:
            result = session.run("CALL gds.graph.drop('pagerankGraph', false) YIELD graphName;")
            result = session.run(q1)
            result = session.run(q2)
            records = list(result)
        return (records[0], records[-1])