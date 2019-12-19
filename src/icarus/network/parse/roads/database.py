
from  icarus.util.database import DatabaseUtil

class RoadParserDatabase(DatabaseUtil):
    def write_nodes(self, nodes):
        self.write_geom_rows(nodes, 'nodes', geo=1)
    
    def write_links(self, links):
        self.write_rows(links, 'links')