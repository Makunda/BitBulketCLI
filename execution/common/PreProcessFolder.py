import glob

from logger.Logger import Logger
from services.FileService import FileService
from services.HighlightService import HighlightService
from services.ZipService import ZipService
from utils.FolderUtils import FolderUtils
from utils.PathUtils import PathUtils
from utils.config.ExclusionConfig import ExclusionConfig


class PreProcessFolder:
    """
    The PreProcessFolder class is launch the actions related to the pre processing of the data
    Pre-process the files in the destination folder
        - Flag the empty folders
        - Remove the files with the size of 0
        - Remove the files matching the exclusions patterns
        - Reassign the files with a path that is too long
        - Extract the list of file extensions found in the application and assign them to the categories
    """

    def __init__(self, path_to_analyze: str):
        self._logger = Logger.get_logger("Pre Proc. Folder")
        self._exclusionConfig = ExclusionConfig()
        self._zip_service = ZipService()

        self._success_files = []
        self._failed_files = []
        self._extension_list = []

        self._path_to_analyze = path_to_analyze

    def __unzip_subfolders(self) -> (int, int):
        """
        Unzip the subfolders of a folder
        :param folder: Folder to process
        :return: None
        """
        self._logger.info("Unzip the subfolders of the folder: " + self._path_to_analyze)
        it = 0
        errors = 0

        # Unzip the files inside, and delete the previous nested zip file
        items = glob.glob(self._path_to_analyze, recursive=True)
        for item in items:
            try:
                if PathUtils.isfile(item) and item.endswith(".zip"):
                    self._zip_service.unzip_file(item, self._path_to_analyze)
                    FolderUtils.remove_file(item)
                    it += 1
            except Exception as e:
                self._logger.error("Failed to unzip the file: " + item)
                errors += 1

        self._logger.info("Unzipped " + str(it) + " files")
        return it, errors

    def __remove_empties(self) -> (int, int, int):
        """
        Remove the empty files and folders
        :return: The number of files and folders removed, and the number of errors
        """
        self._logger.info("Remove the empty files and folders")
        it_files = 0
        it_folders = 0
        errors = 0

        # Remove the empty files
        for root, dirs, files in PathUtils.walk(self._path_to_analyze):
            for file in files:
                file_path = PathUtils.join_path(root, file)
                try:
                    if PathUtils.is_empty(file_path):
                        FolderUtils.remove_file(file_path)
                        it_files += 1
                except Exception as e:
                    self._logger.error("Failed to remove the file: " + file_path)
                    errors += 1

            # Remove the empty folders
            for direct in dirs:
                dir_path = PathUtils.join_path(root, direct)
                try:
                    if PathUtils.is_empty(dir_path):
                        FolderUtils.remove_folder(dir_path)
                        it_folders += 1

                except Exception as e:
                    self._logger.error("Failed to remove the folder: " + dir_path)
                    errors += 1

        self._logger.info("Removed " + str(it_files) + " empty files")
        self._logger.info("Removed " + str(it_folders) + " empty folders")

    def __remove_exclusions(self) -> (int, int, int):
        """
        Remove the files matching the exclusions patterns
        :return: The number of files and folders removed, and the number of errors
        """
        self._logger.info("Remove the files matching the exclusions patterns")
        it_files = 0
        it_folders = 0
        errors = 0

        # Remove the exclusions
        for root, dirs, files in PathUtils.walk(self._path_to_analyze):
            for file in files:
                file_path = PathUtils.join_path(root, file)
                try:
                    if self._exclusionConfig.is_excluded(file_path):
                        FolderUtils.remove_file(file_path)
                        it_files += 1
                except Exception as e:
                    self._logger.error("Error removing the file: " + file_path)
                    errors += 1

            for direct in dirs:
                dir_path = PathUtils.join_path(root, direct)
                try:
                    if self._exclusionConfig.is_excluded(dir_path):
                        FolderUtils.remove_folder(dir_path)
                        it_folders += 1
                except Exception as e:
                    self._logger.error("Error removing the folder: " + dir_path)
                    errors += 1

        self._logger.info("Removed " + str(it_files) + " files matching the exclusions patterns")
        self._logger.info("Removed " + str(it_folders) + " folders matching the exclusions patterns")

    def __reassign_long_paths(self) -> None:
        """
        Reassign the files with a path that is too long
        :return: None
        """
        self._logger.info("Reassign the files with a path that is too long")
        it_files = 0

        # Reassign the files with a path that is too long
        for root, dirs, files in PathUtils.walk(self._path_to_analyze):
            for file in files:
                file_path = PathUtils.join_path(root, file)

                try:
                    new_path = FolderUtils.shorten_path(file_path)
                    if new_path != file_path:
                        it_files += 1
                except Exception as e:
                    self._logger.error("Error reassigning the path of the file: " + file_path)

        self._logger.info("Reassigned " + str(it_files) + " files with a path that is too long")


    def launch(self) -> None:
        """
        Launch the pre-processing of the data
        :return: None
        """
        self._logger.info("Launch the pre processing of the data")
        self._logger.info("Unzip the sub-folders of the folder.")
        self.__unzip_subfolders()

        self._logger.info("Remove the empty files and folders")
        self.__remove_empties()

        self._logger.info("Remove the files matching the exclusions patterns")
        self.__remove_exclusions()

        self._logger.info("Reassign the files with a path that is too long")
        self.__reassign_long_paths()

        self._logger.info("Pre-processing of the data completed")