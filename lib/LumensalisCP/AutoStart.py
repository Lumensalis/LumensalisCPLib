from LumensalisCP.common import *
from LumensalisCP.Main.Manager import MainManager


def autoStart(**kwds ):
    main = MainManager.initOrGetManager(**kwds)
    project = main.identity.project
    if project is not None:
        main = "demoMain" if project.find("Demos") >= 0 else "main"
        print( f"autoStart project {project}..." )
        execSource = f"""
from {project} import *
{main}()
"""
        exec(execSource)
