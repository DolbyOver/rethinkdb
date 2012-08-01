"""This module implements a way to access RethinkDB clusters over the
network. It is used to send ReQL commands to RethinkDB in order to do
data manipulation."""

import json
import socket
import struct

import reql.query_language_pb2 as p

last_connection = None

class QueryError():
    """Foo"""
    pass

class BatchedIterator():
    """Foo"""
    def __init__():
        self.batch_size = 200 # allow the user to set this
    pass

class Connection():
    """A network connection to the RethinkDB cluster. Queries may be
    evaluated via this connection object. The connection automatically
    tries to route queries to the appropriate server node to minimize
    network hops.

    The connection may be used with Python's `with` statement for
    exception safety.
    """
    def __init__(self, host_or_list=None, port=None, db_name=None):
        """Connect to a RethinkDB cluster. The connection may be
        created by specifying the host (in which case the default port
        will be used), host and port, no arguments (in which case the
        default port on localhost will be used), or a list of values
        where each value contains the host string or a tuple of (host,
        port) pairs.

        Once the connection object reaches a single node, it retreives
        the addresses of other nodes and connects to them
        automatically. Queries are then routed to the most appropriate
        node to minimize network hops on the server.

        If all of the nodes are inaccessible, or if all of the nodes
        terminate their network connections, the connection object
        raises an error. If some of the nodes are inaccessible, or if
        some of the nodes terminate their network connections, the
        connection object does not attempt to connect to them again.

        Use :func:`rethinkdb.connect` - as shorthand for
        this method.

        Creating a connection sets :data:`last_connection` to
        itself. This is used by :func:`rethinkdb.query.Expression.run`
        as a default connection if no connection object is passed.

        :param host_or_list: A hostname, or a list of hostnames or
          (host, port) tuples.
        :type host_or_list: str or a list of values where each value
          may be an str, or an (str, int) tuple.
        :param port: The port to connect to. If not specified, the
          default port is used. If `host_or_port` argument is a list,
          `port` is ignored.
        :type port: int

        :param db_name: An optional name of a database to be used by
          default for expression that don't specify a database
          explicitly. Equivalent to calling :func:`use`.
        :type db_name: str
        """
        self.token = 1
        self.socket = socket.create_connection((host_or_list, port))

    def _get_token(self):
        token = self.token
        self.token += 1
        return token

    def _recvall(self, length):
        buf = ""
        while len(buf) != length:
            buf += self.socket.recv(length - len(buf))
        return buf

    def _run(self, protobuf, query, debug=False):
        if debug:
            print "sending:", protobuf

        serialized = protobuf.SerializeToString()

        header = struct.pack("<L", len(serialized))
        self.socket.sendall(header + serialized)
        resp_header = self._recvall(4)
        msglen = struct.unpack("<L", resp_header)[0]
        response_serialized = self._recvall(msglen)
        response = p.Response()
        response.ParseFromString(response_serialized)

        if debug:
            print "response:", response

        if response.status_code == p.Response.SUCCESS_JSON:
            return json.loads(response.response[0])
        elif response.status_code == p.Response.SUCCESS_STREAM:
            return [json.loads(s) for s in response.response]
        elif response.status_code == p.Response.SUCCESS_PARTIAL:
            new_protobuf = p.Query()
            new_protobuf.token = protobuf.token
            new_protobuf.type = p.Query.CONTINUE
            return [json.loads(s) for s in response.response] + self._run(new_protobuf, query)
        elif response.status_code == p.Response.SUCCESS_EMPTY:
            print "huh"
            return None
        elif response.status_code == p.Response.BAD_PROTOBUF:
            raise ValueError("RethinkDB server rejected our protocol buffer as "
                "malformed. RethinkDB client is buggy?")
        elif response.status_code == p.Response.BAD_QUERY:
            raise BadQueryError(response.error_message, response.backtrace.frame, query)
        elif response.status_code == p.Response.RUNTIME_ERROR:
            raise ExecutionError(response.error_message, response.backtrace.frame, query)
        else:
            raise ValueError("Got unexpected status code from server: %d" % response.status_code)


    def run(self, expr, debug=False):
        """Evaluate the expression or list of expressions `expr` on
        the server using this connection. If `expr` is a list,
        evaluates them on the server in order - this can be used to
        pack multiple expressions together to save network roundtrips.

        Use :func:`rethinkdb.query.Expression.run` - as shorthand for
        this method.

        :param expr: An expression or a list of expressions to be
          evaluated on the server.
        :type expr: :class:`rethinkdb.query.Expression`, list of
          :class:`rethinkdb.query.Expression`

        :returns: The return value depends on the expression being
          evaluated. It may be a JSON value, a
          :class:`rethinkdb.net.BatchedIterator`, or nothing. See the
          documentation for the specific expression being evaluated
          for more details. If `expr` is a list, returns a list of
          results, where each element is a result for each individual
          expression.

        :raises: :class:`rethinkdb.net.QueryError` in case of a server
          error.

        :Example:

        >>> q = table('table_name').all()
        >>> conn.run(q) # returns an iterator
        >>> q1 = table('another_table').all()
        >>> q2 = table('yet_another_table').all()
        >>> conn.run([q1, q2]) # returns a list of two iterators
        """
        protobuf = p.Query()
        protobuf.token = self._get_token()
        expr._finalize_query(protobuf)
        return self._run(protobuf, expr, debug)


    def use(self, db_name):
        """Sets the default database for this connection. All queries
        that don't explicitly specify a database will use the database
        set by this method.

        :param db_name: The name of the database to use by default.
        :type db_name: str

        :Example:

        >>> q = table('users').all()
        >>> conn.use('foo')
        >>> conn.run(q)      # select all users from database 'foo'
        >>> conn.use('bar')
        >>> conn.run(q)      # select all users from database 'bar'
        """
        pass

    def close(self):
        """Closes all network sockets on this connection object to the
        cluster."""
        pass

def connect(host_or_list=None, port=None, db_name=None):
    """
    Creates a :class:`Connection` object. This method is a shorthand
    for constructing the :class:`Connection` object directly.

    :returns: :class:`Connection` -- a connection object that can be
      used to communicate with the RethinkDB cluster.

    :Example:

    >>> conn = connect() # localhost, default port
    >>> conn = connect('electro') # host 'electro', default port
    >>> conn = connect('electro', 8080) # host 'electro', port 8080
    >>> conn = connect([('electro', 8080),
    >>>                 'magneto',
    >>>                 ('puzzler', 8181)])
    """
    return Connection(host_or_list, port, db_name)

