from rbtools.clients.perforce import PerforceClient
from rbtools.utils.console import edit_text
                        if getattr(self.options, 'parent_branch', None):
                svn_remote = execute(
                    [self.git, "config", "--get", "svn-remote.svn.url"],
                    ignore_errors=True)
                if (version_parts and svn_remote and
                                              (1, 5, 4))):
        # Okay, maybe Perforce (git-p4).
        git_p4_ref = os.path.join(git_dir, 'refs', 'remotes', 'p4', 'master')
        data = execute([self.git, 'config', '--get', 'git-p4.port'],
                       ignore_errors=True)
        m = re.search(r'(.+)', data)
        if m and os.path.exists(git_p4_ref):
            port = m.group(1)
            self.type = 'perforce'
            self.upstream_branch = 'remotes/p4/master'
            return RepositoryInfo(path=port,
                                  base_path='',
                                  supports_parent_diffs=True)
            self.upstream_branch = self.get_origin(self.upstream_branch,
                                                   True)[0]
        origin_url = execute(
            [self.git, "config", "--get", "remote.%s.url" % upstream_remote],
            ignore_errors=True).rstrip("\n")
            if prop:
                return prop
        elif self.type == 'perforce':
            prop = PerforceClient().scan_for_server(repository_info)

    def extract_summary(self, revision_range=None):
        """Extracts the summary based on the provided revision range."""
        if not revision_range or ":" not in revision_range:
            command = [self.git, "log", "--pretty=format:%s", "HEAD^!"]
        else:
            r1, r2 = revision_range.split(":")
            command = [self.git, "log", "--pretty=format:%s", "%s^!" % r2]

        return execute(command, ignore_errors=True).strip()

    def extract_description(self, revision_range=None):
        """Extracts the description based on the provided revision range."""
        if revision_range and ":" not in revision_range:
            command = [self.git, "log", "--pretty=format:%s%n%n%b",
                       revision_range + ".."]
        elif revision_range:
            r1, r2 = revision_range.split(":")
            command = [self.git, "log", "--pretty=format:%s%n%n%b",
                       "%s..%s" % (r1, r2)]
        else:
            parent_branch = self.get_parent_branch()
            head_ref = self.get_head_ref()
            merge_base = self.get_merge_base(head_ref)
            command = [self.git, "log", "--pretty=format:%s%n%n%b",
                       (parent_branch or merge_base) + ".."]

        return execute(command, ignore_errors=True).strip()

    def _set_summary(self, revision_range=None):
        """Sets the summary based on the provided revision range.

        Extracts and sets the summary if guessing is enabled and summary is not
        yet set.
        if (getattr(self.options, 'guess_summary', None) and
                not getattr(self.options, 'summary', None)):
            self.options.summary = self.extract_summary(revision_range)

    def _set_description(self, revision_range=None):
        """Sets the description based on the provided revision range.

        Extracts and sets the description if guessing is enabled and
        description is not yet set.
        if (getattr(self.options, 'guess_description', None) and
                not getattr(self.options, 'description', None)):
            self.options.description = self.extract_description(revision_range)

    def get_parent_branch(self):
        """Returns the parent branch."""
        if self.type == 'perforce':
            parent_branch = self.options.parent_branch or 'p4'
        else:
            parent_branch = self.options.parent_branch

        return parent_branch

    def get_head_ref(self):
        """Returns the HEAD reference."""

        return head_ref

    def get_merge_base(self, head_ref):
        """Returns the merge base."""
        return execute([self.git, "merge-base",
                        self.upstream_branch,
                        head_ref]).strip()

    def diff(self, args):
        """Performs a diff across all modified files in the branch.

        The diff takes into account of the parent branch.
        """
        parent_branch = self.get_parent_branch()
        head_ref = self.get_head_ref()
        self.merge_base = self.get_merge_base(head_ref)
        self._set_summary()
        self._set_description()
        return {
            'diff': diff_lines,
            'parent_diff': parent_diff_lines,
            'base_commit_id': self.merge_base,
        }
        """Performs a diff on a particular branch range."""
        elif self.type == "perforce":
            diff_lines = execute([self.git, "diff", "--no-color",
                                  "--no-prefix", "-r", "-u", rev_range],
                                 split_lines=True)
            return self.make_perforce_diff(ancestor, diff_lines)
        if not rev and self.merge_base:
            rev = execute([self.git, "svn", "find-rev",
                           self.merge_base]).strip()

    def make_perforce_diff(self, parent_branch, diff_lines):
        """Format the output of git diff to look more like perforce's."""
        diff_data = ''
        filename = ''
        p4rev = ''

        # Find which depot changelist we're based on
        log = execute([self.git, 'log', parent_branch], ignore_errors=True)

        for line in log:
            m = re.search(r'repo-paths = "(.+)": change = (\d+)\]', log, re.M)
            if m:
                base_path = m.group(1).strip()
                p4rev = m.group(2).strip()
                break

        for line in diff_lines:
            if line.startswith('diff '):
                # Grab the filename and then filter this out.
                # This will be in the format of:
                #    diff --git a/path/to/file b/path/to/file
                filename = line.split(' ')[2].strip()
            elif (line.startswith('index ') or
                  line.startswith('new file mode ')):
                # Filter this out
                pass
            elif line.startswith('--- '):
                data = execute(
                    ['p4', 'files', base_path + filename + '@' + p4rev],
                    ignore_errors=True)
                m = re.search(r'^%s%s#(\d+).*$' % (re.escape(base_path),
                                                   re.escape(filename)),
                              data, re.M)
                if m:
                    fileVersion = m.group(1).strip()
                else:
                    fileVersion = 1

                diff_data += '--- %s%s\t%s%s#%s\n' % (base_path, filename,
                                                      base_path, filename,
                                                      fileVersion)
            elif line.startswith('+++ '):
                # TODO: add a real timestamp
                diff_data += '+++ %s%s\t%s\n' % (base_path, filename,
                                                 'TIMESTAMP')
            else:
                diff_data += line

        return diff_data

        head_ref = self.get_head_ref()
        self.merge_base = self.get_merge_base(head_ref)
            diff_lines = self.make_diff(revision_range)
            diff_lines = self.make_diff(r1, r2)

        self._set_summary(revision_range)
        self._set_description(revision_range)
        return {
            'diff': diff_lines,
            'parent_diff': parent_diff_lines,
            'base_commit_id': self.merge_base,
        }
    def has_pending_changes(self):
        """Checks if there are changes waiting to be committed.

        Returns True if the working directory has been modified or if changes
        have been staged in the index, otherwise returns False.
        """
        status = execute(['git', 'status', '--porcelain'])
        return status != ''

    def create_commmit(self, message, author):
        modified_message = edit_text(message)
        execute(['git', 'add', '--all', ':/'])
        execute(['git', 'commit', '-m', modified_message,
                 '--author="%s <%s>"' % (author.fullname, author.email)])