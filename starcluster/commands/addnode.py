#!/usr/bin/env python

from completers import ClusterCompleter


class CmdAddNode(ClusterCompleter):
    """
    addnode [options] <cluster_tag>

    Add a node to a running cluster

    Example:

        $ starcluster addnode mynewcluster

    This will add a new node to mynewcluster. To give the node an alias:

        $ starcluster addnode -a mynode mynewcluster
    """
    names = ['addnode', 'an']

    tag = None

    def addopts(self, parser):
        parser.add_option("-a", "--alias", dest="alias",
                          action="append", type="string", default=[],
                          help=("alias to give to the new node " + \
                                "(e.g. node007, mynode, etc)"))
        parser.add_option("-n", "--num-nodes", dest="num_nodes",
                          action="store", type="int", default=1,
                          help=("number of new nodes to launch"))
        parser.add_option("-x", "--no-create", dest="no_create",
                          action="store_true", default=False,
                          help="do not launch new EC2 instances when " + \
                          "adding nodes (use existing instances instead)")

    def _get_duplicate(self, lst):
        d = {}
        for item in lst:
            if item in d:
                return item
            else:
                d[item] = 0

    def execute(self, args):
        if len(args) != 1:
            self.parser.error("please specify a cluster <cluster_tag>")
        tag = self.tag = args[0]
        aliases = []
        for alias in self.opts.alias:
            aliases.extend(alias.split(','))
        if 'master' in aliases:
            self.parser.error("'master' is a reserved alias")
        num_nodes = self.opts.num_nodes
        if num_nodes == 1 and aliases:
            num_nodes = len(aliases)
        if num_nodes > 1 and aliases and len(aliases) != num_nodes:
            self.parser.error("you must specify the same number of aliases "
                              "(-a) as nodes (-n)")
        dupe = self._get_duplicate(aliases)
        if dupe:
            self.parser.error("cannot have duplicate aliases (duplicate: %s)" %
                              dupe)
        if not self.opts.alias and self.opts.no_create:
            self.parser.error("you must specify one or more node aliases via "
                              "the -a option when using -x")
        self.cm.add_nodes(tag, num_nodes, aliases=aliases,
                          no_create=self.opts.no_create)
