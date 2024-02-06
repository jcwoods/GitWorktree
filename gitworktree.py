import git
import os
import pathlib
import shutil
import sys
import tempfile

from time import sleep

class GitWorkTree(object):
    def __init__(self, barerepo:str):
        '''
        Create a worktree for the named bare git repo location.  Note that
        'barerepo' may be either a standard- or bare-cloned git repository.
        '''

        self.barerepo = barerepo
        self.tmpdir = None
        self.target = None
        self.repo = None
        return

    def __str__(self):
        return str(self.target)

    def create(self, target:str=None, branch:str=None):
        '''
        Create the worktree at the (optionally) designated location.

        If target is given, the designated path will be used.  If the path
        does not exist, it will be created (recursively if necessary).  If
        target is not given, a temporary directory will be created.
        
        If branch is given, the selected branch will be checked out in the
        target directory.  If branch is not given, the default branch will
        be selected.
        '''

        if target is None:
            # if target is not set, we'll create a temporary directory
            self.tmpdir = tempfile.TemporaryDirectory()
            target = self.tmpdir.name
        else:
            # create the directory if required
            self.tmpdir = None
            pathlib.Path(target).mkdir(parents=True, exist_ok=False)

        self.target = target
        self.repo = git.Repo(self.barerepo)
        self.repo.git.worktree("add", self.target, branch)

        return self.target

    def cleanup(self):
        '''
        Clean up the worktree and any associated target location.
        '''

        if self.target and os.path.isdir(self.target):
            # remove the worktree
            if self.repo is not None:
                self.repo.git.worktree("remove", self.target)
                self.repo = None

            # cleanup the directory
            if self.tmpdir is not None:
                self.tmpdir.cleanup()
                self.tmpdir = None
            else:
                shutil.rmtree(self.target)

        return

    def __enter__(self):
        return self.create()

    def __exit__(self, *args):
        return self.cleanup()


def main(argv):
    '''
    A test routine.  Creates a worktree from the named repository.  Once the
    worktree is created, list the files in the directory.
    '''

    try:
        path = argv[1]
    except IndexError:
        path = "datarake.git"

    with GitWorkTree(path) as gwt:
        for dirpath, _, filenames in os.walk(gwt):
            for f in filenames:
                print(os.path.join(dirpath, f))
        
        sleep(15)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
