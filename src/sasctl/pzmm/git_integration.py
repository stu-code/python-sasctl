# Copyright (c) 2022, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import io
import zipfile
from pathlib import Path
from typing import Optional, Union
from uuid import UUID
from warnings import warn

from .._services.model_repository import ModelRepository as mr
from ..core import is_uuid, RestObj

try:
    import git
    from git import Repo
except ImportError:
    git = None
    Repo = None


def check_git_status() -> None:
    """
    Check to see if GitPython has been installed and if a valid git executable
    exists on the target system. If one of those two conditions is not met, then
    a RunTime error is raised.

    Raises
    ------
    RuntimeError
        Raised if an invalid git setup for git integration is detected.
    """
    if git is None:
        raise RuntimeError(
            "The 'GitPython' package and a valid git executable are required"
            + " for use of the git integration functions."
        )


def get_zipped_model(
    model: Union[str, RestObj],
    git_path: Union[str, Path],
    project: Optional[Union[str, RestObj]] = None,
) -> (str, str):
    """
    Retrieve a zipped file containing all the model contents of a specified
    model.

    The project argument is only needed if the model argument is not a valid
    UUID or RestObj.

    Parameters
    ----------
    model : str or RestObj
        Model name, UUID, or RestObj which identifies the model. If only the model name
        is provided, the project name must also be supplied.
    git_path : str or pathlib.Path
        Base directory of the git repository.
    project : str or RestObj, optional
        Project identifier, which is required when only the model name is supplied.
        Default is None.

    Returns
    -------
    model_name : str
        Name of the model retrieved from SAS Model Manager.
    project_name : str
        Name of the project the model was retrieved from in SAS Model Manager.
    """
    # Find the specified model and pull down the contents in a zip format
    if isinstance(model, RestObj):
        model = mr.get_model(model)
    elif is_uuid(model):
        model = mr.get_model(model)
    else:
        if not project:
            raise ValueError(
                "The model cannot be determined accurately from just the model name. "
                "Please provide either the model UUID or the project name."
            )
        else:
            project = mr.get_project(project)
        model = mr.list_models(
            filter=f"and(eq(projectName,'{project.name}'),eq(name,'{model}'))"
        )[0]
    params = {"format": "zip"}
    model_zip = mr.get(f"models/{model.id}", params=params, format_="content")
    model_name = model.name
    project_name = model.projectName

    # Check to see if project folder exists
    if (Path(git_path) / project_name).exists():
        # Check to see if model folder exists
        if (Path(git_path) / project_name / model_name).exists():
            with open(
                Path(git_path) / project_name / model_name / (model_name + ".zip"), "wb"
            ) as zip_file:
                zip_file.write(model_zip)
        else:
            new_dir = Path(git_path) / project_name / model_name
            new_dir.mkdir(parents=True, exist_ok=True)
            with open(
                Path(git_path) / project_name / model_name / (model_name + ".zip"), "wb"
            ) as zip_file:
                zip_file.write(model_zip)
    else:
        new_dir = Path(git_path) / project_name
        new_dir.mkdir(parents=True, exist_ok=True)
        new_dir = Path(git_path) / project_name / model_name
        new_dir.mkdir(parents=True, exist_ok=True)
        with open(
            Path(git_path) / f"{project_name}/{model_name}/{model_name}.zip",
            "wb",
        ) as zip_file:
            zip_file.write(model_zip)

    return model_name, project_name


def project_exists(response, project):
    """
    Checks if project exists on SAS Viya. If the project does not exist, then a new
    project is created or an error is raised.

    Parameters
    ----------
    response : RestObj
        JSON response of the get_project() call to model repository service.
    project : string or RestObj
        The name or id of the model project, or a RestObj representation of the project.

    Returns
    -------
    response : RestObj
        JSON response of the get_project() call to model repository service.

    Raises
    ------
    SystemError
        Alerts user that API calls cannot continue until a valid project is provided.
    """
    if response is None:
        try:
            warn(f"No project with the name or UUID {project} was found.")
            UUID(project)
            raise SystemError(
                "The provided UUID does not match any projects found in SAS Model "
                "Manager. Please enter a valid UUID or a new name for a project to be "
                "created."
            )
        except ValueError:
            repo = mr.default_repository().get("id")
            response = mr.create_project(project, repo)
            print(f"A new project named {response.name} was created.")
            return response
    else:
        return response


def model_exists(project, name, force):
    """Checks if model already exists and either raises an error or deletes the redundant model.

    Parameters
    ----------
    project : str or dict
        The name or id of the model project, or a dictionary representation of the project.
    name : str or dict
        The name of the model.
    force : bool, optional
        Sets whether to overwrite models with the same name upon upload.

    Raises
    ------
    ValueError
        Model repository API cannot overwrite an already existing model with the upload model call.
        Alerts user of the force argument to allow multi-call API overwriting.
    """
    project = mr.get_project(project)
    project_id = project["id"]
    project_models = mr.get(f"/projects/{project_id}/models")

    for model in project_models:
        # Throws a TypeError if only one model is in the project
        try:
            if model["name"] == name:
                if force:
                    mr.delete_model(model.id)
                else:
                    raise ValueError(
                        f"A model with the same model name exists in project "
                        f"{project.name}. Include the force=True argument to overwrite "
                        f"models with the same name."
                    )
        except TypeError:
            if project_models["name"] == name:
                if force:
                    mr.delete_model(project_models.id)
                else:
                    raise ValueError(
                        f"A model with the same model name exists in project "
                        f"{project.name}. Include the force=True argument to overwrite "
                        f"models with the same name."
                    )


class GitIntegrate:
    @classmethod
    def pull_viya_model(
        cls,
        model,
        git_path,
        project=None,
    ):
        """Send an API request in order to pull a model from a project in
        SAS Model Manager in a zipped format. The contents of the zip file
        include all files found in SAS Model Manager's model UI, except that
        read-only json files are updated to match the current state of the model.

        After pulling down the zipped model, unpack the file in the model folder.
        Overwrites files with the same name.

        If supplying a model name instead of model UUID, a project name or uuid must
        be supplied as well. Models in the model repository are allowed duplicate
        names, therefore we need a method of parsing the returned models.

        Parameters
        ----------
        model : str or RestObj
            A string or JSON response representing the model to be pulled down
        git_path : str or pathlib.Path
            Base directory of the git repository.
        project : str or RestObj, optional
            A string or JSON response representing the project the model exists in, default is None.
        """
        # Try to pull down the model assuming a UUID or RestObj is provided
        try:
            if isinstance(model, RestObj):
                model = model.id
            else:
                UUID(model)
            project_name = mr.get_model(model).projectName
            model_name, project_name = get_zipped_model(model, git_path, project_name)
        # If a name is provided instead, use the provided project name or UUID to find
        # the correct model
        except ValueError:
            project_response = mr.get_project(project)
            if project_response is None:
                raise SystemError(
                    "For models with only a provided name, a project name or UUID must "
                    "also be supplied."
                )
            project_name = project_response["name"]
            project_id = project_response["id"]
            project_models = mr.get(f"/projects/{project_id}/models")
            for model in project_models:
                # Throws a TypeError if only one model is in the project
                try:
                    if model["name"] == model:
                        model_id = model.id
                        model_name, project_name = get_zipped_model(
                            model_id, git_path, project_name
                        )
                except TypeError:
                    if project_models["name"] == model:
                        model_id = project_models.id
                        model_name, project_name = get_zipped_model(
                            model_id, git_path, project_name
                        )

        # Unpack the pulled down zip model and overwrite any duplicate files
        model_path = Path(git_path) / f"{project_name}/{model_name}"
        with zipfile.ZipFile(
            str(model_path / (model_name + ".zip")), mode="r"
        ) as zFile:
            zFile.extractall(str(model_path))

        # Delete the zip model objects in the directory to minimize confusion when
        # uploading back to SAS Model Manager
        for zip_file in model_path.glob("*.zip"):
            zip_file.unlink()

    @classmethod
    def push_git_model(
        cls, git_path, model_name=None, project_name=None, project_version="latest"
    ):
        """Push a single model in the git repository up to SAS Model Manager. This
        function creates an archive of all files in the directory and imports the zipped
        model.

        Parameters
        ----------
        git_path : str or pathlib.Path
            Base directory of the git repository or path which includes project and
            model directories.
        model_name : str, optional
            Name of model to be imported, by default None
        project_name : str, optional
            Name of project the model is imported from, by default None
        project_version : str, optional
            Name of project version to import model in to. Default
            value is "latest".
        """
        if model_name is None and project_name is None:
            model_dir = git_path
            model_name = model_dir.name
            project_name = model_dir.parent.name
        else:
            model_dir = Path(git_path) / (project_name + "/" + model_name)
        for zip_file in model_dir.glob("*.zip"):
            zip_file.unlink()
        file_names = []
        file_names.extend(sorted(Path(model_dir).glob("*")))
        with zipfile.ZipFile(
            str(model_dir / (model_dir.name + ".zip")), mode="w"
        ) as zFile:
            for file in file_names:
                zFile.write(str(file), arcname=file.name)
        with open(model_dir / (model_dir.name + ".zip"), "rb") as zFile:
            zip_io_file = io.BytesIO(zFile.read())
            # Check to see if provided project argument is a valid project on SAS Model
            # Manager
            project_response = mr.get_project(project_name)
            project = project_exists(project_response, project_name)
            project_name = project.name
            # Check if model with same name already exists in project. Delete if it
            # exists.
            model_exists(project_name, model_name, True)
            mr.import_model_from_zip(
                model_name, project_name, zip_io_file, version=project_version
            )

    @classmethod
    def git_repo_push(cls, git_path, commit_message, remote="origin", branch="main"):
        """Create a new commit with new files, then push changes from the local
        repository to a remote branch. The default remote branch is origin.

        Parameters
        ----------
        git_path : str or pathlib.Path
            Base directory of the git repository.
        commit_message : str
            Commit message for the new commit
        remote : str, optional
            Remote name for the remote repository, by default 'origin'
        branch : str
            Branch name for the target pull branch from remote, by default 'main'
        """
        check_git_status()

        repo = Repo(git_path)
        repo.git.add(all=True)
        repo.index.commit(commit_message)
        repo.git.push(remote, branch)

    @classmethod
    def git_repo_pull(cls, git_path, remote="origin", branch="main"):
        """Pull down any changes from a remote branch of the git repository. The default branch is
        origin.

        Parameters
        ----------
        git_path : str or pathlib.Path
            Base directory of the git repository.
        remote : str
            Remote name for the remote repository, by default 'origin'
        branch : str
            Branch name for the target pull branch from remote, by default 'main'
        """
        check_git_status()

        repo = git.Git(git_path)
        repo.pull(remote, branch)

    @classmethod
    def push_git_project(cls, git_path, project=None):
        """Using a user provided project name, search for the project in the specified
        git repository, check if the project already exists on SAS Model Manager (create
        a new project if it does not), then upload each model found in the git project
        to SAS Model Manager

        Parameters
        ----------
        git_path : str or pathlib.Path
            Base directory of the git repository or the project directory.
        project : str or RestObj
            Project name, UUID, or JSON response from SAS Model Manager.
        """
        # Check to see if provided project argument is a valid project on SAS Model
        # Manager
        project_response = mr.get_project(project)
        project = project_exists(project_response, project)
        project_name = project.name

        # Check if project exists in git path and produce an error if it does not
        project_path = Path(git_path) / project_name
        if project_path.exists():
            models = [x for x in project_path.glob("*") if x.is_dir()]
            if len(models) == 0:
                print(f"No models were found in project {project_name}.")
            print(f"{len(models)} models were found in project {project_name}.")
        else:
            raise FileNotFoundError(
                "No directory with the name {} was found in the specified git path.".format(
                    project
                )
            )

        # Loop through paths of models and upload each to SAS Model Manager
        for model in models:
            # Remove any extra zip objects in the directory
            for zip_file in model.glob("*.zip"):
                zip_file.unlink()
            cls.push_git_model(model)

    @classmethod
    def pull_mm_project(cls, git_path, project):
        """Following the user provided project argument, pull down all models from the
        corresponding SAS Model Manager project into the mapped git directories.

        Parameters
        ----------
        git_path : str or pathlib.Path
            Base directory of the git repository.
        project : str or RestObj
            The name or id of the model project, or a RestObj representation of the
            project.
        """
        # Check to see if provided project argument is a valid project on SAS Model
        # Manager
        project_response = mr.get_project(project)
        project = project_exists(project_response, project)
        project_name = project.name
        # Check if project exists in git path and create it if it does not
        project_path = Path(git_path) / project_name
        if not project_path.exists():
            Path(project_path).mkdir(parents=True, exist_ok=True)

        # Return a list of model names from SAS Model Manager project
        model_response = mr.get(f"projects/{project.id}/models")
        if not model_response:
            raise FileNotFoundError(
                "No models were found in the specified project. A new project folder "
                "has been created if it did not already exist within the git "
                "repository."
            )
        model_names = []
        model_id = []
        for model in model_response:
            model_names.append(model.name)
            model_id.append(model.id)
        # For each model, search for an appropriate model directory in the project
        # directory and pull down the model
        for name, m_id in zip(model_names, model_id):
            model_path = project_path / name
            # If the model directory does not exist, create one in the project directory
            if not model_path.exists():
                Path(model_path).mkdir(parents=True, exist_ok=True)
            cls.pull_viya_model(m_id, model_path.parents[1])
