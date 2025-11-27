from gitara.renderer import render_git_command


def test_git_status():
    assert render_git_command({"name": "git_status", "arguments": {}}) == "git status"
    assert render_git_command({"name": "git_status", "arguments": {"verbose": False}}) == "git status"
    assert render_git_command({"name": "git_status", "arguments": {"verbose": True}}) == "git status --verbose"
    assert render_git_command({"name": "git_status", "arguments": {"ignored": True}}) == "git status --ignored"
    assert (
        render_git_command({"name": "git_status", "arguments": {"verbose": True, "ignored": True}})
        == "git status --verbose --ignored"
    )


def test_git_add():
    assert render_git_command({"name": "git_add", "arguments": {}}) == "git add ."
    assert render_git_command({"name": "git_add", "arguments": {"files": []}}) == "git add ."
    assert render_git_command({"name": "git_add", "arguments": {"files": ["."]}}) == "git add ."
    assert render_git_command({"name": "git_add", "arguments": {"files": ["file.txt"]}}) == "git add file.txt"
    assert (
        render_git_command({"name": "git_add", "arguments": {"files": ["file1.txt", "file2.txt"]}})
        == "git add file1.txt file2.txt"
    )


def test_git_commit():
    assert render_git_command({"name": "git_commit", "arguments": {}}) == "# Error: message is required"
    assert render_git_command({"name": "git_commit", "arguments": {"message": "test"}}) == 'git commit -m "test"'
    assert (
        render_git_command({"name": "git_commit", "arguments": {"message": "test", "amend": False}})
        == 'git commit -m "test"'
    )
    assert render_git_command({"name": "git_commit", "arguments": {"amend": True}}) == "git commit --amend"
    assert (
        render_git_command({"name": "git_commit", "arguments": {"message": "test", "amend": True}})
        == 'git commit --amend -m "test"'
    )


def test_git_push():
    assert render_git_command({"name": "git_push", "arguments": {}}) == "git push"
    assert render_git_command({"name": "git_push", "arguments": {"remote": "some_origin"}}) == "git push some_origin"
    assert (
        render_git_command({"name": "git_push", "arguments": {"branch": "branch_name"}})
        == "git push origin branch_name"
    )
    assert render_git_command({"name": "git_push", "arguments": {"force": True}}) == "git push --force"
    assert render_git_command({"name": "git_push", "arguments": {"set_upstream": True}}) == "git push --set-upstream"
    assert (
        render_git_command(
            {
                "name": "git_push",
                "arguments": {
                    "remote": "origin",
                    "branch": "main",
                    "force": True,
                    "set_upstream": True,
                },
            }
        )
        == "git push origin main --force --set-upstream"
    )


def test_git_pull():
    assert render_git_command({"name": "git_pull", "arguments": {}}) == "git pull"
    assert render_git_command({"name": "git_pull", "arguments": {"remote": "origin"}}) == "git pull origin"
    assert render_git_command({"name": "git_pull", "arguments": {"branch": "main"}}) == "git pull origin main"
    assert (
        render_git_command(
            {
                "name": "git_pull",
                "arguments": {"remote": "some_origin", "branch": "some_branch"},
            }
        )
        == "git pull some_origin some_branch"
    )
    assert render_git_command({"name": "git_pull", "arguments": {"rebase": True}}) == "git pull --rebase"
    assert render_git_command({"name": "git_pull", "arguments": {"rebase": False}}) == "git pull"
    assert (
        render_git_command(
            {
                "name": "git_pull",
                "arguments": {
                    "remote": "upstream",
                    "branch": "develop",
                    "rebase": True,
                },
            }
        )
        == "git pull upstream develop --rebase"
    )


def test_git_branch():
    assert render_git_command({"name": "git_branch", "arguments": {}}) == "git branch"
    assert render_git_command({"name": "git_branch", "arguments": {"action": "list"}}) == "git branch"
    assert (
        render_git_command({"name": "git_branch", "arguments": {"action": "list", "all": True}}) == "git branch --all"
    )
    assert render_git_command({"name": "git_branch", "arguments": {"action": "list", "all": False}}) == "git branch"
    assert (
        render_git_command(
            {
                "name": "git_branch",
                "arguments": {"action": "delete", "branch_name": "feature"},
            }
        )
        == "git branch -d feature"
    )
    assert (
        render_git_command(
            {
                "name": "git_branch",
                "arguments": {
                    "action": "delete",
                    "branch_name": "feature",
                    "force": True,
                },
            }
        )
        == "git branch -D feature"
    )
    assert (
        render_git_command(
            {
                "name": "git_branch",
                "arguments": {
                    "action": "delete",
                    "branch_name": "feature",
                    "force": False,
                },
            }
        )
        == "git branch -d feature"
    )
    assert (
        render_git_command({"name": "git_branch", "arguments": {"action": "delete"}})
        == "# Error: branch name is required"
    )


def test_git_switch():
    assert render_git_command({"name": "git_switch", "arguments": {}}) == "git switch"
    assert render_git_command({"name": "git_switch", "arguments": {"branch": "main"}}) == "git switch main"
    assert (
        render_git_command({"name": "git_switch", "arguments": {"branch": "feature", "create": True}})
        == "git switch -c feature"
    )
    assert (
        render_git_command({"name": "git_switch", "arguments": {"branch": "feature", "create": False}})
        == "git switch feature"
    )
    assert render_git_command({"name": "git_switch", "arguments": {"detach": True}}) == "git switch --detach"
    assert (
        render_git_command({"name": "git_switch", "arguments": {"branch": "main", "detach": True}})
        == "git switch --detach main"
    )


def test_git_restore():
    assert render_git_command({"name": "git_restore", "arguments": {"files": ["file.txt"]}}) == "git restore file.txt"
    assert (
        render_git_command({"name": "git_restore", "arguments": {"files": ["file1.txt", "file2.txt"]}})
        == "git restore file1.txt file2.txt"
    )
    assert render_git_command({"name": "git_restore", "arguments": {"files": ["."]}}) == "git restore ."
    assert (
        render_git_command(
            {
                "name": "git_restore",
                "arguments": {"files": ["file.txt"], "source": "HEAD"},
            }
        )
        == "git restore --source=HEAD file.txt"
    )
    assert (
        render_git_command(
            {
                "name": "git_restore",
                "arguments": {"files": ["file.txt"], "source": "HEAD~1"},
            }
        )
        == "git restore --source=HEAD~1 file.txt"
    )
    assert (
        render_git_command(
            {
                "name": "git_restore",
                "arguments": {"files": ["file.txt"], "restore_target": "worktree"},
            }
        )
        == "git restore file.txt"
    )
    assert (
        render_git_command(
            {
                "name": "git_restore",
                "arguments": {"files": ["file.txt"], "restore_target": "staged"},
            }
        )
        == "git restore --staged file.txt"
    )
    assert (
        render_git_command(
            {
                "name": "git_restore",
                "arguments": {"files": ["file.txt"], "restore_target": "both"},
            }
        )
        == "git restore --staged --worktree file.txt"
    )
    assert (
        render_git_command(
            {
                "name": "git_restore",
                "arguments": {
                    "files": ["file.txt"],
                    "source": "main",
                    "restore_target": "staged",
                },
            }
        )
        == "git restore --source=main --staged file.txt"
    )


def test_git_merge():
    assert render_git_command({"name": "git_merge", "arguments": {"branch": "feature"}}) == "git merge feature"
    assert render_git_command({"name": "git_merge", "arguments": {"branch": "develop"}}) == "git merge develop"
    assert (
        render_git_command({"name": "git_merge", "arguments": {"branch": "feature", "no_ff": True}})
        == "git merge feature --no-ff"
    )
    assert (
        render_git_command({"name": "git_merge", "arguments": {"branch": "feature", "no_ff": False}})
        == "git merge feature"
    )
    assert (
        render_git_command({"name": "git_merge", "arguments": {"branch": "feature", "ff_only": True}})
        == "git merge feature --ff-only"
    )
    assert (
        render_git_command({"name": "git_merge", "arguments": {"branch": "feature", "ff_only": False}})
        == "git merge feature"
    )
    assert (
        render_git_command(
            {
                "name": "git_merge",
                "arguments": {"branch": "feature", "strategy": "recursive"},
            }
        )
        == "git merge feature"
    )
    assert (
        render_git_command(
            {
                "name": "git_merge",
                "arguments": {"branch": "feature", "strategy": "resolve"},
            }
        )
        == "git merge feature --strategy=resolve"
    )
    assert (
        render_git_command(
            {
                "name": "git_merge",
                "arguments": {"branch": "feature", "strategy": "ours"},
            }
        )
        == "git merge feature --strategy=ours"
    )
    assert (
        render_git_command(
            {
                "name": "git_merge",
                "arguments": {"branch": "feature", "strategy": "subtree"},
            }
        )
        == "git merge feature --strategy=subtree"
    )
    assert (
        render_git_command(
            {
                "name": "git_merge",
                "arguments": {"branch": "feature", "no_ff": True, "strategy": "ours"},
            }
        )
        == "git merge feature --no-ff --strategy=ours"
    )


def test_git_stash():
    assert render_git_command({"name": "git_stash", "arguments": {"action": "save"}}) == "git stash save"

    assert (
        render_git_command(
            {
                "name": "git_stash",
                "arguments": {"action": "save", "message": "WIP changes"},
            }
        )
        == 'git stash save -m "WIP changes"'
    )
    assert (
        render_git_command(
            {
                "name": "git_stash",
                "arguments": {"action": "save", "include_untracked": True},
            }
        )
        == "git stash save --include-untracked"
    )
    assert (
        render_git_command(
            {
                "name": "git_stash",
                "arguments": {"action": "save", "include_untracked": False},
            }
        )
        == "git stash save"
    )
    assert (
        render_git_command(
            {
                "name": "git_stash",
                "arguments": {
                    "action": "save",
                    "message": "WIP",
                    "include_untracked": True,
                },
            }
        )
        == 'git stash save -m "WIP" --include-untracked'
    )
    assert render_git_command({"name": "git_stash", "arguments": {"action": "pop"}}) == "git stash pop"
    assert (
        render_git_command(
            {
                "name": "git_stash",
                "arguments": {"action": "pop", "stash_ref": "stash@{0}"},
            }
        )
        == "git stash pop stash@{0}"
    )
    assert (
        render_git_command(
            {
                "name": "git_stash",
                "arguments": {"action": "pop", "stash_ref": "stash@{2}"},
            }
        )
        == "git stash pop stash@{2}"
    )
    assert render_git_command({"name": "git_stash", "arguments": {"action": "apply"}}) == "git stash apply"
    assert (
        render_git_command(
            {
                "name": "git_stash",
                "arguments": {"action": "apply", "stash_ref": "stash@{1}"},
            }
        )
        == "git stash apply stash@{1}"
    )
    assert render_git_command({"name": "git_stash", "arguments": {"action": "list"}}) == "git stash list"
    assert render_git_command({"name": "git_stash", "arguments": {"action": "drop"}}) == "git stash drop"
    assert (
        render_git_command(
            {
                "name": "git_stash",
                "arguments": {"action": "drop", "stash_ref": "stash@{1}"},
            }
        )
        == "git stash drop stash@{1}"
    )
    assert render_git_command({"name": "git_stash", "arguments": {"action": "clear"}}) == "git stash clear"
    assert render_git_command({"name": "git_stash", "arguments": {"action": "show"}}) == "git stash show"
    assert (
        render_git_command({"name": "git_stash", "arguments": {"action": "show", "patch": True}})
        == "git stash show --patch"
    )
    assert (
        render_git_command(
            {
                "name": "git_stash",
                "arguments": {"action": "show", "stash_ref": "stash@{2}"},
            }
        )
        == "git stash show stash@{2}"
    )
    assert (
        render_git_command(
            {
                "name": "git_stash",
                "arguments": {
                    "action": "show",
                    "stash_ref": "stash@{1}",
                    "patch": True,
                },
            }
        )
        == "git stash show --patch stash@{1}"
    )


def test_git_rebase():
    assert render_git_command({"name": "git_rebase", "arguments": {"target": "main"}}) == "git rebase main"
    assert render_git_command({"name": "git_rebase", "arguments": {"target": "develop"}}) == "git rebase develop"
    assert (
        render_git_command({"name": "git_rebase", "arguments": {"target": "origin/main"}}) == "git rebase origin/main"
    )
    assert render_git_command({"name": "git_rebase", "arguments": {"continue": True}}) == "git rebase --continue"
    assert render_git_command({"name": "git_rebase", "arguments": {"abort": True}}) == "git rebase --abort"
    assert render_git_command({"name": "git_rebase", "arguments": {"continue": False}}) == "git rebase"
    assert render_git_command({"name": "git_rebase", "arguments": {"abort": False}}) == "git rebase"
    assert (
        render_git_command({"name": "git_rebase", "arguments": {"target": "main", "continue": True}})
        == "git rebase --continue"
    )
    assert (
        render_git_command({"name": "git_rebase", "arguments": {"target": "main", "abort": True}})
        == "git rebase --abort"
    )


def test_git_reset():
    assert render_git_command({"name": "git_reset", "arguments": {"mode": "soft"}}) == "git reset --soft"
    assert render_git_command({"name": "git_reset", "arguments": {"mode": "mixed"}}) == "git reset --mixed"
    assert render_git_command({"name": "git_reset", "arguments": {"mode": "hard"}}) == "git reset --hard"
    assert (
        render_git_command({"name": "git_reset", "arguments": {"mode": "soft", "target": "HEAD"}})
        == "git reset --soft HEAD"
    )
    assert (
        render_git_command({"name": "git_reset", "arguments": {"mode": "soft", "target": "HEAD~1"}})
        == "git reset --soft HEAD~1"
    )
    assert (
        render_git_command({"name": "git_reset", "arguments": {"mode": "mixed", "target": "HEAD~2"}})
        == "git reset --mixed HEAD~2"
    )
    assert (
        render_git_command({"name": "git_reset", "arguments": {"mode": "hard", "target": "abc123"}})
        == "git reset --hard abc123"
    )
    assert (
        render_git_command(
            {
                "name": "git_reset",
                "arguments": {"mode": "hard", "target": "origin/main"},
            }
        )
        == "git reset --hard origin/main"
    )
    assert render_git_command({"name": "git_reset", "arguments": {}}) == "# Error: mode is required"


def test_git_log():
    assert render_git_command({"name": "git_log", "arguments": {}}) == "git log"
    assert render_git_command({"name": "git_log", "arguments": {"ref": "main"}}) == "git log main"
    assert render_git_command({"name": "git_log", "arguments": {"ref": "origin/develop"}}) == "git log origin/develop"
    assert render_git_command({"name": "git_log", "arguments": {"limit": 10}}) == "git log -n 10"
    assert render_git_command({"name": "git_log", "arguments": {"limit": 5}}) == "git log -n 5"
    assert render_git_command({"name": "git_log", "arguments": {"oneline": True}}) == "git log --oneline"
    assert render_git_command({"name": "git_log", "arguments": {"oneline": False}}) == "git log"
    assert render_git_command({"name": "git_log", "arguments": {"graph": True}}) == "git log --graph"
    assert render_git_command({"name": "git_log", "arguments": {"graph": False}}) == "git log"
    assert (
        render_git_command(
            {
                "name": "git_log",
                "arguments": {
                    "ref": "main",
                    "limit": 10,
                    "oneline": True,
                    "graph": True,
                },
            }
        )
        == "git log main -n 10 --oneline --graph"
    )
    assert (
        render_git_command({"name": "git_log", "arguments": {"limit": 3, "oneline": True}}) == "git log -n 3 --oneline"
    )
    assert (
        render_git_command({"name": "git_log", "arguments": {"ref": "feature", "graph": True}})
        == "git log feature --graph"
    )
