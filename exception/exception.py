from pkg.gcp.gcp import REGIONS


class GcpRegionNotFound(Exception):
    def __init__(self,region ,message="not a valid region. try the following " + ", ".join(REGIONS)) -> None:
        self.message = message
        self.region = region
        super().__init__(self.message)
    pass