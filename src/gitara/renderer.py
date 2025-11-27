def render_git_command(tool_call: dict) -> str:
    """
    Render a tool call as a git command.

    Args:
        tool_call: Parsed tool call dict with 'name' and 'arguments'

    Returns:
        Git command string
    """
    name = tool_call.get("name", "")
    args = tool_call.get("arguments", {})

    if not isinstance(args, dict):
        args = {}

    cmd = ["git"]
    match name:
        case "git_status":
            cmd.append("status")
            if args.get("verbose"):
                cmd.append("--verbose")
            if args.get("ignored"):
                cmd.append("--ignored")
        case "git_add":
            cmd.append("add")
            files = args.get("files", [])
            if not files:
                files = ["."]
            cmd.extend(files)
        case "git_commit":
            cmd.append("commit")
            message = args.get("message")
            amend = args.get("amend")
            if not message and not amend:
                return "# Error: message is required"
            if amend:
                cmd.append("--amend")
            if message:
                cmd.extend(["-m", f'"{message}"'])
        case "git_push":
            cmd.append("push")
            if remote := args.get("remote", "origin" if args.get("branch") else None):
                cmd.append(remote)
            if branch := args.get("branch"):
                cmd.append(branch)
            if args.get("force"):
                cmd.append("--force")
            if args.get("set_upstream"):
                cmd.append("--set-upstream")
        case "git_pull":
            cmd.append("pull")
            branch = args.get("branch")
            if remote := args.get("remote", "origin" if branch else None):
                cmd.append(remote)
            if branch:
                cmd.append(branch)
            if args.get("rebase"):
                cmd.append("--rebase")
        case "git_branch":
            cmd.append("branch")
            match args.get("action", "list"):
                case "list":
                    if args.get("all"):
                        cmd.append("--all")
                case "delete":
                    if branch_name := args.get("branch_name"):
                        d_flag = "-D" if args.get("force") else "-d"
                        cmd.extend([d_flag, branch_name])
                    else:
                        return "# Error: branch name is required"
        case "git_switch":
            cmd.append("switch")
            if args.get("create"):
                cmd.append("-c")
            elif args.get("detach"):
                cmd.append("--detach")
            if branch := args.get("branch"):
                cmd.append(branch)
        case "git_restore":
            cmd.append("restore")
            if source := args.get("source"):
                cmd.append(f"--source={source}")
            restore_target = args.get("restore_target", "worktree")
            if restore_target == "staged":
                cmd.append("--staged")
            elif restore_target == "both":
                cmd.extend(["--staged", "--worktree"])
            if files := args.get("files", []):
                cmd.extend(files)
        case "git_merge":
            cmd.append("merge")
            if branch := args.get("branch"):
                cmd.append(branch)
            if args.get("no_ff"):
                cmd.append("--no-ff")
            elif args.get("ff_only"):
                cmd.append("--ff-only")
            strategy = args.get("strategy")
            if strategy and strategy != "recursive":
                cmd.append(f"--strategy={strategy}")
        case "git_stash":
            action = args.get("action", "save")
            cmd.extend(["stash", action])
            match action:
                case "save":
                    if message := args.get("message"):
                        cmd.extend(["-m", f'"{message}"'])
                    if args.get("include_untracked"):
                        cmd.append("--include-untracked")
                case "pop" | "apply" | "drop":
                    if stash_ref := args.get("stash_ref"):
                        cmd.append(stash_ref)
                case "show":
                    if args.get("patch"):
                        cmd.append("--patch")
                    if stash_ref := args.get("stash_ref"):
                        cmd.append(stash_ref)
        case "git_rebase":
            cmd.append("rebase")
            if args.get("continue"):
                cmd.append("--continue")
            elif args.get("abort"):
                cmd.append("--abort")
            elif target := args.get("target"):
                cmd.append(target)
        case "git_reset":
            cmd.append("reset")
            if mode := args.get("mode"):
                cmd.append(f"--{mode}")
            else:
                return "# Error: mode is required"
            if target := args.get("target"):
                cmd.append(target)
        case "git_log":
            cmd.append("log")
            if ref := args.get("ref"):
                cmd.append(ref)
            if limit := args.get("limit"):
                cmd.extend(["-n", str(limit)])
            if args.get("oneline"):
                cmd.append("--oneline")
            if args.get("graph"):
                cmd.append("--graph")
        case _:
            return f"# Unknown git command: {name}"

    return " ".join(cmd)
