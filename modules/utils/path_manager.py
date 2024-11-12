import os

def makeRelPath(pwd, folder):
        """
        Make a path to the folder relative to the base directory of the project

        Args:
                pwd (str): Present working directory
                folder (str): The name of the folder

        Returns:
                path (str): Relative path to the folder specified in the arguments
        """
        
        path = ""
        dirs = pwd.split("/")
        for directory in reversed(dirs):
                if (directory != "MLOps-1"):
                        path += "../"
                else:
                        break
        if (path != ""):
                path += f'{folder}/'
        else:
                path = f'./{folder}/'
        return path
